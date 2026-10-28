#!/usr/bin/env python3
"""Manage private team registration; callers must serialize shared registry writes.

This helper records supplied tool results only. It does not create chats, verify
model availability, or lock against concurrent processes.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

SKILL_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = SKILL_DIR.parent.parent
ASSET = SKILL_DIR / 'assets' / 'roster.json'
VERSION = 1


class StateError(Exception):
    pass


def fail(message):
    raise StateError(message)


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        fail(f'{label} must be a nonempty string')
    return value


def read_json(path):
    try:
        with path.open(encoding='utf-8') as source:
            return json.load(source)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f'Cannot read {path.name}: {exc}')


def atomic_json(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=path.parent, prefix=f'.{path.name}.',
                                         suffix='.tmp', delete=False) as out:
            temporary = Path(out.name)
            json.dump(data, out, ensure_ascii=False, indent=2)
            out.write('\n')
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def private_dir(value):
    path = Path(value).expanduser().resolve()
    # A checkout uses the project layout; an installed standalone skill is
    # bounded by its own directory rather than the user's entire skills area.
    boundaries = [SKILL_DIR]
    if ((PROJECT_DIR / '.git').exists() or (PROJECT_DIR / 'tests').is_dir()
            or (SKILL_DIR.parent.name == 'skills'
                and PROJECT_DIR.name not in {'.codex', '.agents'})):
        boundaries.append(PROJECT_DIR)
    if any(path == root or path.is_relative_to(root) for root in boundaries):
        fail('state directory must be outside the public repository and skill source tree')
    return path


def check_template(template):
    if not isinstance(template, dict) or template.get('schema_version') != VERSION:
        fail('Invalid roster schema version')
    root = nonempty(template.get('root_role'), 'root_role')
    teams = template.get('teams')
    if not isinstance(teams, list) or len(teams) != 5:
        fail('Roster must contain exactly five teams')
    seen = {root}
    for team in teams:
        if not isinstance(team, dict):
            fail('Invalid team')
        role = nonempty(team.get('id'), 'team id')
        if role in seen:
            fail(f'Duplicate role: {role}')
        seen.add(role)
        for field in ('name', 'title', 'scope'):
            nonempty(team.get(field), f'{role} {field}')
        engineers = team.get('engineers')
        if not isinstance(engineers, list) or len(engineers) != 10:
            fail(f'{role} must contain exactly ten engineers')
        for engineer in engineers:
            if not isinstance(engineer, list) or len(engineer) != 2:
                fail(f'Invalid engineer in {role}')
            child = nonempty(engineer[0], 'engineer id')
            nonempty(engineer[1], f'{child} title')
            if child in seen:
                fail(f'Duplicate role: {child}')
            seen.add(child)
    models = template.get('models')
    if not isinstance(models, dict):
        fail('Invalid model configuration')
    for kind in ('pm', 'engineer'):
        config = models.get(kind)
        if not isinstance(config, dict):
            fail(f'Invalid {kind} model configuration')
        nonempty(config.get('model'), f'{kind} model')
        nonempty(config.get('reasoning_effort'), f'{kind} effort')


def roles_for(org):
    roles = {}
    for team in org['teams']:
        roles[team['id']] = {'parent': org['root_role'], 'kind': 'pm'}
        for role, _title in team['engineers']:
            roles[role] = {'parent': team['id'], 'kind': 'engineer'}
    return roles


def initial_registry(org):
    entries = {}
    for role, info in roles_for(org).items():
        entries[role] = {
            **info, 'status': 'planned', 'registration': 'unregistered',
            'thread_id': None, 'host_id': None,
            'model': copy.deepcopy(org['models'][info['kind']]),
            'model_status': 'requested',
        }
    return {'schema_version': VERSION, 'roles': entries}


def check_state(org, registry, template, require_ready=False):
    check_template(template)
    check_template(org)
    # Template establishes role identities, descriptions, and hierarchy;
    # only model and effort values may be customized in private state.
    for field in ('schema_version', 'root_role', 'teams'):
        if org.get(field) != template.get(field):
            fail(f'Organization {field} differs from roster template')
    if set(org['models']) != {'pm', 'engineer'}:
        fail('Invalid model categories')
    for config in org['models'].values():
        if set(config) != {'model', 'reasoning_effort'}:
            fail('Invalid model fields')
    if not isinstance(registry, dict) or registry.get('schema_version') != VERSION:
        fail('Invalid registry schema version')
    entries = registry.get('roles')
    roles = roles_for(org)
    if not isinstance(entries, dict) or set(entries) != set(roles):
        fail('Registry roles do not match the organization')
    threads = set()
    counts = {'planned': 0, 'created': 0, 'ready': 0}
    expected_keys = {'parent', 'kind', 'status', 'registration', 'thread_id',
                     'host_id', 'model', 'model_status'}
    for role, info in roles.items():
        entry = entries[role]
        if not isinstance(entry, dict) or set(entry) != expected_keys:
            fail(f'Invalid registry fields for {role}')
        if entry['parent'] != info['parent'] or entry['kind'] != info['kind']:
            fail(f'Invalid reporting relationship for {role}')
        if entry['model'] != org['models'][info['kind']] or entry['model_status'] != 'requested':
            fail(f'Invalid requested model or effort for {role}')
        status = entry['status']
        if status not in counts:
            fail(f'Invalid status for {role}')
        counts[status] += 1
        if status == 'planned':
            if entry['registration'] != 'unregistered' or entry['thread_id'] is not None or entry['host_id'] is not None:
                fail(f'Inconsistent planned registration for {role}')
        else:
            if entry['registration'] != 'registered':
                fail(f'Inconsistent registration for {role}')
            thread = canonical_uuid(entry['thread_id'])
            if thread != entry['thread_id']:
                fail(f'Noncanonical thread ID for {role}')
            nonempty(entry['host_id'], f'{role} host ID')
            if thread in threads:
                fail(f'Duplicate thread ID: {thread}')
            threads.add(thread)
    if require_ready and counts['ready'] != len(roles):
        fail(f'Not all roles are ready: {counts}')
    return counts


def canonical_uuid(value):
    if not isinstance(value, str):
        fail('Thread ID must be a valid UUID')
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError):
        fail('Thread ID must be a valid UUID')


def load_state(directory):
    org = read_json(directory / 'org.json')
    registry = read_json(directory / 'registry.json')
    template = read_json(ASSET)
    check_state(org, registry, template)
    return org, registry, template


def initialize(args, directory):
    template = read_json(ASSET)
    check_template(template)
    org = copy.deepcopy(template)
    for kind, override in (('pm', args.pm_model), ('engineer', args.engineer_model)):
        if override is not None:
            org['models'][kind]['model'] = nonempty(override, f'{kind} model')
        if args.effort is not None:
            org['models'][kind]['reasoning_effort'] = nonempty(args.effort, 'effort')
    org_path, registry_path = directory / 'org.json', directory / 'registry.json'
    if org_path.exists() or registry_path.exists():
        current, registry, source = load_state(directory)
        if current != org:
            fail('Existing organization configuration is incompatible with requested init')
        check_state(current, registry, source)
        print('Existing state retained')
        return
    directory.mkdir(parents=True, exist_ok=True)
    atomic_json(org_path, org)
    atomic_json(registry_path, initial_registry(org))
    print('Initialized: 55 planned, 0 created, 0 ready')


def register(args, directory):
    org, registry, template = load_state(directory)
    entries = registry['roles']
    if args.role not in entries:
        fail(f'Unknown role: {args.role}')
    thread = canonical_uuid(args.thread_id)
    host = nonempty(args.host_id, 'host ID')
    entry = entries[args.role]
    if entry['status'] != 'planned':
        if (entry['thread_id'], entry['host_id']) != (thread, host):
            fail(f'{args.role} is already registered with different identity')
        if entry['status'] == 'ready' and args.status == 'created':
            fail(f'{args.role} cannot be downgraded from ready')
    for role, other in entries.items():
        if role != args.role and other['thread_id'] == thread:
            fail(f'Thread ID already registered to {role}')
    if entry['status'] == args.status and entry['thread_id'] == thread and entry['host_id'] == host:
        print(f'{args.role} already {args.status}; no change')
        return
    entry.update(status=args.status, registration='registered', thread_id=thread, host_id=host)
    check_state(org, registry, template)
    atomic_json(directory / 'registry.json', registry)
    print(f'{args.role} registered: {args.status}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init', help='Initialize private planned organization state')
    init.add_argument('--state-dir', required=True)
    init.add_argument('--pm-model')
    init.add_argument('--engineer-model')
    init.add_argument('--effort')
    reg = commands.add_parser('register', help='Record a supplied chat identity; serialize registry writes')
    reg.add_argument('--state-dir', required=True)
    reg.add_argument('--role', required=True)
    reg.add_argument('--thread-id', required=True)
    reg.add_argument('--host-id', required=True)
    reg.add_argument('--status', choices=('created', 'ready'), required=True)
    validate = commands.add_parser('validate', help='Validate private state and report counts')
    validate.add_argument('--state-dir', required=True)
    validate.add_argument('--require-ready', action='store_true')
    args = parser.parse_args(argv)
    try:
        directory = private_dir(args.state_dir)
        if args.command == 'init':
            initialize(args, directory)
        elif args.command == 'register':
            register(args, directory)
        else:
            org, registry, template = load_state(directory)
            counts = check_state(org, registry, template, args.require_ready)
            print(f"Valid: {counts['planned']} planned, {counts['created']} created, {counts['ready']} ready")
        return 0
    except (StateError, OSError, ValueError, TypeError, KeyError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
