import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'scripts' / 'validate_repo.py'
DEMO = ROOT / 'examples' / 'end_to_end_demo' / 'run_demo.py'


class RepoAndDemoTests(unittest.TestCase):
    def test_validate_repo_and_standalone_package(self) -> None:
        proc = subprocess.run(
            [sys.executable, '-B', str(VALIDATOR), '--verify-package'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertIn('Repository validation passed.', proc.stdout)

    def test_end_to_end_demo_executes_and_reports_boundaries(self) -> None:
        proc = subprocess.run(
            [sys.executable, '-B', str(DEMO), '--verify', '--json'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        report = json.loads(proc.stdout)
        self.assertEqual(report['status'], 'accepted_and_delivered_locally')
        self.assertEqual(report['stages']['2_pm02_routing_and_dispatch']['dispatch_ready'], False)
        self.assertEqual(report['stages']['3_engineer_guard_patch_and_test']['competing_cs0202_exit'], 2)
        self.assertEqual(report['stages']['3_engineer_guard_patch_and_test']['watched_test_exit'], 0)
        self.assertTrue(report['stages']['4_pm02_acceptance_and_clerk_summary']['sha256_verified'])
        boundaries = report['evidence_boundaries']
        self.assertTrue(boundaries['executed_locally'])
        self.assertTrue(boundaries['simulated_in_demo'])
        self.assertTrue(boundaries['requires_host_runtime'])


if __name__ == '__main__':
    unittest.main()
