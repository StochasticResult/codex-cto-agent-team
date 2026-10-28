#!/usr/bin/env python3
"""Read local evidence and return a routing decision. Never send a request.

The schema reader supports only the keywords in the bundled input schema.
It is not a general JSON Schema implementation or an account discovery tool.
"""
import argparse
import copy
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

ASSETS = Path(__file__).resolve().parent.parent / 'assets'
TYPES = {'object': dict, 'array': list, 'string': str, 'boolean': bool,
         'null': type(None), 'integer': int, 'number': (int, float)}


def validate(value, schema, path='$'):
    """Validate the fixed, local schema subset; no remote references or code."""
    kinds = schema.get('type', [])
    kinds = [kinds] if isinstance(kinds, str) else kinds
    if kinds and not any(isinstance(value, TYPES[k]) and
                         not (k in ('number', 'integer') and isinstance(value, bool))
                         for k in kinds):
        raise ValueError(f'{path}: invalid type')
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f'{path}: nonfinite value')
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        raise ValueError(f'{path}: invalid constant')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path}: invalid choice')
    if isinstance(value, dict):
        if set(schema.get('required', [])) - set(value):
            raise ValueError(f'{path}: missing required fields')
        properties = schema.get('properties', {})
        extra = schema.get('additionalProperties', True)
        for key, item in value.items():
            if key in properties:
                validate(item, properties[key], f'{path}.{key}')
            elif extra is False:
                raise ValueError(f'{path}: unexpected field {key}')
            elif isinstance(extra, dict):
                validate(item, extra, f'{path}.{key}')
    elif isinstance(value, list):
        for index, item in enumerate(value):
            validate(item, schema.get('items', {}), f'{path}[{index}]')
    elif isinstance(value, str) and len(value) < schema.get('minLength', 0):
        raise ValueError(f'{path}: empty value')
    elif type(value) in (int, float):
        if value < schema.get('minimum', -math.inf) or value > schema.get('maximum', math.inf):
            raise ValueError(f'{path}: outside permitted range')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      parse_constant=reject_constant)


def reject_constant(value):
    raise ValueError(f'Nonfinite JSON: {value}')


