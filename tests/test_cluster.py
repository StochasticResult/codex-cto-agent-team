"""Smoke tests for cluster.py. Run: python -m unittest discover -s tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills' / 'cto-agent-team' / 'scripts' / 'cluster.py'


class ClusterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.env = {**os.environ, 'CLUSTER_DIR': self.tmp.name}
        self.addCleanup(self.tmp.cleanup)

    def run_cli(self, agent: str, *args: str, ok: bool = True) -> str:
        proc = subprocess.run([sys.executable, '-B', str(SCRIPT), '--agent', agent, *args],
                              capture_output=True, text=True, encoding='utf-8', env=self.env, check=False)
        self.assertEqual(proc.returncode == 0, ok, proc.stdout + proc.stderr)
        return proc.stdout + proc.stderr

    def task(self, task_id: str) -> dict:
        return json.loads((Path(self.tmp.name) / 'tasks' / f'{task_id}.json').read_text(encoding='utf-8'))

    def test_full_cycle_and_permissions(self) -> None:
        self.run_cli('codex', 'capacity', '--remaining', '80', '--state', 'ok', '--tier', 'standard=m1:high')
        out = self.run_cli('claude', 'task', 'new', '--title', 't', '--goal', 'g', '--accept', 'a1')
        task_id = out.split()[0]
        self.assertEqual(self.task(task_id)['assignee'], 'codex')
        self.assertEqual(self.task(task_id)['model'], 'm1')
        self.assertIn('TODO', self.run_cli('codex', 'poll'))
        self.run_cli('antigravity', 'task', 'claim', task_id, ok=False)   # not the assignee
        self.run_cli('codex', 'task', 'claim', task_id)
        self.run_cli('codex', 'task', 'done', task_id, '--result', 'r', '--evidence', 'e')
        self.assertIn('REVIEW', self.run_cli('claude', 'poll'))
        self.run_cli('codex', 'task', 'accept', task_id, ok=False)        # only the CTO accepts
        self.run_cli('claude', 'task', 'rework', task_id, '--note', 'fix x')
        self.run_cli('codex', 'task', 'claim', task_id)
        self.run_cli('codex', 'task', 'done', task_id, '--result', 'r2')
        self.run_cli('claude', 'task', 'accept', task_id)
        self.assertEqual(self.task(task_id)['status'], 'done')
        self.assertEqual(self.run_cli('codex', 'poll').strip(), 'NOTHING')

    def test_routing_skips_low_capacity(self) -> None:
        self.run_cli('codex', 'capacity', '--remaining', '5')
        self.run_cli('antigravity', 'capacity', '--remaining', '60')
        out = self.run_cli('claude', 'task', 'new', '--title', 't', '--goal', 'g')
        self.assertEqual(self.task(out.split()[0])['assignee'], 'antigravity')
        self.run_cli('antigravity', 'capacity', '--state', 'exhausted')
        self.run_cli('claude', 'capacity', '--state', 'paused')
        out = self.run_cli('claude', 'task', 'new', '--title', 't2', '--goal', 'g')
        self.assertEqual(self.task(out.split()[0])['status'], 'open')

    def test_unmetered_agent_ignores_remaining(self) -> None:
        Path(self.tmp.name, 'policy.json').write_text('{"unmetered": ["codex"]}', encoding='utf-8')
        self.run_cli('codex', 'capacity', '--remaining', '3')
        out = self.run_cli('claude', 'task', 'new', '--title', 't', '--goal', 'g')
        self.assertEqual(self.task(out.split()[0])['assignee'], 'codex')
        self.run_cli('codex', 'capacity', '--state', 'exhausted')
        out = self.run_cli('claude', 'task', 'new', '--title', 't2', '--goal', 'g')
        self.assertNotEqual(self.task(out.split()[0])['assignee'], 'codex')

    def test_member_proposal_messages_and_overlap(self) -> None:
        out = self.run_cli('codex', 'task', 'new', '--title', 'idea', '--goal', 'g', '--paths', 'a.py')
        self.assertEqual(self.task(out.split()[0])['status'], 'open')
        self.run_cli('codex', 'task', 'new', '--title', 'x', '--goal', 'g', '--assign', 'antigravity', ok=False)
        out = self.run_cli('claude', 'task', 'new', '--title', 'y', '--goal', 'g', '--assign', 'codex',
                           '--paths', 'a.py')
        self.assertIn('WARNING', out)
        self.run_cli('codex', 'msg', 'send', '--to', 'claude', '你好')
        self.assertIn('MAIL', self.run_cli('claude', 'poll'))
        self.assertIn('你好', self.run_cli('claude', 'msg', 'read'))
        self.run_cli('codex', 'status', '--doing', 'working', '--files', 'a.py')
        self.assertIn('working', self.run_cli('claude', 'board'))
        self.run_cli('nobody', 'poll', ok=False)


if __name__ == '__main__':
    unittest.main()
