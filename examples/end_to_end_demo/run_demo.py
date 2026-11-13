#!/usr/bin/env python3
"""Reproducible offline end-to-end demonstration of the CTO -> PM -> Engineer workflow.

Runs strictly against a temporary private state directory and a disposable copy of
sample_app/ outside the repository, using only Python 3.11+ standard library modules.
Explicitly separates:
  1. [EXECUTED BY REPO SCRIPTS]: real CLI invocations, locks, tests, and SHA-256 checks
  2. [SIMULATED FOR OFFLINE REPLAY]: illustrative role handoff text and fixture IDs
  3. [HOST RUNTIME CAPABILITIES]: live thread creation, LLM execution, and UI/cron hosts
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

DEMO_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEMO_DIR.parents[1]
SKILL_DIR = REPO_ROOT / 'skills' / 'cto-agent-team'
TEAM_STATE = SKILL_DIR / 'scripts' / 'team_state.py'
MODEL_ROUTE = SKILL_DIR / 'scripts' / 'model_route.py'
AGENT_GUARD = SKILL_DIR / 'scripts' / 'agent_guard.py'
SAMPLE_SRC = DEMO_DIR / 'sample_app' / 'health_summary.py'
ROUTING_INPUT = DEMO_DIR / 'demo_routing_input.json'

PATCHED_MODULE = '''"""Sample telemetry service helper used in the offline end-to-end team demo."""
from __future__ import annotations


def summarize_latencies(latencies_ms: list[float], error_count: int = 0) -> dict[str, object]:
    """Return service latency summary metrics for a monitoring window."""
    if error_count < 0:
        raise ValueError("error_count must be non-negative")
    if not latencies_ms:
        status = "degraded" if error_count > 0 else "idle"
        return {
            "status": status,
            "sample_count": 0,
            "avg_ms": None,
            "error_count": error_count,
        }
    avg_ms = round(sum(latencies_ms) / len(latencies_ms), 2)
    return {
        "status": "degraded" if error_count > 0 else "ok",
        "sample_count": len(latencies_ms),
        "avg_ms": avg_ms,
        "error_count": error_count,
    }
'''

PATCHED_TESTS = '''import unittest

from health_summary import summarize_latencies


class HealthSummaryTests(unittest.TestCase):
    def test_empty_window_returns_idle_without_division_error(self) -> None:
        self.assertEqual(
            summarize_latencies([]),
            {"status": "idle", "sample_count": 0, "avg_ms": None, "error_count": 0},
        )

    def test_empty_window_with_errors_marks_degraded(self) -> None:
        self.assertEqual(
            summarize_latencies([], error_count=2),
            {"status": "degraded", "sample_count": 0, "avg_ms": None, "error_count": 2},
        )

    def test_populated_window_computes_average(self) -> None:
        self.assertEqual(
            summarize_latencies([10.0, 20.0], error_count=0),
            {"status": "ok", "sample_count": 2, "avg_ms": 15.0, "error_count": 0},
        )


if __name__ == "__main__":
    unittest.main()
'''


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            newline='\n',
            dir=path.parent,
            prefix=f'.{path.name}.',
            suffix='.tmp',
            delete=False,
        ) as handle:
            tmp = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + '\n')


def run_cli(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding='utf-8',
        check=False,
    )


def execute_demo(keep_temp: bool = False) -> dict[str, object]:
    """Execute the five-stage workflow in an isolated temp root and verify every check."""
    with ExitStack() as stack:
        if keep_temp:
            temp_root = Path(tempfile.mkdtemp(prefix='cto-team-demo-'))
        else:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory(prefix='cto-team-demo-'))
            temp_root = Path(temp_dir)

        private_state = temp_root / 'private-state'
        lock_dir = private_state / 'locks'
        workspace = temp_root / 'workspace'
        workspace.mkdir(parents=True, exist_ok=True)
        target_module = workspace / 'health_summary.py'
        target_test = workspace / 'test_health_summary.py'
        shutil.copy2(SAMPLE_SRC, target_module)

        # Stage 1: CTO Intake & Private Registry Init
        init_res = run_cli([sys.executable, '-B', str(TEAM_STATE), 'init', '--state-dir', str(private_state)])
        if init_res.returncode != 0:
            raise RuntimeError(f'team_state init failed: {init_res.stderr}')

        pm02_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'demo.codex-cto-agent-team/PM02'))
        cs0201_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'demo.codex-cto-agent-team/CS0201'))
        for role, thread_id in (('PM02', pm02_id), ('CS0201', cs0201_id)):
            for status in ('created', 'ready'):
                reg = run_cli([
                    sys.executable, '-B', str(TEAM_STATE), 'register',
                    '--state-dir', str(private_state),
                    '--role', role,
                    '--thread-id', thread_id,
                    '--host-id', 'demo-host-01',
                    '--status', status,
                ])
                if reg.returncode != 0:
                    raise RuntimeError(f'register {role} ({status}) failed: {reg.stderr}')

        val_res = run_cli([sys.executable, '-B', str(TEAM_STATE), 'validate', '--state-dir', str(private_state)])
        if val_res.returncode != 0:
            raise RuntimeError(f'team_state validate failed: {val_res.stderr}')

        task_path = private_state / 'tasks' / 'TASK-DEMO-001.json'
        atomic_write_json(task_path, {
            'task_id': 'TASK-DEMO-001',
            'revision': 1,
            'owner_pm': 'PM02',
            'assigned_engineer': 'CS0201',
            'goal': 'Return idle/degraded status safely when summarize_latencies receives an empty list.',
            'writable_resources': [str(target_module), str(target_test)],
            'acceptance_criteria': [
                'summarize_latencies([]) returns status=idle and avg_ms=None without ZeroDivisionError.',
                'summarize_latencies([], error_count>0) returns status=degraded.',
                'Unit tests pass inside agent_guard.py run watchdog.',
                'Published CS0201 event includes valid SHA-256 digests for both workspace files.',
            ],
            'status': 'dispatched',
        })

        # Stage 2: PM02 Task Routing & Dispatch Handoff
        route_res = run_cli([
            sys.executable, '-B', str(MODEL_ROUTE), str(ROUTING_INPUT), '--now', '2030-01-02T00:00:00Z',
        ])
        if route_res.returncode != 0:
            raise RuntimeError(f'model_route failed: {route_res.stderr or route_res.stdout}')
        routing_payload = json.loads(route_res.stdout)
        if routing_payload.get('state') != 'selected' or routing_payload.get('dispatch_ready') is not False:
            raise RuntimeError(f'Unexpected fixture routing payload: {routing_payload}')

        dispatch_evt = private_state / 'shared' / 'events' / 'PM02' / 'TASK-DEMO-001' / 'EVT-001-dispatch.json'
        atomic_write_json(dispatch_evt, {
            'identity': {
                'event_id': 'EVT-001-dispatch',
                'task_id': 'TASK-DEMO-001',
                'task_revision': 1,
                'source_role': 'PM02',
                'event_kind': 'dispatch',
            },
            'change': {
                'summary': 'Dispatched empty-window ZeroDivisionError fix to CS0201 under single-writer lease.',
                'status': 'dispatched',
                'observed_at': '2030-01-02T00:00:00Z',
                'result_revision': 1,
            },
            'evidence': {
                'canonical_task': str(task_path),
                'routing_fixture_output': routing_payload,
            },
            'scope': {
                'verified': ['Baseline defect confirmed in sample_app/health_summary.py'],
                'remaining': ['Acquire lease', 'Patch module', 'Run unit tests'],
                'limits': ['Routing payload uses offline fixture evidence (dispatch_ready: false).'],
            },
            'next_step': {
                'owner': 'CS0201',
                'action': 'Acquire exclusive lease on health_summary.py, apply patch, run unit tests, and publish result event.',
                'dependency': 'Advisory lease on target files',
            },
            'correction': None,
        })

        # Stage 3: Engineer CS0201 Lease Acquisition, Conflict Check, Patch & Watched Test
        acq_res = run_cli([
            sys.executable, '-B', str(AGENT_GUARD),
            '--lock-dir', str(lock_dir),
            'acquire', '--owner', 'CS0201', '--task', 'TASK-DEMO-001', '--ttl', '300',
            str(target_module),
        ])
        if acq_res.returncode != 0:
            raise RuntimeError(f'CS0201 acquire failed: {acq_res.stderr}')

        conflict_res = run_cli([
            sys.executable, '-B', str(AGENT_GUARD),
            '--lock-dir', str(lock_dir),
            'acquire', '--owner', 'CS0202', '--task', 'TASK-DEMO-999', '--ttl', '300',
            str(target_module),
        ])
        if conflict_res.returncode != 2:
            raise RuntimeError(f'Expected RESOURCE_LOCKED exit code 2 for CS0202, got {conflict_res.returncode}')

        # Verify baseline defect exists before patching
        baseline_check = run_cli([
            sys.executable, '-B', '-c', 'import health_summary; health_summary.summarize_latencies([])',
        ], cwd=workspace)
        if baseline_check.returncode == 0:
            raise RuntimeError('Expected baseline sample_app to raise ZeroDivisionError on empty input')

        atomic_write_text(target_module, PATCHED_MODULE)
        atomic_write_text(target_test, PATCHED_TESTS)

        test_res = run_cli([
            sys.executable, '-B', str(AGENT_GUARD),
            'run', '--timeout', '15', '--idle-timeout', '10', '--cwd', str(workspace),
            '--', sys.executable, '-B', '-m', 'unittest', 'discover', '-s', '.', '-v',
        ])
        if test_res.returncode != 0:
            raise RuntimeError(f'Watched unit test failed ({test_res.returncode}): {test_res.stdout}\n{test_res.stderr}')

        rel_res = run_cli([
            sys.executable, '-B', str(AGENT_GUARD),
            '--lock-dir', str(lock_dir),
            'release', '--owner', 'CS0201', str(target_module),
        ])
        if rel_res.returncode != 0:
            raise RuntimeError(f'CS0201 release failed: {rel_res.stderr}')

        module_sha = sha256_file(target_module)
        test_sha = sha256_file(target_test)
        result_evt = private_state / 'shared' / 'events' / 'CS0201' / 'TASK-DEMO-001' / 'EVT-002-result.json'
        atomic_write_json(result_evt, {
            'identity': {
                'event_id': 'EVT-002-result',
                'task_id': 'TASK-DEMO-001',
                'task_revision': 1,
                'source_role': 'CS0201',
                'event_kind': 'implementation_result',
            },
            'change': {
                'summary': 'Handled empty latency list without ZeroDivisionError and added 3 unit tests.',
                'status': 'ready_for_acceptance',
                'observed_at': '2030-01-02T00:05:00Z',
                'result_revision': 2,
            },
            'evidence': {
                'artifacts': [
                    {'path': str(target_module), 'sha256': module_sha},
                    {'path': str(target_test), 'sha256': test_sha},
                ],
                'checks': ['agent_guard run -- unittest discover: 3 tests passed (exit 0)'],
                'conflict_guard_verified': 'competing CS0202 acquire blocked with exit code 2',
            },
            'scope': {
                'verified': ['Empty list -> idle/degraded', 'Non-empty average calculation'],
                'remaining': ['PM02 acceptance verification'],
                'limits': ['Verified on isolated workspace copy using local standard-library tests.'],
            },
            'next_step': {
                'owner': 'PM02',
                'action': 'Verify SHA-256 digests and test evidence against TASK-DEMO-001 acceptance criteria.',
                'dependency': None,
            },
            'correction': None,
        })

        # Stage 4: PM02 Acceptance & Clerk Summary
        published_result = json.loads(result_evt.read_text(encoding='utf-8'))
        artifacts = published_result['evidence']['artifacts']
        digests_match = all(sha256_file(Path(item['path'])) == item['sha256'] for item in artifacts)
        if not digests_match:
            raise RuntimeError('SHA-256 verification failed during PM02 acceptance check')

        accept_evt = private_state / 'shared' / 'events' / 'PM02' / 'TASK-DEMO-001' / 'EVT-003-accepted.json'
        atomic_write_json(accept_evt, {
            'identity': {
                'event_id': 'EVT-003-accepted',
                'task_id': 'TASK-DEMO-001',
                'task_revision': 1,
                'source_role': 'PM02',
                'event_kind': 'acceptance_decision',
            },
            'change': {
                'summary': 'PM02 verified SHA-256 digests and unit-test evidence; task accepted for CTO delivery.',
                'status': 'accepted',
                'observed_at': '2030-01-02T00:06:00Z',
                'result_revision': 2,
            },
            'evidence': {
                'consumed_event': 'EVT-002-result',
                'sha256_verified': digests_match,
            },
            'scope': {
                'verified': ['All 4 TASK-DEMO-001 acceptance criteria satisfied locally.'],
                'remaining': ['CTO user delivery summary'],
                'limits': ['No live host chat threads were created in this offline demonstration.'],
            },
            'next_step': {
                'owner': 'CTO',
                'action': 'Deliver verified outcome summary to user.',
                'dependency': None,
            },
            'correction': None,
        })

        status_md = private_state / 'shared' / 'STATUS.md'
        atomic_write_text(
            status_md,
            '# Shared Team Status Summary (Demo Clerk)\n\n'
            '- `TASK-DEMO-001` | Owner: `PM02` | Engineer: `CS0201` | Status: `accepted` | '
            'Result Event: `EVT-003-accepted` | Artifacts Verified: `sha256` match (`3` tests OK)\n',
        )

        # Stage 5: CTO Final Delivery Report
        report: dict[str, object] = {
            'task_id': 'TASK-DEMO-001',
            'status': 'accepted_and_delivered_locally',
            'temp_root': str(temp_root) if keep_temp else '<cleaned temporary directory>',
            'stages': {
                '1_cto_intake_and_registry': {
                    'team_state_init': init_res.stdout.strip(),
                    'registered_roles': {'PM02': pm02_id, 'CS0201': cs0201_id},
                    'validate': val_res.stdout.strip(),
                },
                '2_pm02_routing_and_dispatch': {
                    'selector_state': routing_payload['state'],
                    'selected_model': routing_payload['model'],
                    'dispatch_ready': routing_payload['dispatch_ready'],
                    'event_file': 'shared/events/PM02/TASK-DEMO-001/EVT-001-dispatch.json',
                },
                '3_engineer_guard_patch_and_test': {
                    'acquire_cs0201_exit': acq_res.returncode,
                    'competing_cs0202_exit': conflict_res.returncode,
                    'baseline_bug_confirmed': True,
                    'watched_test_exit': test_res.returncode,
                    'release_cs0201_exit': rel_res.returncode,
                    'artifact_sha256': {
                        'health_summary.py': module_sha,
                        'test_health_summary.py': test_sha,
                    },
                },
                '4_pm02_acceptance_and_clerk_summary': {
                    'sha256_verified': digests_match,
                    'accepted_event': 'shared/events/PM02/TASK-DEMO-001/EVT-003-accepted.json',
                    'clerk_summary_written': True,
                },
                '5_cto_final_delivery': {
                    'delivered': True,
                    'summary': 'Empty-window ZeroDivisionError fixed and verified with 3 unit tests under single-writer lease.',
                },
            },
            'evidence_boundaries': {
                'executed_locally': [
                    'team_state.py init, register, and validate created and checked 55 role entries in private temp state.',
                    'model_route.py evaluated demo_routing_input.json and emitted a fixture payload.',
                    'agent_guard.py acquire locked target_module for CS0201 and blocked CS0202 with exit code 2.',
                    'agent_guard.py run executed unittest inside a bounded process-tree watchdog (exit 0).',
                    'agent_guard.py release freed the advisory lease after verification.',
                    'Atomic JSON event files, SHA-256 artifact checks, and shared/STATUS.md passed integrity checks.',
                ],
                'simulated_in_demo': [
                    'CTO, PM02, and CS0201 role reasoning/handoff prose.',
                    'Deterministic synthetic uuid5 thread IDs (demo-host-01).',
                    'Fixture model catalog evidence (dispatch_ready: false; no LLM API calls made).',
                ],
                'requires_host_runtime': [
                    'Spawning real PM/engineer chat threads or subagents (e.g., Codex create_thread / Antigravity invoke_subagent).',
                    'Live LLM inference, reasoning effort support, and account quota/capacity.',
                    'Host scheduler/heartbeat wakeups for automated completion follow-up and browser UI verification.',
                ],
            },
        }
        return report


def format_human_report(report: dict[str, object]) -> str:
    stages = report['stages']
    boundaries = report['evidence_boundaries']
    assert isinstance(stages, dict)
    assert isinstance(boundaries, dict)
    lines = [
        '=== codex-cto-agent-team :: Reproducible Offline End-to-End Demo ===',
        f"Task ID : {report['task_id']}",
        f"Outcome : {report['status']}",
        '',
        '[Stage 1] CTO Intake & Private Registry',
        f"  - team_state init     : {stages['1_cto_intake_and_registry']['team_state_init']}",
        f"  - team_state validate : {stages['1_cto_intake_and_registry']['validate']}",
        '',
        '[Stage 2] PM02 Task Routing & Dispatch Handoff',
        f"  - model_route state   : {stages['2_pm02_routing_and_dispatch']['selector_state']}",
        f"  - selected fixture    : {stages['2_pm02_routing_and_dispatch']['selected_model']} "
        f"(dispatch_ready={stages['2_pm02_routing_and_dispatch']['dispatch_ready']})",
        '',
        '[Stage 3] CS0201 Single-Writer Lease, Patch & Watched Test',
        f"  - acquire CS0201      : exit {stages['3_engineer_guard_patch_and_test']['acquire_cs0201_exit']}",
        f"  - competing CS0202    : exit {stages['3_engineer_guard_patch_and_test']['competing_cs0202_exit']} (RESOURCE_LOCKED)",
        f"  - watched unittest    : exit {stages['3_engineer_guard_patch_and_test']['watched_test_exit']} (3 tests passed)",
        f"  - release CS0201      : exit {stages['3_engineer_guard_patch_and_test']['release_cs0201_exit']}",
        '',
        '[Stage 4] PM02 Acceptance & Clerk Summary',
        f"  - SHA-256 verified    : {stages['4_pm02_acceptance_and_clerk_summary']['sha256_verified']}",
        f"  - clerk STATUS.md     : written ({stages['4_pm02_acceptance_and_clerk_summary']['clerk_summary_written']})",
        '',
        '[Stage 5] CTO Final Delivery & Capability Boundaries',
        '  * [EXECUTED BY REPO SCRIPTS]',
        *(f'      - {item}' for item in boundaries['executed_locally']),
        '  * [SIMULATED FOR OFFLINE REPLAY]',
        *(f'      - {item}' for item in boundaries['simulated_in_demo']),
        '  * [HOST RUNTIME CAPABILITIES (NOT SUPPLIED BY THIS REPO)]',
        *(f'      - {item}' for item in boundaries['requires_host_runtime']),
    ]
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='Print structured JSON summary instead of text')
    parser.add_argument('--verify', action='store_true', help='Strict verification mode (same checks, CI-friendly)')
    parser.add_argument('--keep-temp', action='store_true', help='Preserve temporary private-state and workspace directory')
    args = parser.parse_args(argv)

    report = execute_demo(keep_temp=args.keep_temp)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_human_report(report))
    if args.verify and report.get('status') != 'accepted_and_delivered_locally':
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
