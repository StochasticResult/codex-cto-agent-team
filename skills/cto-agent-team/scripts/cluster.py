#!/usr/bin/env python3
"""Shared task board for the Claude / Codex / Antigravity cluster.

One private folder is the only channel between the agents. Every command names the
calling agent with --agent. Python 3.11+, standard library only.

The board folder is $CLUSTER_DIR, or the folder of this script when a policy.json is
next to it. Keep the board outside public repositories and installed skill folders.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

_HERE = Path(__file__).resolve().parent
_HAS_BOARD = bool(os.environ.get('CLUSTER_DIR')) or (_HERE / 'policy.json').is_file()
ROOT = Path(os.environ.get('CLUSTER_DIR') or _HERE)
TASKS, STATUS, CAPACITY, INBOX = (ROOT / n for n in ('tasks', 'status', 'capacity', 'inbox'))
OPEN_STATES = ('open', 'assigned', 'in_progress', 'review', 'rework', 'blocked')
DEFAULT_POLICY: dict[str, Any] = {
    'cto': 'claude',
    'agents': ['claude', 'codex', 'antigravity'],
    'min_remaining_pct': 15,
    'capacity_stale_hours': 24,
    'task_stale_hours': 6,
    'tiers': ['heavy', 'standard', 'light'],
    'default_order': ['codex', 'antigravity', 'claude'],
    'type_preferences': {},
    'unmetered': [],
}


class ClusterError(Exception):
    pass


def now() -> datetime:
    return datetime.now().astimezone()


def stamp() -> str:
    return now().isoformat(timespec='seconds')


def age_hours(iso: str | None) -> float:
    if not iso:
        return float('inf')
    return (now() - datetime.fromisoformat(iso)).total_seconds() / 3600


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f'.{path.name}.{uuid.uuid4().hex[:8]}.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


@contextlib.contextmanager
def board_lock(timeout: float = 15.0) -> Iterator[None]:
    """Cross-process mutex: mkdir is atomic on every platform we use."""
    lock = ROOT / '.lock'
    deadline = time.monotonic() + timeout
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError:
            with contextlib.suppress(OSError):
                if time.time() - lock.stat().st_mtime > 60:
                    lock.rmdir()
                    continue
            if time.monotonic() > deadline:
                raise ClusterError('board is locked by another process; retry in a moment') from None
            time.sleep(0.2)
    try:
        yield
    finally:
        with contextlib.suppress(OSError):
            lock.rmdir()


def policy() -> dict[str, Any]:
    return {**DEFAULT_POLICY, **(read_json(ROOT / 'policy.json', {}) or {})}


def check_agent(name: str) -> str:
    if name not in policy()['agents']:
        raise ClusterError(f'unknown agent {name!r}; expected one of {policy()["agents"]}')
    return name


def require_cto(agent: str) -> None:
    if agent != policy()['cto']:
        raise ClusterError(f'only the cluster CTO ({policy()["cto"]}) can do this; send it a message instead')


def all_tasks() -> list[dict[str, Any]]:
    return [read_json(p) for p in sorted(TASKS.glob('TASK-*.json'))]


def load_task(task_id: str) -> dict[str, Any]:
    task = read_json(TASKS / f'{task_id}.json')
    if task is None:
        raise ClusterError(f'no such task: {task_id}')
    return task


def save_task(task: dict[str, Any], by: str, action: str, note: str = '') -> None:
    task['updated_at'] = stamp()
    task.setdefault('history', []).append({'at': task['updated_at'], 'by': by, 'action': action, 'note': note})
    write_json(TASKS / f'{task["id"]}.json', task)


def capacity_of(agent: str) -> dict[str, Any]:
    return read_json(CAPACITY / f'{agent}.json', {}) or {}


def available(agent: str, pol: dict[str, Any]) -> tuple[bool, str]:
    cap = capacity_of(agent)
    state = cap.get('state', 'unknown')
    remaining = cap.get('remaining_pct')
    if state == 'exhausted':
        return False, 'exhausted'
    if state == 'paused':
        return False, 'paused by user'
    if agent in pol['unmetered']:
        # The user said this agent's quota is not a constraint; only a reported limit stops it.
        return True, 'unmetered'
    if remaining is not None and remaining < pol['min_remaining_pct']:
        return False, f'only {remaining}% left'
    if age_hours(cap.get('reported_at')) > pol['capacity_stale_hours']:
        return True, 'capacity unknown or stale'
    return True, f'{remaining}% left' if remaining is not None else 'ok'


def route(task_type: str, tier: str) -> tuple[str | None, list[str]]:
    """Pick an agent: preference order for the task type, skipping agents without capacity."""
    pol = policy()
    order = pol['type_preferences'].get(task_type) or pol['default_order']
    load = {a: 0 for a in pol['agents']}
    for task in all_tasks():
        if task['status'] in ('assigned', 'in_progress', 'rework') and task.get('assignee') in load:
            load[task['assignee']] += 1
    reasons: list[str] = []
    fresh: list[str] = []
    stale: list[str] = []
    for agent in order:
        ok, why = available(agent, pol)
        tier_cfg = (capacity_of(agent).get('tiers') or {}).get(tier)
        reasons.append(f'{agent}: {"ok" if ok else "skip"} ({why}; open tasks {load[agent]}'
                       f'{"" if tier_cfg else f"; no {tier} tier reported"})')
        if ok:
            (stale if 'stale' in why else fresh).append(agent)
    for pool in (fresh, stale):
        if pool:
            best = min(pool, key=lambda a: (load[a] >= 3, order.index(a)))
            return best, reasons
    return None, reasons


def cmd_task_new(a: argparse.Namespace) -> None:
    pol = policy()
    if a.tier not in pol['tiers']:
        raise ClusterError(f'tier must be one of {pol["tiers"]}')
    with board_lock():
        prefix = f'TASK-{now():%Y%m%d}-'
        seq = max([int(p.stem.rsplit('-', 1)[1]) for p in TASKS.glob(f'{prefix}*.json')] or [0]) + 1
        assignee: str | None
        if a.agent != pol['cto']:
            # A member can propose work for the CTO to assign, or record work it takes itself.
            if a.assign not in ('auto', a.agent):
                require_cto(a.agent)
            assignee = a.agent if a.assign == a.agent else None
            reasons = ['self-assigned' if assignee else 'proposed by a member; waiting for the CTO to assign']
        elif a.assign == 'auto':
            assignee, reasons = route(a.type, a.tier)
        else:
            assignee, reasons = check_agent(a.assign), [f'assigned by {a.agent}']
        tier_cfg = (capacity_of(assignee).get('tiers') or {}).get(a.tier, {}) if assignee else {}
        task = {
            'id': f'{prefix}{seq:02d}', 'title': a.title, 'goal': a.goal, 'acceptance': a.accept or [],
            'type': a.type, 'tier': a.tier, 'project': a.project, 'paths': a.paths or [],
            'created_by': a.agent, 'assignee': assignee, 'status': 'assigned' if assignee else 'open',
            'model': a.model or tier_cfg.get('model'), 'effort': a.effort or tier_cfg.get('effort'),
            'routing': reasons, 'created_at': stamp(), 'result': None, 'evidence': None,
        }
        overlap = [f'{t["id"]} ({t.get("assignee")}): {sorted(set(t.get("paths", [])) & set(task["paths"]))}'
                   for t in all_tasks() if t['status'] in OPEN_STATES and set(t.get('paths', [])) & set(task['paths'])]
        save_task(task, a.agent, 'created', f'assignee={assignee}')
    print(f'{task["id"]} -> {assignee or "UNASSIGNED (no agent has capacity)"}'
          f'  model={task["model"]} effort={task["effort"]}')
    for line in reasons:
        print(f'  {line}')
    for line in overlap:
        print(f'  WARNING write-set overlap with {line}')


def transition(a: argparse.Namespace, allowed_from: tuple[str, ...], new_status: str, action: str,
               *, cto_only: bool = False, assignee_only: bool = False) -> dict[str, Any]:
    with board_lock():
        task = load_task(a.id)
        if cto_only:
            require_cto(a.agent)
        if assignee_only and task.get('assignee') != a.agent:
            raise ClusterError(f'{a.id} is assigned to {task.get("assignee")}, not {a.agent}')
        if task['status'] not in allowed_from:
            raise ClusterError(f'{a.id} is {task["status"]}; {action} needs one of {allowed_from}')
        task['status'] = new_status
        for field in ('result', 'evidence'):
            if getattr(a, field, None):
                task[field] = getattr(a, field)
        if getattr(a, 'to', None):
            task['assignee'] = check_agent(a.to)
            tier_cfg = (capacity_of(a.to).get('tiers') or {}).get(task['tier'], {})
            task['model'], task['effort'] = tier_cfg.get('model'), tier_cfg.get('effort')
        save_task(task, a.agent, action, getattr(a, 'note', '') or '')
    print(f'{task["id"]}: {action} -> {task["status"]} (assignee {task.get("assignee")})')
    return task


def cmd_task_note(a: argparse.Namespace) -> None:
    with board_lock():
        task = load_task(a.id)
        save_task(task, a.agent, 'note', a.note)
    print(f'{a.id}: note added')


def fmt_task(task: dict[str, Any]) -> str:
    return (f'{task["id"]}  [{task["status"]:<11}] {task.get("assignee") or "-":<11} '
            f'{task["type"]}/{task["tier"]}  {task["title"]}')


def cmd_task_list(a: argparse.Namespace) -> None:
    rows = [t for t in all_tasks()
            if (a.all or t['status'] in OPEN_STATES) and (not a.assignee or t.get('assignee') == a.assignee)]
    print('\n'.join(fmt_task(t) for t in rows) or 'no tasks')


def cmd_task_show(a: argparse.Namespace) -> None:
    print(json.dumps(load_task(a.id), ensure_ascii=False, indent=2))


def cmd_status_set(a: argparse.Namespace) -> None:
    write_json(STATUS / f'{a.agent}.json', {
        'agent': a.agent, 'doing': a.doing, 'task': a.task, 'files': a.files or [],
        'next': a.next, 'blocked_on': a.blocked_on, 'updated_at': stamp()})
    print(f'status of {a.agent} updated')


def cmd_capacity_set(a: argparse.Namespace) -> None:
    cap = capacity_of(a.agent)
    if a.remaining is not None:
        cap['remaining_pct'] = a.remaining
    if a.state:
        cap['state'] = a.state
    if a.resets_at:
        cap['resets_at'] = a.resets_at
    if a.note:
        cap['note'] = a.note
    tiers = cap.setdefault('tiers', {})
    for spec in a.tier or []:
        name, _, rest = spec.partition('=')
        model, _, effort = rest.partition(':')
        if name not in policy()['tiers'] or not model:
            raise ClusterError(f'bad --tier {spec!r}; use e.g. heavy=MODEL:EFFORT')
        tiers[name] = {'model': model, 'effort': effort or None}
    cap.update(agent=a.agent, reported_at=stamp(), reported_by=a.agent)
    write_json(CAPACITY / f'{a.agent}.json', cap)
    print(f'capacity of {a.agent}: state={cap.get("state")} remaining={cap.get("remaining_pct")} tiers={tiers}')


def cmd_msg_send(a: argparse.Namespace) -> None:
    targets = [x for x in policy()['agents'] if x != a.agent] if a.to == 'all' else [check_agent(a.to)]
    for target in targets:
        write_json(INBOX / target / f'{now():%Y%m%d-%H%M%S}-{a.agent}-{uuid.uuid4().hex[:6]}.json',
                   {'from': a.agent, 'to': target, 'at': stamp(), 'task': a.task, 'text': a.text})
    print(f'sent to {", ".join(targets)}')


def unread(agent: str) -> list[Path]:
    return sorted((INBOX / agent).glob('*.json'))


def cmd_msg_read(a: argparse.Namespace) -> None:
    files = unread(a.agent)
    for path in files:
        msg = read_json(path)
        print(f'[{msg["at"]}] {msg["from"]} -> {a.agent}' + (f' ({msg["task"]})' if msg.get('task') else ''))
        print(f'  {msg["text"]}')
        (path.parent / 'read').mkdir(exist_ok=True)
        os.replace(path, path.parent / 'read' / path.name)
    print(f'{len(files)} message(s)')


def poll_items(agent: str) -> list[str]:
    pol = policy()
    tasks = all_tasks()
    items = [f'TODO   {fmt_task(t)}' for t in tasks if t.get('assignee') == agent and t['status'] in ('assigned', 'rework')]
    items += [f'YOURS  {fmt_task(t)}' for t in tasks if t.get('assignee') == agent and t['status'] == 'in_progress']
    if unread(agent):
        items.append(f'MAIL   {len(unread(agent))} unread message(s): run `msg read`')
    if agent == pol['cto']:
        items += [f'REVIEW {fmt_task(t)}' for t in tasks if t['status'] in ('review', 'blocked', 'open')]
        items += [f'STALE  {fmt_task(t)} (no update for {age_hours(t["updated_at"]):.0f}h)' for t in tasks
                  if t['status'] in ('assigned', 'in_progress', 'rework') and t.get('assignee') != agent
                  and age_hours(t['updated_at']) > pol['task_stale_hours']]
    return items


def cmd_poll(a: argparse.Namespace) -> None:
    items = poll_items(a.agent)
    print('\n'.join(items) if items else 'NOTHING')


def cmd_board(a: argparse.Namespace) -> None:
    pol = policy()
    print(f'== cluster board {stamp()}  (CTO: {pol["cto"]})')
    for agent in pol['agents']:
        cap, st = capacity_of(agent), read_json(STATUS / f'{agent}.json', {}) or {}
        ok, why = available(agent, pol)
        print(f'\n[{agent}] {"available" if ok else "NOT AVAILABLE"} - {why}')
        for tier, cfg in (cap.get('tiers') or {}).items():
            print(f'   {tier:<8} {cfg.get("model")} / {cfg.get("effort")}')
        if st:
            print(f'   doing: {st.get("doing")}  (task {st.get("task")}, {age_hours(st.get("updated_at")):.1f}h ago)')
            if st.get('files'):
                print(f'   files: {", ".join(st["files"])}')
            if st.get('blocked_on'):
                print(f'   blocked on: {st["blocked_on"]}')
    rows = [t for t in all_tasks() if t['status'] in OPEN_STATES]
    print('\n== open tasks')
    print('\n'.join(fmt_task(t) for t in rows) or 'none')


def cmd_route(a: argparse.Namespace) -> None:
    agent, reasons = route(a.type, a.tier)
    print(f'{a.type}/{a.tier} -> {agent}')
    print('\n'.join(f'  {r}' for r in reasons))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--agent', required=True, help='who is calling: claude, codex, or antigravity')
    sub = p.add_subparsers(dest='cmd', required=True)

    sub.add_parser('poll', help='what needs my attention; prints NOTHING when idle').set_defaults(fn=cmd_poll)
    sub.add_parser('board', help='everyone: capacity, current work, open tasks').set_defaults(fn=cmd_board)
    r = sub.add_parser('route', help='show who would get a task')
    r.add_argument('--type', default='general')
    r.add_argument('--tier', default='standard')
    r.set_defaults(fn=cmd_route)

    task = sub.add_parser('task').add_subparsers(dest='task_cmd', required=True)
    n = task.add_parser('new')
    n.add_argument('--title', required=True)
    n.add_argument('--goal', required=True)
    n.add_argument('--accept', action='append', help='one acceptance criterion; repeat')
    n.add_argument('--type', default='general')
    n.add_argument('--tier', default='standard')
    n.add_argument('--assign', default='auto')
    n.add_argument('--project', help='absolute path of the repository or folder')
    n.add_argument('--paths', nargs='*', help='files or folders this task may write')
    n.add_argument('--model')
    n.add_argument('--effort')
    n.set_defaults(fn=cmd_task_new)
    ls = task.add_parser('list')
    ls.add_argument('--all', action='store_true')
    ls.add_argument('--assignee')
    ls.set_defaults(fn=cmd_task_list)
    sh = task.add_parser('show')
    sh.add_argument('id')
    sh.set_defaults(fn=cmd_task_show)

    def step(name: str, fn: Any, *extra: str) -> None:
        sp = task.add_parser(name)
        sp.add_argument('id')
        sp.add_argument('--note', default='')
        for flag in extra:
            sp.add_argument(flag, required=flag in ('--result', '--to'))
        sp.set_defaults(fn=fn)

    step('claim', lambda a: transition(a, ('assigned', 'rework'), 'in_progress', 'claimed', assignee_only=True))
    step('done', lambda a: transition(a, ('in_progress',), 'review', 'submitted', assignee_only=True),
         '--result', '--evidence')
    step('block', lambda a: transition(a, ('assigned', 'in_progress', 'rework'), 'blocked', 'blocked', assignee_only=True))
    step('release', lambda a: transition(a, ('assigned', 'in_progress', 'rework', 'blocked'), 'open', 'released',
                                         assignee_only=True))
    step('accept', lambda a: transition(a, ('review',), 'done', 'accepted', cto_only=True))
    step('rework', lambda a: transition(a, ('review', 'blocked'), 'rework', 'rework', cto_only=True))
    step('cancel', lambda a: transition(a, OPEN_STATES, 'cancelled', 'cancelled', cto_only=True))
    step('assign', lambda a: transition(a, ('open', 'assigned', 'blocked', 'rework'), 'assigned', 'assigned',
                                        cto_only=True), '--to')
    nt = task.add_parser('note')
    nt.add_argument('id')
    nt.add_argument('note')
    nt.set_defaults(fn=cmd_task_note)

    st = sub.add_parser('status', help='tell the others what you are doing')
    st.add_argument('--doing', required=True)
    st.add_argument('--task')
    st.add_argument('--files', nargs='*')
    st.add_argument('--next')
    st.add_argument('--blocked-on')
    st.set_defaults(fn=cmd_status_set)

    cap = sub.add_parser('capacity', help='report remaining usage and model tiers')
    cap.add_argument('--remaining', type=int, help='percent of quota left, 0-100')
    cap.add_argument('--state', choices=['ok', 'low', 'exhausted', 'paused'])
    cap.add_argument('--resets-at')
    cap.add_argument('--note')
    cap.add_argument('--tier', action='append', help='heavy=MODEL:EFFORT; repeat for standard and light')
    cap.set_defaults(fn=cmd_capacity_set)

    msg = sub.add_parser('msg').add_subparsers(dest='msg_cmd', required=True)
    ms = msg.add_parser('send')
    ms.add_argument('--to', required=True, help='agent name or all')
    ms.add_argument('--task')
    ms.add_argument('text')
    ms.set_defaults(fn=cmd_msg_send)
    msg.add_parser('read').set_defaults(fn=cmd_msg_read)
    return p


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)
        if reconfigure is not None:
            with contextlib.suppress(ValueError):
                reconfigure(encoding='utf-8')
    args = build_parser().parse_args(argv)
    try:
        if not _HAS_BOARD:
            raise ClusterError('no board folder: set CLUSTER_DIR, or put this script and a policy.json in the board folder')
        check_agent(args.agent)
        args.fn(args)
    except ClusterError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
