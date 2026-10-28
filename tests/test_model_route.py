"""Offline fixtures exercise decisions and payloads, not provider availability."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/cto-agent-team/scripts/model_route.py'
NOW = datetime(2030, 1, 2, tzinfo=timezone.utc)


def fixture():
    return {
        'workflow': {'task_kind': 'extract', 'required_tools': ['files'],
                     'context_min': 1000, 'quality_gate': 'artifact accepted',
                     'requires_parallel': False, 'complexity': 'simple', 'risk': 'normal',
                     'quality_requirements': ['structured']},
        'host': {'id': 'fixture', 'version': '1', 'skills': 'manual',
                 'subagents': False, 'independent_chats': False, 'explicit_model': True,
                 'completion_notice': False, 'state_files': True, 'tools': ['files'],
                 'parameter_schema_source': 'local fixture schema'},
        'catalog': {'source': 'fixture', 'observed_at': '2030-01-01T00:00:00Z',
                    'expires_at': '2030-01-03T00:00:00Z', 'evidence_kind': 'fixture',
                    'models': [candidate('compact', 'extraction', {'effort': 'medium'}),
                               candidate('capable', 'scoped_engineering', {'effort': 'high'}),
                               candidate('review', 'complex_engineering', {'effort': 'max'})]},
        'policy': {'id': 'fixture-policy', 'revision': 1, 'source': 'fixture permission',
                   'allowed': [], 'max_cost': None, 'allow_unknown_cost': True,
                   'automatic_substitution': True,
                   'candidate_authority': 'verified_existing_resources',
                   'profile': 'fixture-profile', 'task_routes': {'extract': 'extraction'},
                   'max_quality_attempts': 2,
                   'quality_steps': {'extraction': 'scoped_engineering',
                                     'scoped_engineering': 'complex_engineering'}},
        'mapping': {'host': 'fixture', 'model_key': 'model', 'settings_keys': ['effort'],
                    'verified_by': 'local fixture schema'},
        'request': {'pinned_model': None, 'native_settings': {}, 'retry': None,
                    'quality_escalation': None},
        'execution': {'status': 'not_executed', 'request_accepted': False,
                      'tool_receipt': None, 'actual_model': None,
                      'actual_native_settings': None, 'execution_evidence': None}}


def candidate(name, route, settings):
    return {'id': name, 'provider': 'fixture-provider', 'docs_listed': True,
            'account_available': True, 'availability_evidence': 'fixture receipt',
            'tools': ['files'], 'context': 8000, 'cost': None,
            'native_settings': [settings], 'host_supported': True,
            'resource_scope': 'existing', 'capability_evidence': 'fixture artifact',
            'quality_capabilities': ['structured'],
            'route_support': [{'route': route, 'native_settings': settings}]}


def profile():
    return {'id': 'fixture-profile', 'routes': {
        'extraction': {'model': 'compact', 'native_settings': {'effort': 'medium'}},
        'scoped_engineering': {'model': 'capable', 'native_settings': {'effort': 'high'}},
        'complex_engineering': {'model': 'review', 'native_settings': {'effort': 'max'}}}}


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), 'The executable selector is not implemented')
        spec = importlib.util.spec_from_file_location('model_route', SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.doc = fixture()

    def select(self):
        return self.module.select(self.doc, now=NOW, profile=profile())

    def blocked(self, reason=None):
        result = self.select()
        self.assertIsNone(result['parameters'])
        if reason:
            self.assertEqual(result['reason'], reason)
        return result

    def escalation(self, previous):
        self.doc['request']['quality_escalation'] = {
            'reason_kind': 'acceptance_failure', 'reason': 'Missing required field',
            'evidence': 'fixture artifact failed acceptance', 'previous_selection': previous,
            'previous_outcome': {'request_accepted': True,
                                 'execution_evidence': 'fixture completed turn'}}

    def retry(self, previous=None):
        self.doc['request']['retry'] = {
            'host': 'fixture', 'failed_turn_id': 'fixture-turn', 'verified_request': True,
            'authorization_evidence': 'fixture prior accepted request',
            'request': {'model': 'prior-model',
                        'native_settings': {'effort': 'max', 'speed': 'normal'}}}
        if previous is not None:
            self.doc['request']['retry']['previous_selection'] = previous
            self.doc['request']['retry']['request'] = {
                'model': previous['model'], 'native_settings': previous['native_settings']}
        self.doc['mapping']['settings_keys'].append('speed')

    def test_vendor_native_keys_are_not_translated(self):
        result = self.select()
        self.assertEqual(result['parameters'], {'model': 'compact', 'effort': 'medium'})
        self.assertFalse(result['dispatch_ready'])
        self.assertEqual(result['evidence_level'], 'fixture')
        self.assertEqual(result['execution']['status'], 'not_executed')
        self.doc['mapping']['model_key'] = 'model_id'
        self.assertEqual(self.select()['parameters'], {'model_id': 'compact', 'effort': 'medium'})
        self.doc['mapping']['settings_keys'] = ['thinking']
        self.blocked('unsupported_parameters')

    def test_explicit_compatibility_profile_drives_real_selection(self):
        self.doc['mapping']['settings_keys'] = ['thinking']
        self.doc['policy']['profile'] = 'compatibility-6.1'
        self.doc['catalog']['models'] = [
            candidate('gpt-6.1-terra', 'extraction', {'thinking': 'medium'}),
            candidate('gpt-6.1-sol', 'complex_engineering', {'thinking': 'xhigh'}),
            candidate('gpt-6-luna', 'mechanical_supervision', {'thinking': 'low'})]
        selected = self.module.select(self.doc, now=NOW)
        self.assertEqual(selected['parameters'], {'model': 'gpt-6.1-terra', 'thinking': 'medium'})
        self.doc['workflow']['risk'] = 'critical'
        selected = self.module.select(self.doc, now=NOW)
        self.assertEqual(selected['parameters'], {'model': 'gpt-6.1-sol', 'thinking': 'xhigh'})
        self.doc['workflow']['risk'] = 'normal'
        self.doc['policy']['task_routes']['extract'] = 'mechanical_supervision'
        selected = self.module.select(self.doc, now=NOW)
        self.assertEqual(selected['parameters'], {'model': 'gpt-6-luna', 'thinking': 'low'})

    def test_unknown_or_documented_only_candidates_are_rejected(self):
        for field, value in [('account_available', None), ('host_supported', None),
                             ('resource_scope', 'unknown'), ('capability_evidence', None),
                             ('context', None), ('quality_capabilities', [])]:
            with self.subTest(field=field):
                self.doc = fixture()
                self.doc['catalog']['models'][0][field] = value
                self.blocked('no_eligible_model')
        self.doc = fixture()
        self.doc['catalog']['evidence_kind'] = 'docs'
        self.blocked('account_evidence_required')

    def test_missing_host_tools_or_parallel_are_hard_failures(self):
        self.doc['host']['tools'] = []
        self.blocked('missing_tools')
        self.doc = fixture()
        self.doc['workflow']['requires_parallel'] = True
        self.assertEqual(self.blocked('parallel_unavailable')['fallback'], 'serial')
        self.doc = fixture()
        self.doc['host']['explicit_model'] = False
        self.blocked('explicit_model_unavailable')

    def test_pin_never_silently_substitutes(self):
        self.doc['request']['pinned_model'] = 'missing'
        self.blocked('pinned_model_unavailable')
        self.doc['request']['pinned_model'] = 'compact'
        self.doc['request']['native_settings'] = {'effort': 'medium'}
        selected = self.select()
        self.assertTrue(selected['user_pin'])
        self.escalation(selected)
        self.blocked('pinned_model')

    def test_allowlist_and_verified_new_candidates(self):
        self.doc['policy']['candidate_authority'] = 'explicit_allowlist'
        self.blocked('no_eligible_model')
        self.doc['policy']['allowed'] = [{'id': 'compact', 'native_settings': {'effort': 'medium'}}]
        self.assertEqual(self.select()['model'], 'compact')
        self.doc['policy']['allowed'][0]['native_settings'] = {'effort': 'high'}
        self.blocked('no_eligible_model')

    def test_stale_and_future_catalog_need_refresh(self):
        self.doc['catalog']['expires_at'] = '2030-01-01T00:00:00Z'
        self.assertEqual(self.blocked('catalog_stale')['state'], 'refresh_required')
        self.doc['catalog']['observed_at'] = '2031-01-01T00:00:00Z'
        self.blocked('catalog_stale')

    def test_unknown_or_stale_cost_cannot_satisfy_hard_cap(self):
        self.doc['policy']['max_cost'] = {'amount': 3, 'currency': 'USD', 'unit': 'credit',
                                         'provider': 'fixture', 'window': 'monthly'}
        self.blocked('cost_unknown')
        self.doc['catalog']['models'][0]['cost'] = {
            **self.doc['policy']['max_cost'], 'amount': 2, 'source': 'fixture',
            'observed_at': '2030-01-01T00:00:00Z', 'expires_at': '2030-01-01T12:00:00Z'}
        self.blocked('cost_unknown')
        self.doc['catalog']['models'][0]['cost']['expires_at'] = '2030-01-03T00:00:00Z'
        self.assertEqual(self.select()['model'], 'compact')
        self.doc['catalog']['models'][0]['cost']['unit'] = 'million_input_tokens'
        self.blocked('cost_unknown')

    def test_comparable_cost_only_and_profile_fallback(self):
        other = candidate('other', 'extraction', {'effort': 'medium'})
        self.doc['catalog']['models'].append(other)
        for model, amount in [(self.doc['catalog']['models'][0], 5), (other, 2)]:
            model['cost'] = {'amount': amount, 'currency': 'USD', 'unit': 'request',
                             'provider': 'fixture', 'window': 'on-demand', 'source': 'fixture',
                             'observed_at': '2030-01-01T00:00:00Z',
                             'expires_at': '2030-01-03T00:00:00Z'}
        self.assertEqual(self.select()['model'], 'other')
        other['cost']['unit'] = 'subscription_credit'
        self.assertEqual(self.select()['model'], 'compact')
        self.doc['policy']['automatic_substitution'] = False
        self.doc['catalog']['models'][0]['account_available'] = False
        self.blocked('substitution_disabled')

    def test_quality_requires_evidence_and_stops_after_two_upgrades(self):
        first = self.select()
        self.escalation(first)
        second = self.select()
        self.assertEqual((second['model'], second['quality_attempt']), ('capable', 1))
        self.escalation(second)
        third = self.select()
        self.assertEqual((third['model'], third['quality_attempt']), ('review', 2))
        self.escalation(third)
        self.assertEqual(self.blocked('quality_limit')['state'], 'owner_review')
        self.escalation(first)
        self.doc['request']['quality_escalation']['previous_outcome']['execution_evidence'] = ''
        self.blocked('invalid_input')
        self.doc['request']['quality_escalation']['reason_kind'] = 'shell_error'
        self.blocked('invalid_input')

    def test_exact_retry_bypasses_stale_missing_catalog_and_retains_history(self):
        first = self.select()
        self.escalation(first)
        second = self.select()
        second['native_settings']['speed'] = 'normal'
        second['parameters']['speed'] = 'normal'
        self.doc['request']['quality_escalation'] = None
        self.retry(second)
        self.doc['catalog']['models'] = []
        self.doc['catalog']['expires_at'] = '2000-01-01T00:00:00Z'
        self.doc['policy']['max_cost'] = {'amount': 0}
        result = self.select()
        self.assertEqual(result['parameters'], {'model': 'capable', 'effort': 'high', 'speed': 'normal'})
        self.assertEqual(result['quality_attempt'], 1)
        self.assertEqual(result['quality_history'], second['quality_history'])
        self.assertEqual(result['execution']['status'], 'not_executed')

    def test_retry_cannot_drop_parameters_change_host_or_override_pin(self):
        self.retry()
        self.doc['mapping']['settings_keys'] = ['effort']
        self.blocked('unsupported_parameters')
        self.doc['mapping']['settings_keys'].append('speed')
        self.doc['request']['retry']['host'] = 'another-host'
        self.blocked('retry_host_mismatch')
        self.doc['request']['retry']['host'] = 'fixture'
        self.doc['request']['pinned_model'] = 'different-model'
        self.blocked('retry_pin_conflict')

    def test_retry_unknown_quality_history_blocks_later_escalation(self):
        self.retry()
        result = self.select()
        self.assertIsNone(result['quality_attempt'])
        self.doc['request']['retry'] = None
        self.escalation(result)
        self.blocked('quality_history_unknown')

    def test_retry_without_ordinary_catalog_still_preserves_original_request(self):
        self.retry()
        self.doc['catalog'] = None
        self.assertEqual(self.select()['parameters'], {
            'model': 'prior-model', 'effort': 'max', 'speed': 'normal'})
        self.doc['request']['retry'] = None
        self.blocked('catalog_stale')

    def test_source_backed_hard_stop_and_mutually_exclusive_modes(self):
        self.retry()
        self.doc['request']['stop'] = {'reason': 'Access revoked', 'evidence': 'fixture account receipt'}
        self.blocked('hard_stop')
        self.doc['request']['stop'] = None
        self.escalation({'quality_attempt': 0})
        self.blocked('conflicting_modes')

    def test_schema_rejects_typos_collision_and_invalid_numeric_values(self):
        self.doc['mapping']['settings_keys'] = ['model']
        self.blocked('invalid_mapping')
        self.doc = fixture()
        self.doc['policy']['typo'] = True
        self.blocked('invalid_input')
        self.doc = fixture()
        self.doc['catalog']['models'][0]['context'] = True
        self.blocked('invalid_input')

    def test_replay_history_and_previous_payload_cannot_be_mismatched(self):
        first = self.select()
        self.retry(first)
        self.doc['request']['retry']['request']['model'] = 'different'
        self.blocked('retry_history_mismatch')
        self.doc = fixture()
        self.escalation(first)
        self.doc['request']['quality_escalation']['previous_selection']['parameters']['effort'] = 'other'
        self.blocked('quality_evidence_required')

    def test_false_acceptance_and_no_progress_cannot_escalate(self):
        first = self.select()
        self.escalation(first)
        self.doc['request']['quality_escalation']['previous_outcome']['request_accepted'] = False
        self.blocked('invalid_input')
        self.escalation(first)
        self.doc['policy']['quality_steps']['extraction'] = 'extraction'
        self.blocked('quality_endpoint')

    def test_cli_is_read_only_and_returns_native_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'input.json'
            path.write_text(json.dumps(self.doc), encoding='utf-8')
            prof = Path(tmp)/'profile.json'
            prof.write_text(json.dumps(profile()), encoding='utf-8')
            before = {p.name:p.read_bytes() for p in Path(tmp).iterdir()}
            result = subprocess.run([sys.executable, '-B', str(SCRIPT), str(path),
                                     '--profile', str(prof), '--now', NOW.isoformat()],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['parameters'], {'model': 'compact', 'effort': 'medium'})
            self.assertEqual(before, {p.name:p.read_bytes() for p in Path(tmp).iterdir()})

    def test_cli_quality_and_retry_envelopes_and_bad_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path, prof, envelope = (directory/n for n in ['input.json', 'profile.json', 'envelope.json'])
            prof.write_text(json.dumps(profile()), encoding='utf-8')
            first = self.select()
            self.escalation(first)
            envelope.write_text(json.dumps(self.doc['request']['quality_escalation']), encoding='utf-8')
            self.doc['request']['quality_escalation'] = None
            path.write_text(json.dumps(self.doc), encoding='utf-8')
            command = [sys.executable, '-B', str(SCRIPT), str(path), '--profile', str(prof), '--now', NOW.isoformat()]
            selected = subprocess.run(command + ['--escalate-from', str(envelope)], capture_output=True, text=True)
            self.assertEqual(selected.returncode, 0, selected.stderr)
            self.assertEqual(json.loads(selected.stdout)['parameters'], {'model': 'capable', 'effort': 'high'})
            self.retry()
            envelope.write_text(json.dumps(self.doc['request']['retry']), encoding='utf-8')
            self.doc['request']['retry'] = None
            path.write_text(json.dumps(self.doc), encoding='utf-8')
            replay = subprocess.run(command + ['--retry-from', str(envelope)], capture_output=True, text=True)
            self.assertEqual(json.loads(replay.stdout)['parameters'], {
                'model': 'prior-model', 'effort': 'max', 'speed': 'normal'})
            path.write_text('{broken', encoding='utf-8')
            bad = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertIsNone(json.loads(bad.stdout)['parameters'])


if __name__ == '__main__':
    unittest.main()
