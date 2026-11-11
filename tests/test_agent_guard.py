import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'cto-agent-team' / 'scripts' / 'agent_guard.py'


class AgentGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.locks = Path(self.tmp.name) / 'private-locks'

    def cli(self, *args, lock_dir=True):
        cmd = [sys.executable, '-B', str(SCRIPT)]
        if lock_dir is True:
            cmd.extend(['--lock-dir', str(self.locks)])
        elif isinstance(lock_dir, (str, Path)):
            cmd.extend(['--lock-dir', str(lock_dir)])
        cmd.extend(str(a) for a in args)
        return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

    def test_acquire_renew_conflict_rollback_and_release(self):
        res_a = str(Path(self.tmp.name) / 'shared-a.txt')
        res_b = str(Path(self.tmp.name) / 'shared-b.txt')

        r1 = self.cli('acquire', '--owner', 'PM01', '--task', 'TASK-1', '--ttl', '120', res_a)
        self.assertEqual(r1.returncode, 0, r1.stderr)
        data1 = json.loads(r1.stdout)
        self.assertTrue(data1['ok'])
        self.assertEqual(data1['locks'][0]['status'], 'acquired')

        # Same owner + task renews idempotently
        r_renew = self.cli('acquire', '--owner', 'PM01', '--task', 'TASK-1', '--ttl', '120', res_a)
        self.assertEqual(r_renew.returncode, 0, r_renew.stderr)
        self.assertEqual(json.loads(r_renew.stdout)['locks'][0]['status'], 'renewed')

        # Partial multi-resource conflict rolls back newly acquired slot (res_b) and exits 2
        r_conflict = self.cli('acquire', '--owner', 'PM02', '--task', 'TASK-2', '--ttl', '120', res_b, res_a)
        self.assertEqual(r_conflict.returncode, 2)
        conflict = json.loads(r_conflict.stdout)
        self.assertEqual(conflict['error'], 'RESOURCE_LOCKED')
        status = json.loads(self.cli('locks').stdout)
        self.assertEqual(status['active_count'], 1)

        # Wrong owner cannot release without --force
        r_wrong = self.cli('release', '--owner', 'PM02', res_a)
        self.assertEqual(r_wrong.returncode, 2)
        self.assertEqual(json.loads(self.cli('locks').stdout)['active_count'], 1)

        # Owner releases cleanly
        r_rel = self.cli('release', '--owner', 'PM01', res_a)
        self.assertEqual(r_rel.returncode, 0, r_rel.stderr)
        self.assertEqual(json.loads(self.cli('locks').stdout)['active_count'], 0)

    def test_expired_lease_takeover_and_prune(self):
        res = str(Path(self.tmp.name) / 'expiring.txt')
        r1 = self.cli('acquire', '--owner', 'CS0101', '--task', 'TASK-OLD', '--ttl', '1', res)
        self.assertEqual(r1.returncode, 0, r1.stderr)
        time.sleep(1.15)

        # Another agent can take over expired lease cleanly
        r2 = self.cli('acquire', '--owner', 'CS0201', '--task', 'TASK-NEW', '--ttl', '1', res)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(json.loads(r2.stdout)['locks'][0]['lease']['owner'], 'CS0201')

        time.sleep(1.15)
        pruned = json.loads(self.cli('locks', '--prune').stdout)
        self.assertEqual(pruned['active_count'], 0)
        self.assertEqual(len(pruned['pruned']), 1)

    def test_public_tree_lock_dir_rejected(self):
        for bad in (ROOT / 'temp-locks', ROOT / 'skills' / 'cto-agent-team' / 'temp-locks'):
            res = self.cli('locks', lock_dir=bad)
            self.assertEqual(res.returncode, 2)
            self.assertFalse(bad.exists())

    def test_run_watchdog_succeeds_and_kills_hung_command(self):
        ok = self.cli('run', '--timeout', '10', '--idle-timeout', '5', '--',
                      sys.executable, '-c', 'print("guard-ok")', lock_dir=False)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn('guard-ok', ok.stdout)

        hung = self.cli('run', '--timeout', '5', '--idle-timeout', '0.6', '--',
                        sys.executable, '-c', 'import time; print("started", flush=True); time.sleep(10)',
                        lock_dir=False)
        self.assertEqual(hung.returncode, 124)
        self.assertIn('started', hung.stdout)
        self.assertIn('AGENT_GUARD_TIMEOUT', hung.stderr)


if __name__ == '__main__':
    unittest.main()
