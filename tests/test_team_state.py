import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'cto-agent-team' / 'scripts' / 'team_state.py'
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('team_state', SCRIPT)
team_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(team_state)


class TeamStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / 'private'

    def cli(self, command, *args, ok=True, state=None):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), command,
                                 '--state-dir', str(state or self.state), *args],
                                capture_output=True, text=True, encoding='utf-8')
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertNotIn('Traceback', result.stderr)
        return result

    def load(self, filename):
        return json.loads((self.state / filename).read_text(encoding='utf-8'))

    def save(self, filename, data):
        (self.state / filename).write_text(json.dumps(data), encoding='utf-8')

    def register(self, role, thread, status='created', host='test-host', ok=True):
        return self.cli('register', '--role', role, '--thread-id', str(thread),
                        '--host-id', host, '--status', status, ok=ok)

    def test_init_is_planned_and_repeat_preserves_registration(self):
        self.cli('init')
        org, registry = self.load('org.json'), self.load('registry.json')
        self.assertEqual(org['root_role'], 'CTO')
        self.assertEqual(len(org['teams']), 5)
        self.assertTrue(all(len(t['engineers']) == 10 for t in org['teams']))
        self.assertEqual(len(registry['roles']), 55)
        self.assertNotIn('CTO', registry['roles'])
        self.assertTrue(all(e['status'] == 'planned' and e['registration'] == 'unregistered'
                            and e['thread_id'] is None and e['host_id'] is None
                            and e['model_status'] == 'requested'
                            for e in registry['roles'].values()))
        thread = uuid.uuid4()
        self.register('PM01', thread)
        before = (self.state / 'registry.json').read_bytes()
        self.cli('init')
        self.assertEqual((self.state / 'registry.json').read_bytes(), before)
        self.cli('validate')
        self.cli('validate', '--require-ready', ok=False)

    def test_custom_models_and_incompatible_reinit(self):
        self.cli('init', '--pm-model', 'custom-pm', '--engineer-model', 'custom-eng', '--effort', 'high')
        org = self.load('org.json')
        entries = self.load('registry.json')['roles']
        self.assertEqual(entries['PM01']['model'], {'model': 'custom-pm', 'reasoning_effort': 'high'})
        self.assertEqual(entries['CS0101']['model'], {'model': 'custom-eng', 'reasoning_effort': 'high'})
        self.assertEqual(org['models']['engineer'], entries['CS0101']['model'])
        before = (self.state / 'org.json').read_bytes(), (self.state / 'registry.json').read_bytes()
        self.cli('init', ok=False)
        self.assertEqual(before, ((self.state / 'org.json').read_bytes(), (self.state / 'registry.json').read_bytes()))
        self.cli('init', '--pm-model', 'custom-pm', '--engineer-model', 'custom-eng', '--effort', 'high')
        self.cli('validate')

    def test_register_guards_and_idempotence(self):
        self.cli('init')
        first, second = uuid.uuid4(), uuid.uuid4()
        self.register('PM01', first)
        before = (self.state / 'registry.json').read_bytes()
        self.register('PM01', first)
        self.assertEqual(before, (self.state / 'registry.json').read_bytes())
        for role, thread, host in [('PM02', first, 'test-host'), ('PM01', second, 'test-host'),
                                   ('INVALID', second, 'test-host'), ('PM02', 'bogus', 'test-host'),
                                   ('PM02', second, '  '), ('PM01', first, 'other-host')]:
            self.register(role, thread, host=host, ok=False)
            self.assertEqual(before, (self.state / 'registry.json').read_bytes())
        self.register('PM01', first, 'ready')
        before = (self.state / 'registry.json').read_bytes()
        self.register('PM01', first, 'ready')
        self.register('PM01', first, 'created', ok=False)
        self.assertEqual(before, (self.state / 'registry.json').read_bytes())

    def test_public_tree_rejected_and_no_files_created(self):
        for directory in (ROOT / 'temporary-private-test', ROOT / 'skills' / 'cto-agent-team' / 'temporary-private-test', ROOT / 'skills' / '..' / 'temporary-private-test'):
            self.cli('init', state=directory, ok=False)
            self.assertFalse(directory.exists())
        if hasattr(os, 'symlink'):
            alias = Path(self.tmp.name) / 'alias'
            try:
                alias.symlink_to(ROOT, target_is_directory=True)
            except OSError:
                return
            self.cli('init', state=alias / 'temporary-private-test', ok=False)
            self.assertFalse((ROOT / 'temporary-private-test').exists())

    def test_validate_detects_corruption_and_relationships(self):
        self.cli('init')
        org = self.load('org.json')
        registry = self.load('registry.json')
        cases = []
        bad = json.loads(json.dumps(registry)); bad['roles']['CS0101']['parent'] = 'PM02'; cases.append(('registry.json', bad))
        bad = json.loads(json.dumps(registry)); bad['roles']['CS0101']['model']['reasoning_effort'] = 'low'; cases.append(('registry.json', bad))
        bad = json.loads(json.dumps(registry)); bad['roles']['PM01']['status'] = 'ready'; cases.append(('registry.json', bad))
        bad = json.loads(json.dumps(registry)); del bad['roles']['CS0101']; cases.append(('registry.json', bad))
        bad = json.loads(json.dumps(org)); bad['teams'][0]['engineers'][0], bad['teams'][1]['engineers'][0] = bad['teams'][1]['engineers'][0], bad['teams'][0]['engineers'][0]; cases.append(('org.json', bad))
        bad = json.loads(json.dumps(org)); bad['teams'][0]['engineers'][1][0] = bad['teams'][0]['engineers'][0][0]; cases.append(('org.json', bad))
        for filename, bad in cases:
            with self.subTest(filename=filename, bad=bad):
                self.save(filename, bad)
                self.cli('validate', ok=False)
                self.save('org.json', org)
                self.save('registry.json', registry)
        (self.state / 'registry.json').write_text('{invalid', encoding='utf-8')
        self.cli('validate', ok=False)

    def test_duplicate_registered_thread_detected(self):
        self.cli('init')
        thread = uuid.uuid4()
        self.register('PM01', thread)
        self.register('PM02', uuid.uuid4())
        registry = self.load('registry.json')
        registry['roles']['PM02']['thread_id'] = str(thread)
        self.save('registry.json', registry)
        self.cli('validate', ok=False)

    def test_all_roles_ready_and_reporting(self):
        self.cli('init')
        org, roles = self.load('org.json'), self.load('registry.json')['roles']
        for team in org['teams']:
            self.assertEqual(roles[team['id']]['parent'], 'CTO')
            for child, _ in team['engineers']:
                self.assertEqual(roles[child]['parent'], team['id'])
        for role in roles:
            self.register(role, uuid.uuid4(), 'ready')
        self.cli('validate', '--require-ready')
        self.assertTrue(all(e['status'] == 'ready' and e['registration'] == 'registered'
                            for e in self.load('registry.json')['roles'].values()))

    def test_atomic_replace_failure_preserves_original_and_cleans_temp(self):
        self.cli('init')
        target = self.state / 'registry.json'
        before = target.read_bytes()
        with mock.patch.object(team_state.os, 'replace', side_effect=OSError('replace failed')):
            with self.assertRaises(OSError):
                team_state.atomic_json(target, {'changed': True})
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(list(self.state.glob('.registry.json.*.tmp')), [])
        self.cli('validate')


if __name__ == '__main__':
    unittest.main()
