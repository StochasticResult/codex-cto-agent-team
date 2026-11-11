#!/usr/bin/env python3
"""Manage private advisory resource leases and bounded process-tree execution.

Requires Python 3.11 or later and only the standard library. Lease state must
live in a private directory outside the public repository and installed skill.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time

SKILL_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = SKILL_DIR.parent.parent


class GuardError(Exception):
    pass


def utc_iso(ts: float | None = None) -> str:
    stamp = ts if ts is not None else time.time()
    return datetime.fromtimestamp(stamp, tz=timezone.utc).isoformat(timespec='seconds')


def private_lock_dir(value: str | None) -> Path:
    if not value or not value.strip():
        raise GuardError('--lock-dir is required for lease operations and must point to a private directory')
    path = Path(value).expanduser().resolve()
    boundaries = [SKILL_DIR]
    if ((PROJECT_DIR / '.git').exists() or (PROJECT_DIR / 'tests').is_dir()
            or (SKILL_DIR.parent.name == 'skills'
                and PROJECT_DIR.name not in {'.codex', '.agents'})):
        boundaries.append(PROJECT_DIR)
    if any(path == root or path.is_relative_to(root) for root in boundaries):
        raise GuardError('lock directory must be outside the public repository and skill source tree')
    return path


def resource_key(resource: str) -> str:
    candidate = Path(resource)
    try:
        normalized = str(candidate.resolve()).lower()
    except OSError:
        normalized = resource.strip().lower()
    digest = hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]
    leaf = ''.join(ch if ch.isalnum() or ch in ('-', '_', '.') else '_'
                   for ch in Path(normalized).name)[:48] or 'resource'
    return f'{leaf}_{digest}'


def read_lease(slot: Path) -> dict | None:
    lease_file = slot / 'lease.json'
    if not lease_file.exists():
        return None
    try:
        data = json.loads(lease_file.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else None
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def lease_expired(lease: dict | None) -> bool:
    if not lease:
        return True
    try:
        return time.time() >= float(lease.get('expires_ts', 0))
    except (TypeError, ValueError):
        return True


def write_lease(slot: Path, data: dict) -> None:
    tmp = slot / f'.lease.{os.getpid()}.tmp'
    try:
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(tmp, slot / 'lease.json')
    finally:
        tmp.unlink(missing_ok=True)


def cmd_acquire(args: argparse.Namespace) -> int:
    if args.ttl <= 0:
        raise GuardError('--ttl must be greater than 0')
    if not args.owner.strip() or not args.task.strip():
        raise GuardError('--owner and --task must be nonempty strings')
    lock_root = private_lock_dir(args.lock_dir)
    lock_root.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    created_slots: list[Path] = []

    for resource in args.resources:
        key = resource_key(resource)
        slot = lock_root / key
        now = time.time()
        payload = {
            'resource': resource,
            'normalized_key': key,
            'owner': args.owner,
            'task': args.task,
            'host': socket.gethostname(),
            'pid': os.getpid(),
            'acquired_ts': now,
            'acquired_at': utc_iso(now),
            'ttl_sec': args.ttl,
            'expires_ts': now + args.ttl,
            'expires_at': utc_iso(now + args.ttl),
        }
        for attempt in range(2):
            try:
                os.mkdir(slot)
                write_lease(slot, payload)
                created_slots.append(slot)
                results.append({'status': 'acquired', 'lease': payload})
                break
            except FileExistsError:
                existing = read_lease(slot)
                if (existing and existing.get('owner') == args.owner
                        and existing.get('task') == args.task
                        and not lease_expired(existing)):
                    write_lease(slot, payload)
                    results.append({'status': 'renewed', 'lease': payload})
                    break
                if lease_expired(existing):
                    shutil.rmtree(slot, ignore_errors=True)
                    if attempt == 0:
                        continue
                for created in created_slots:
                    shutil.rmtree(created, ignore_errors=True)
                conflict = {
                    'ok': False,
                    'error': 'RESOURCE_LOCKED',
                    'resource': resource,
                    'held_by': existing or {'owner': 'unknown', 'reason': 'lock directory exists'},
                    'advice': 'Do not overwrite or wait blindly. Coordinate with the holder or select a disjoint resource.',
                }
                print(json.dumps(conflict, ensure_ascii=False, indent=2))
                return 2

    print(json.dumps({'ok': True, 'locks': results}, ensure_ascii=False, indent=2))
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    lock_root = private_lock_dir(args.lock_dir)
    released: list[dict] = []
    skipped: list[dict] = []
    for resource in args.resources:
        slot = lock_root / resource_key(resource)
        if not slot.exists():
            released.append({'resource': resource, 'status': 'already_free'})
            continue
        existing = read_lease(slot)
        if (not args.force and existing and args.owner
                and existing.get('owner') != args.owner):
            skipped.append({'resource': resource, 'status': 'owned_by_other', 'held_by': existing})
            continue
        shutil.rmtree(slot, ignore_errors=True)
        released.append({'resource': resource, 'status': 'released'})

    ok = len(skipped) == 0
    print(json.dumps({'ok': ok, 'released': released, 'skipped': skipped}, ensure_ascii=False, indent=2))
    return 0 if ok else 2


def cmd_locks(args: argparse.Namespace) -> int:
    lock_root = private_lock_dir(args.lock_dir)
    if not lock_root.exists():
        print(json.dumps({'ok': True, 'active_count': 0, 'active': [], 'pruned': []}, ensure_ascii=False, indent=2))
        return 0
    active: list[dict] = []
    pruned: list[str] = []
    for slot in sorted(lock_root.iterdir()):
        if not slot.is_dir():
            continue
        lease = read_lease(slot)
        expired = lease_expired(lease)
        if expired and args.prune:
            shutil.rmtree(slot, ignore_errors=True)
            pruned.append(slot.name)
        else:
            active.append({'slot': slot.name, 'expired': expired, 'lease': lease})
    print(json.dumps({'ok': True, 'active_count': len(active), 'active': active, 'pruned': pruned},
                     ensure_ascii=False, indent=2))
    return 0


def terminate_process_tree(proc: subprocess.Popen) -> None:
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(proc.pid)],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except OSError:
            try:
                proc.kill()
            except OSError:
                pass


def run_watched(cmd: list[str], *, timeout_sec: float, idle_timeout_sec: float,
                cwd: str | None = None) -> int:
    start_ts = time.monotonic()
    events: queue.Queue[tuple[str, str]] = queue.Queue()
    popen_kwargs: dict = {
        'cwd': cwd,
        'stdin': subprocess.DEVNULL,
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'text': True,
        'encoding': 'utf-8',
        'errors': 'replace',
        'bufsize': 1,
    }
    if sys.platform != 'win32':
        popen_kwargs['start_new_session'] = True

    proc = subprocess.Popen(cmd, **popen_kwargs)

    def drain(stream, tag: str) -> None:
        try:
            for line in iter(stream.readline, ''):
                events.put((tag, line))
        except (OSError, ValueError):
            pass
        finally:
            try:
                stream.close()
            except OSError:
                pass

    out_thread = threading.Thread(target=drain, args=(proc.stdout, 'OUT'), daemon=True)
    err_thread = threading.Thread(target=drain, args=(proc.stderr, 'ERR'), daemon=True)
    out_thread.start()
    err_thread.start()

    last_output = start_ts
    timeout_reason: str | None = None

    while True:
        try:
            tag, line = events.get(timeout=0.1)
            last_output = time.monotonic()
            target = sys.stdout if tag == 'OUT' else sys.stderr
            target.write(line)
            target.flush()
        except queue.Empty:
            pass

        now = time.monotonic()
        if proc.poll() is not None and events.empty():
            break
        if timeout_sec > 0 and (now - start_ts) >= timeout_sec:
            timeout_reason = f'Hard wall-clock timeout ({timeout_sec}s) exceeded'
            break
        if idle_timeout_sec > 0 and (now - last_output) >= idle_timeout_sec:
            timeout_reason = f'Idle output watchdog timeout ({idle_timeout_sec}s without output) exceeded'
            break

    if timeout_reason:
        terminate_process_tree(proc)
        deadline = time.monotonic() + 0.25
        while time.monotonic() < deadline:
            try:
                tag, line = events.get_nowait()
                (sys.stdout if tag == 'OUT' else sys.stderr).write(line)
            except queue.Empty:
                break
        sys.stderr.write(f'\n[AGENT_GUARD_TIMEOUT] {timeout_reason}. Process tree (PID {proc.pid}) terminated.\n')
        sys.stderr.flush()
        return 124

    out_thread.join(timeout=0.5)
    err_thread.join(timeout=0.5)
    return int(proc.returncode or 0)


def cmd_run(args: argparse.Namespace) -> int:
    cmd = list(args.command or [])
    if cmd and cmd[0] == '--':
        cmd = cmd[1:]
    if not cmd:
        raise GuardError('Missing command to execute')
    if args.shell:
        joined = ' '.join(cmd)
        if sys.platform == 'win32':
            full_cmd = ['powershell.exe', '-NoProfile', '-NonInteractive', '-InputFormat', 'None', '-Command', joined]
        else:
            full_cmd = ['sh', '-c', joined]
    else:
        full_cmd = cmd
    return run_watched(full_cmd, timeout_sec=args.timeout, idle_timeout_sec=args.idle_timeout, cwd=args.cwd)


def cmd_ssh(args: argparse.Namespace) -> int:
    ssh_bin = (r'C:\Windows\System32\OpenSSH\ssh.exe'
               if sys.platform == 'win32' and Path(r'C:\Windows\System32\OpenSSH\ssh.exe').exists()
               else 'ssh')
    remote = ' '.join(args.remote_cmd).strip()
    if not remote:
        raise GuardError('Missing remote command')
    if args.ps:
        encoded = base64.b64encode(remote.encode('utf-16le')).decode('ascii')
        remote = f'powershell -NoProfile -NonInteractive -InputFormat None -EncodedCommand {encoded}'
    full_cmd = [
        ssh_bin, '-q', '-n',
        '-o', 'BatchMode=yes',
        '-o', f'ConnectTimeout={args.connect_timeout}',
        '-o', 'ServerAliveInterval=5',
        '-o', 'ServerAliveCountMax=2',
        args.host, remote,
    ]
    return run_watched(full_cmd, timeout_sec=args.timeout, idle_timeout_sec=args.idle_timeout)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Advisory resource lease locking and bounded process watchdog')
    parser.add_argument('--lock-dir', default=os.environ.get('CTO_TEAM_LOCK_DIR', ''),
                        help='Private directory for advisory resource leases (outside the repository and skill)')
    sub = parser.add_subparsers(dest='subcommand', required=True)

    p_acq = sub.add_parser('acquire', help='Acquire advisory lease on one or more shared resources')
    p_acq.add_argument('--owner', required=True, help='Role or worker identifier')
    p_acq.add_argument('--task', required=True, help='Canonical task ID')
    p_acq.add_argument('--ttl', type=int, default=600, help='Lease TTL in seconds (default: 600)')
    p_acq.add_argument('resources', nargs='+', help='File paths or logical resource names')
    p_acq.set_defaults(func=cmd_acquire)

    p_rel = sub.add_parser('release', help='Release advisory lease on shared resources')
    p_rel.add_argument('--owner', default='', help='Expected lease owner')
    p_rel.add_argument('--force', action='store_true', help='Release regardless of current owner')
    p_rel.add_argument('resources', nargs='+', help='File paths or logical resource names')
    p_rel.set_defaults(func=cmd_release)

    p_locks = sub.add_parser('locks', help='List active and expired resource leases')
    p_locks.add_argument('--prune', action='store_true', help='Remove expired lease directories')
    p_locks.set_defaults(func=cmd_locks)

    p_run = sub.add_parser('run', help='Run a local command with stdin closed and process-tree timeouts')
    p_run.add_argument('--timeout', type=float, default=30.0, help='Wall-clock timeout in seconds')
    p_run.add_argument('--idle-timeout', type=float, default=15.0, help='Idle output timeout in seconds')
    p_run.add_argument('--cwd', default=None, help='Working directory')
    p_run.add_argument('--shell', action='store_true', help='Execute command string through non-interactive shell')
    p_run.add_argument('command', nargs=argparse.REMAINDER, help='Command and arguments')
    p_run.set_defaults(func=cmd_run)

    p_ssh = sub.add_parser('ssh', help='Run a non-interactive SSH command with stdin closed and timeouts')
    p_ssh.add_argument('host', help='Target SSH host')
    p_ssh.add_argument('--ps', action='store_true', help='Encode remote command for Windows PowerShell')
    p_ssh.add_argument('--connect-timeout', type=int, default=5, help='SSH connect timeout in seconds')
    p_ssh.add_argument('--timeout', type=float, default=20.0, help='Wall-clock timeout in seconds')
    p_ssh.add_argument('--idle-timeout', type=float, default=10.0, help='Idle output timeout in seconds')
    p_ssh.add_argument('remote_cmd', nargs='+', help='Remote command')
    p_ssh.set_defaults(func=cmd_ssh)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except GuardError as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
