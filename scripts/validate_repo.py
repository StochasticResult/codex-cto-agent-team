#!/usr/bin/env python3
"""Validate repository metadata, Python syntax, links, skill packaging, and changelog entries.

Requires Python 3.11+ and only the Python standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import py_compile
import re
import subprocess
import sys
import tempfile
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / 'skills' / 'cto-agent-team'
ALLOWED_FRONTMATTER_KEYS = {'name', 'description', 'license', 'allowed-tools', 'metadata'}
PRIVATE_STATE_FILENAMES = {'org.json', 'registry.json', 'lease.json'}
MARKDOWN_LINK_RE = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')
HEADING_RE = re.compile(r'^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$')
ANCHOR_TAG_RE = re.compile(r'<a\s+(?:id|name)=["\']([^"\']+)["\']', re.IGNORECASE)


def fail(message: str) -> None:
    raise ValueError(message)


def parse_simple_frontmatter(text: str) -> tuple[dict[str, str], str]:
    normalized = text.replace('\r\n', '\n')
    if not normalized.startswith('---\n'):
        fail('SKILL.md is missing leading YAML frontmatter')
    end = normalized.find('\n---\n', 4)
    if end == -1:
        fail('SKILL.md frontmatter is not properly closed')
    raw_meta = normalized[4:end]
    body = normalized[end + 5:]
    parsed: dict[str, str] = {}
    for line in raw_meta.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if ':' not in stripped:
            fail(f'Unsupported frontmatter line: {line}')
        key, val = stripped.split(':', 1)
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in {'"', "'"}:
            val = val[1:-1]
        parsed[key] = val
    return parsed, body


def validate_skill_metadata() -> None:
    skill_md = SKILL_DIR / 'SKILL.md'
    if not skill_md.is_file():
        fail(f'Missing {skill_md}')
    frontmatter, body = parse_simple_frontmatter(skill_md.read_text(encoding='utf-8'))
    unexpected = set(frontmatter) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        fail(f'Unexpected keys in SKILL.md frontmatter: {sorted(unexpected)}')
    name = frontmatter.get('name', '').strip()
    if name != 'cto-agent-team':
        fail(f'Expected skill name cto-agent-team, got {name!r}')
    description = frontmatter.get('description', '').strip()
    if not description or description.startswith('[TODO:'):
        fail('SKILL.md description is missing or contains TODO')
    if '<' in description or '>' in description:
        fail('SKILL.md description cannot contain angle brackets')
    if len(description) > 1024:
        fail('SKILL.md description exceeds 1024 characters')
    if frontmatter.get('license') != 'MIT':
        fail(f'Expected SKILL.md license MIT, got {frontmatter.get("license")!r}')
    if re.search(r'(?m)^[ ]{0,3}\[TODO:[^\n]*\][ \t]*$', body):
        fail('SKILL.md body contains unfinished TODO placeholder')

    openai_yaml = SKILL_DIR / 'agents' / 'openai.yaml'
    if not openai_yaml.is_file():
        fail(f'Missing {openai_yaml}')
    yaml_text = openai_yaml.read_text(encoding='utf-8')
    for required_key in ('display_name:', 'short_description:', 'default_prompt:'):
        if required_key not in yaml_text:
            fail(f'{openai_yaml} missing {required_key}')
    if '$cto-agent-team' not in yaml_text:
        fail(f'{openai_yaml} default_prompt must mention $cto-agent-team')


def load_json_no_duplicates(path: Path) -> object:
    def reject_dupes(pairs: list[tuple[str, object]]) -> dict[str, object]:
        obj: dict[str, object] = {}
        for k, v in pairs:
            if k in obj:
                fail(f'Duplicate JSON key {k!r} in {path}')
            obj[k] = v
        return obj

    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=reject_dupes)


def validate_assets_and_json() -> None:
    json_files = list((SKILL_DIR / 'assets').rglob('*.json')) + list((REPO_ROOT / 'examples').rglob('*.json'))
    for json_path in sorted(json_files):
        load_json_no_duplicates(json_path)

    spec = importlib.util.spec_from_file_location('team_state_mod', SKILL_DIR / 'scripts' / 'team_state.py')
    if spec is None or spec.loader is None:
        fail('Cannot import team_state.py')
        return
    team_state = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(team_state)
    roster = load_json_no_duplicates(SKILL_DIR / 'assets' / 'roster.json')
    team_state.check_template(roster)

    res = subprocess.run(
        [
            sys.executable, '-B',
            str(SKILL_DIR / 'scripts' / 'model_route.py'),
            str(SKILL_DIR / 'assets' / 'routing.example.json'),
            '--now', '2030-01-02T00:00:00Z',
        ],
        capture_output=True,
        text=True,
        encoding='utf-8',
        check=False,
    )
    if res.returncode != 0:
        fail(f'routing.example.json fixture failed: {res.stderr or res.stdout}')
    payload = json.loads(res.stdout)
    if payload.get('state') != 'selected' or payload.get('dispatch_ready') is not False:
        fail(f'Unexpected model_route fixture result: {payload}')


def validate_python_compile() -> None:
    for folder in ('skills', 'scripts', 'examples', 'tests'):
        base = REPO_ROOT / folder
        if not base.exists():
            continue
        for py_file in sorted(base.rglob('*.py')):
            if '__pycache__' in py_file.parts:
                continue
            py_compile.compile(str(py_file), doraise=True)


def github_heading_slugs(md_path: Path) -> set[str]:
    text = md_path.read_text(encoding='utf-8')
    slugs: set[str] = set(ANCHOR_TAG_RE.findall(text))
    counts: dict[str, int] = {}
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if not match:
            continue
        raw_title = re.sub(r'`([^`]*)`', r'\1', match.group(1))
        raw_title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', raw_title).strip().lower()
        # Keep Unicode word characters, spaces, and hyphens as GitHub anchors do.
        cleaned = ''.join(ch for ch in raw_title if ch.isalnum() or ch in {' ', '-', '_'})
        base_slug = cleaned.replace(' ', '-')
        if not base_slug:
            continue
        idx = counts.get(base_slug, 0)
        counts[base_slug] = idx + 1
        slug = base_slug if idx == 0 else f'{base_slug}-{idx}'
        slugs.add(slug)
    return slugs


def validate_markdown_links() -> None:
    md_files = [
        p for p in REPO_ROOT.rglob('*.md')
        if '.git' not in p.parts and 'dist' not in p.parts
    ]
    slug_cache: dict[Path, set[str]] = {}
    for md_path in sorted(md_files):
        text = md_path.read_text(encoding='utf-8')
        in_fence = False
        for line_no, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith('```') or stripped.startswith('~~~'):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            scrubbed = re.sub(r'`[^`]+`', '', line)
            for raw_target in MARKDOWN_LINK_RE.findall(scrubbed):
                target = raw_target.strip()
                if target.startswith(('http://', 'https://', 'mailto:')):
                    continue
                if target.startswith('#'):
                    rel_part, anchor = '', target[1:]
                elif '#' in target:
                    rel_part, anchor = target.split('#', 1)
                else:
                    rel_part, anchor = target, ''
                dest = md_path if not rel_part else (md_path.parent / rel_part).resolve()
                if not dest.exists():
                    fail(f'Broken link in {md_path.relative_to(REPO_ROOT)}:{line_no} -> {raw_target}')
                if anchor and dest.is_file() and dest.suffix.lower() == '.md':
                    if dest not in slug_cache:
                        slug_cache[dest] = github_heading_slugs(dest)
                    if anchor.lower() not in {s.lower() for s in slug_cache[dest]}:
                        fail(f'Broken anchor #{anchor} in {md_path.relative_to(REPO_ROOT)}:{line_no} -> {dest.name}')


def validate_no_private_state_files() -> None:
    for path in REPO_ROOT.rglob('*'):
        if '.git' in path.parts or 'dist' in path.parts:
            continue
        if path.is_file() and path.name in PRIVATE_STATE_FILENAMES:
            fail(f'Private runtime file committed inside repo: {path.relative_to(REPO_ROOT)}')


def iter_package_files() -> list[Path]:
    files = []
    for path in sorted(SKILL_DIR.rglob('*')):
        if not path.is_file():
            continue
        if '__pycache__' in path.parts or path.suffix in {'.pyc', '.pyo'}:
            continue
        files.append(path)
    return files


def build_dist_archive(out_dir: Path, version_tag: str) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_name = f'cto-agent-team-{version_tag}.zip'
    archive_path = out_dir / archive_name
    with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in iter_package_files():
            arcname = f'cto-agent-team/{file_path.relative_to(SKILL_DIR).as_posix()}'
            info = zipfile.ZipInfo(arcname, date_time=(2026, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            zf.writestr(info, file_path.read_bytes())
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_path = out_dir / 'SHA256SUMS.txt'
    checksum_path.write_text(f'{digest}  {archive_name}\n', encoding='utf-8')
    return archive_path, checksum_path


def verify_standalone_package(out_dir: Path | None = None, version_tag: str = 'dev') -> None:
    with tempfile.TemporaryDirectory(prefix='cto-pkg-verify-') as tmp_name:
        tmp = Path(tmp_name)
        pkg_out = out_dir if out_dir is not None else (tmp / 'dist')
        archive_path, _checksum_path = build_dist_archive(pkg_out, version_tag)
        extract_dir = tmp / 'installed'
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(extract_dir)
        installed_skill = extract_dir / 'cto-agent-team'
        private_state = tmp / 'private-state'
        lock_dir = private_state / 'locks'

        checks = [
            [sys.executable, '-B', str(installed_skill / 'scripts' / 'team_state.py'),
             'init', '--state-dir', str(private_state)],
            [sys.executable, '-B', str(installed_skill / 'scripts' / 'team_state.py'),
             'validate', '--state-dir', str(private_state)],
            [sys.executable, '-B', str(installed_skill / 'scripts' / 'model_route.py'),
             str(installed_skill / 'assets' / 'routing.example.json'), '--now', '2030-01-02T00:00:00Z'],
            [sys.executable, '-B', str(installed_skill / 'scripts' / 'agent_guard.py'),
             '--lock-dir', str(lock_dir), 'locks'],
        ]
        for cmd in checks:
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=False)
            if proc.returncode != 0:
                fail(f'Standalone extracted package check failed: {" ".join(cmd)}\n{proc.stderr or proc.stdout}')


def validate_changelog_version(version: str) -> None:
    clean = version.lstrip('v')
    changelog = REPO_ROOT / 'CHANGELOG.md'
    if not changelog.is_file():
        fail('Missing CHANGELOG.md')
    text = changelog.read_text(encoding='utf-8')
    pattern = re.compile(rf'(?m)^## \[{re.escape(clean)}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$')
    match = pattern.search(text)
    if match is None:
        fail(f'CHANGELOG.md does not contain heading "## [{clean}]"')
        return
    rest = text[match.end():]
    next_section = re.search(r'(?m)^## \[', rest)
    section_body = (rest[:next_section.start()] if next_section else rest).strip()
    if not section_body:
        fail(f'CHANGELOG.md section for {clean} is empty')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-package', action='store_true',
                        help='Build and test an extracted standalone cto-agent-team skill archive')
    parser.add_argument('--build-dist', default='', help='Write release zip and SHA256SUMS.txt to directory')
    parser.add_argument('--version', default='dev', help='Version tag used for dist archive naming')
    parser.add_argument('--check-changelog', default='', help='Verify CHANGELOG.md contains section for version')
    args = parser.parse_args(argv)

    validate_skill_metadata()
    validate_assets_and_json()
    validate_python_compile()
    validate_markdown_links()
    validate_no_private_state_files()

    if args.check_changelog:
        validate_changelog_version(args.check_changelog)
    if args.verify_package:
        out = Path(args.build_dist).resolve() if args.build_dist else None
        verify_standalone_package(out_dir=out, version_tag=args.version)
    elif args.build_dist:
        build_dist_archive(Path(args.build_dist).resolve(), args.version)

    print('Repository validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