def instant(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp requires a timezone')
    return result


def fresh(record, now):
    try:
        return instant(record['observed_at']) <= now < instant(record['expires_at'])
    except (ValueError, KeyError, TypeError, AttributeError):
        return False


def present(value):
    return isinstance(value, str) and bool(value.strip())


def stop(reason, state='blocked', fallback='manual'):
    return {'state': state, 'reason': reason, 'fallback': fallback,
            'parameters': None, 'dispatch_ready': False}


def mapped(host, mapping, model, settings):
    keys = mapping['settings_keys']
    if (mapping['host'] != host['id'] or not present(mapping['verified_by'])
            or not present(host['parameter_schema_source'])
            or not present(mapping['model_key']) or len(keys) != len(set(keys))
            or any(not present(key) for key in keys) or mapping['model_key'] in keys):
        return None, 'invalid_mapping'
    if not present(model) or not isinstance(settings, dict) or set(settings) - set(keys):
        return None, 'unsupported_parameters'
    return {mapping['model_key']: model, **settings}, None


def cost_info(value, now):
    if (not isinstance(value, dict) or type(value.get('amount')) not in (int, float)
            or not math.isfinite(value['amount']) or value['amount'] < 0
            or not present(value.get('source')) or not fresh(value, now)):
        return None
    basis = tuple(value.get(k) for k in ('currency', 'unit', 'provider', 'window'))
    return (value['amount'], basis) if all(present(k) for k in basis) else None


def cap_info(value):
    if not isinstance(value, dict) or type(value.get('amount')) not in (int, float):
        return None
    basis = tuple(value.get(k) for k in ('currency', 'unit', 'provider', 'window'))
    if not math.isfinite(value['amount']) or value['amount'] < 0 or not all(present(k) for k in basis):
        return None
    return value['amount'], basis


def result(doc, model, settings, parameters, route, attempt, history, pin, basis):
    catalog = doc['catalog'] or {}
    fixture = catalog.get('evidence_kind') == 'fixture'
    return {'state': 'selected', 'host': doc['host']['id'], 'route': route,
            'model': model, 'native_settings': copy.deepcopy(settings), 'parameters': parameters,
            'quality_attempt': attempt, 'quality_history': copy.deepcopy(history),
            'user_pin': pin, 'selection_basis': basis,
            'evidence_level': ('fixture' if fixture else
                               'verified_request' if basis == 'exact_verified_retry' else 'configured'),
            'dispatch_ready': not fixture,
            'provenance': {'policy_id': doc['policy']['id'],
                           'policy_revision': doc['policy']['revision'],
                           'profile': doc['policy']['profile'],
                           'catalog_source': catalog.get('source'),
                           'catalog_observed_at': catalog.get('observed_at'),
                           'catalog_expires_at': catalog.get('expires_at'),
                           'catalog_used_for_selection': basis != 'exact_verified_retry',
                           'mapping_source': doc['mapping']['verified_by']},
            'execution': {'status': 'not_executed', 'request_accepted': False,
                          'tool_receipt': None, 'actual_model': None,
                          'actual_native_settings': None, 'execution_evidence': None}}


def select(document, *, now=None, profile=None):
    """Evaluate supplied evidence. A selected payload is not proof of execution."""
    now = now or datetime.now(timezone.utc)
    doc = copy.deepcopy(document)
    try:
        validate(doc, read_json(ASSETS / 'routing.schema.json'))
        return decide(doc, now, profile)
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        decision = stop('invalid_input')
        decision['detail'] = str(exc)
        return decision


def decide(doc, now, profile):
    work, host, policy, request = (doc[k] for k in ('workflow', 'host', 'policy', 'request'))
    retry, quality = request['retry'], request['quality_escalation']
    if retry is not None and quality is not None:
        return stop('conflicting_modes')
    if request.get('stop') is not None:
        return stop('hard_stop')
    if not host['explicit_model']:
        return stop('explicit_model_unavailable', fallback='plan_only')
    if set(work['required_tools']) - set(host['tools']):
        return stop('missing_tools', fallback='plan_only')
    if work['requires_parallel'] and not (host['subagents'] or host['independent_chats']):
        return stop('parallel_unavailable', fallback='serial')
    _, mapping_error = mapped(host, doc['mapping'], 'validation-only', {})
    if mapping_error:
        return stop(mapping_error)
    pin = request['pinned_model']
    if retry is not None:
        if not all(present(retry[k]) for k in ('host', 'failed_turn_id', 'authorization_evidence')):
            return stop('retry_evidence_required')
        if retry['host'] != host['id']:
            return stop('retry_host_mismatch')
        original = retry['request']
        if pin is not None and pin != original['model']:
            return stop('retry_pin_conflict')
        if request['native_settings'] and request['native_settings'] != original['native_settings']:
            return stop('retry_settings_conflict')
        params, error = mapped(host, doc['mapping'], original['model'], original['native_settings'])
        if error:
            return stop(error)
        previous = retry.get('previous_selection', {})
        if previous and (previous.get('host') != host['id']
                         or previous.get('model') != original['model']
                         or previous.get('native_settings') != original['native_settings']
                         or previous.get('parameters') != params):
            return stop('retry_history_mismatch')
        # Missing history does not prevent exact recovery, but cannot reset the count.
        attempt = previous.get('quality_attempt')
        if (type(attempt) is not int or not 0 <= attempt <= 2
                or not isinstance(previous.get('quality_history'), list)
                or len(previous['quality_history']) != attempt):
            attempt = None
        return result(doc, original['model'], original['native_settings'], params,
                      previous.get('route'), attempt, previous.get('quality_history'),
                      previous.get('user_pin', pin is not None), 'exact_verified_retry')

    catalog = doc['catalog']
    if not fresh(catalog, now):
        return stop('catalog_stale', 'refresh_required')
    if catalog['evidence_kind'] == 'docs':
        return stop('account_evidence_required', 'refresh_required')
    if not present(catalog['source']) or not present(policy['source']):
        return stop('evidence_required')
    if len({m['id'] for m in catalog['models']}) != len(catalog['models']):
        return stop('ambiguous_catalog')
    route = policy['task_routes'].get(work['task_kind'])
    if work.get('complexity') == 'complex' or work.get('risk') == 'critical':
        route = 'complex_engineering'
    if not present(route):
        return stop('route_not_configured', fallback='plan_only')
    attempt, history = 0, []
    if quality is not None:
        previous = quality['previous_selection']
        if pin is not None or previous.get('user_pin') is True:
            return stop('pinned_model', 'owner_review')
        attempt = previous.get('quality_attempt')
        if type(attempt) is not int or not 0 <= attempt <= 2:
            return stop('quality_history_unknown', 'owner_review')
        if attempt >= min(2, policy['max_quality_attempts']):
            return stop('quality_limit', 'owner_review')
        if (previous.get('state') != 'selected' or previous.get('host') != host['id']
                or not present(previous.get('model')) or not isinstance(previous.get('native_settings'), dict)
                or not isinstance(previous.get('parameters'), dict)
                or previous.get('user_pin') is not False
                or not isinstance(previous.get('quality_history'), list)
                or len(previous['quality_history']) != attempt
                or mapped(host, doc['mapping'], previous['model'], previous['native_settings'])[0]
                != previous['parameters']
                or not present(quality['previous_outcome']['execution_evidence'])):
            return stop('quality_evidence_required', 'owner_review')
        route = policy['quality_steps'].get(previous.get('route'))
        if not route or route == previous.get('route') or not policy['automatic_substitution']:
            return stop('quality_endpoint', 'owner_review')
        attempt += 1
        history = copy.deepcopy(previous.get('quality_history') or [])
        history.append({'previous_model': previous['model'],
                        'previous_native_settings': previous['native_settings'],
                        'previous_route': previous['route'], 'reason_kind': quality['reason_kind'],
                        'reason': quality['reason'], 'evidence': quality['evidence'],
                        'previous_outcome': quality['previous_outcome']})

    if profile is None and policy['profile'] == 'compatibility-6.1':
        profile = read_json(ASSETS / 'compatibility-6.1.json')
    preferred = None
    if profile is not None:
        if profile.get('id') != policy['profile']:
            return stop('profile_mismatch')
        preferred = profile['routes'].get(route)
    choices, parameter_errors, cost_errors = [], [], []
    for model in catalog['models']:
        if pin is not None and pin != model['id']:
            continue
        if (model['host_supported'] is not True or model['account_available'] is not True
                or model['resource_scope'] != 'existing'
                or not present(model['availability_evidence']) or not present(model['capability_evidence'])
                or set(work['required_tools']) - set(model['tools'])
                or model['context'] is None or model['context'] < max(0, work['context_min'])
                or set(work.get('quality_requirements', [])) - set(model['quality_capabilities'])):
            continue
        settings_list = [r['native_settings'] for r in model['route_support'] if r['route'] == route]
        for settings in settings_list:
            if settings not in model['native_settings']:
                continue
            if request['native_settings'] and settings != request['native_settings']:
                continue
            if policy['candidate_authority'] == 'explicit_allowlist' and not any(
                    m['id'] == model['id'] and m['native_settings'] == settings for m in policy['allowed']):
                continue
            params, error = mapped(host, doc['mapping'], model['id'], settings)
            if error:
                parameter_errors.append(error)
                continue
            cost = cost_info(model['cost'], now)
            cap = cap_info(policy['max_cost'])
            if policy['max_cost'] is not None:
                if cap is None or cost is None or cost[1] != cap[1]:
                    cost_errors.append('cost_unknown')
                    continue
                if cost[0] > cap[0]:
                    cost_errors.append('cost_exceeded')
                    continue
            elif cost is None and not policy['allow_unknown_cost']:
                cost_errors.append('cost_unknown')
                continue
            choices.append({'model': model['id'], 'native_settings': settings,
                            'parameters': params, 'cost': cost})
    if not choices:
        reason = (parameter_errors or cost_errors or
                  ['pinned_model_unavailable' if pin is not None else 'no_eligible_model'])[0]
        return stop(reason)
    preferred_choice = next((c for c in choices if preferred and c['model'] == preferred['model']
                             and c['native_settings'] == preferred['native_settings']), None)
    if pin is None and not policy['automatic_substitution'] and not preferred_choice:
        return stop('substitution_disabled')
    comparable = all(c['cost'] is not None for c in choices) and len({c['cost'][1] for c in choices}) == 1
    if comparable and policy['automatic_substitution']:
        choice = min(choices, key=lambda c: (c['cost'][0], c is not preferred_choice))
        basis = 'comparable_recorded_cost'
    else:
        choice = preferred_choice or (choices[0] if len(choices) == 1 else None)
        basis = 'profile_preference_cost_not_ranked' if preferred_choice else 'only_eligible_configuration'
    if choice is None:
        return stop('preference_required', 'owner_review')
    if quality is not None and (choice['model'], choice['native_settings']) == (
            quality['previous_selection']['model'], quality['previous_selection']['native_settings']):
        return stop('quality_no_progress', 'owner_review')
    return result(doc, choice['model'], choice['native_settings'], choice['parameters'],
                  route, attempt, history, pin is not None, basis)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Private routing input, or the shipped offline fixture')
    parser.add_argument('--profile', help='Explicit local preference profile')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--retry-from', help='Verified capacity retry envelope as JSON')
    modes.add_argument('--escalate-from', help='Quality reason, previous selection and outcome as JSON')
    parser.add_argument('--now', help='ISO timestamp for deterministic offline fixtures')
    args = parser.parse_args(argv)
    try:
        doc = read_json(args.input)
        if args.retry_from:
            doc['request']['retry'] = read_json(args.retry_from)
        if args.escalate_from:
            doc['request']['quality_escalation'] = read_json(args.escalate_from)
        decision = select(doc, now=instant(args.now) if args.now else None,
                          profile=read_json(args.profile) if args.profile else None)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        decision = stop('invalid_input')
        decision['detail'] = str(exc)
    print(json.dumps(decision, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if decision['state'] == 'selected' else 2


if __name__ == '__main__':
    sys.exit(main())
