# Task model routing

Separate the task, host capabilities, model evidence, user policy, native mapping, requested settings, and execution evidence.
The [host adapter](host-adapters.md) establishes actual supported operations. The local selector does not discover accounts or send work.
Use only supported capabilities and the user's authorized resource scope. Keep explicit pins and hard budgets.
Apply changes on the next authorized dispatch. Preserve active work, account settings, subscriptions, and historical requests.

## Local selector

`scripts/model_route.py` requires Python 3.11 or later and only the standard library.
It reads the seven-part [input schema](../assets/routing.schema.json) and returns JSON on standard output.
The bundled schema reader implements only the keywords used by this schema. It is not a general JSON Schema engine.

An offline example needs no credentials:

```sh
python scripts/model_route.py assets/routing.example.json --now 2030-01-02T00:00:00Z
```

This example has synthetic availability and an explicit fixture pin. Its result has `evidence_level: fixture` and `dispatch_ready: false`.
The fixed date is for this fixture only. Real work uses the current time.
Keep real input, profiles, selected requests, and receipts in the [private state directory](state.md#separate-routing-input).

1. Make a private copy of the example.
2. Record the task's tools, context requirement, quality requirements, complexity, risk, and acceptance.
3. Record the current host and its actual parameter schema.
4. Replace fixture evidence with supported read-only discovery or relevant actual-work records.
5. Record the user's policy, candidate authority, profile, cost constraints, and any explicit pin.
6. Use the selector with that input.
7. Examine the decision and its evidence limits before authorized dispatch.
8. Keep the actual tool outcome separately.

| Input | Meaning |
| --- | --- |
| `workflow` | Task kind, tools, context, quality requirements, complexity, risk, and parallel requirement. |
| `host` | Current identity/version, tools, execution modes, explicit model control, persistence, and notification capability. |
| `catalog` | Source, observation and expiry times, evidence kind, account availability, capability evidence, supported settings, and route support. |
| `policy` | User authority, exact allowlist or verified-existing-resource rule, task routes, profile, budgets, and bounded quality steps. |
| `mapping` | One consumer's model key and exact supported native setting keys, with a schema evidence reference. |
| `request` | Explicit pin, native settings, quality escalation, capacity retry, or a source-backed hard stop. |
| `execution` | Separate recorded request acceptance and actual execution evidence. Selection never fills these as completed. |

The helper evaluates supplied references. It cannot establish that an account assertion is true.
A documentation-only catalog cannot establish account availability. A stale catalog returns `refresh_required` for ordinary selection.
A fixture remains a fixture even when its availability values are true.
For ordinary work, `dispatch_ready` means the supplied configuration passed these gates. It is not tool acceptance or backend verification.

`explicit_allowlist` permits only listed model/native-setting combinations.
`verified_existing_resources` permits evidenced candidates in the current host and existing account/resource scope when user policy grants that authority.
Adding a catalog entry alone does not grant permission. Unknown availability, tools, context, or required quality capability prevents selection.
Use `request.pinned_model` for a user model pin. An unavailable pin returns a blocked result and never selects another model.

Use `--profile PATH` for a private preference profile with `id` and `routes`.
Each route contains a preferred `model` and exact `native_settings`.
The built-in `compatibility-6.1` profile is loaded only when explicitly selected by policy.
A complex or critical task uses the `complex_engineering` route. Other task kinds use `policy.task_routes`.
The model must have supported settings for the route and satisfy the task's capabilities.

Reliable costs can order candidates only when currency, unit, provider, and billing window match.
A cost record needs `amount`, `currency`, `unit`, `provider`, `window`, `source`, `observed_at`, and `expires_at`.
A hard `max_cost` needs an amount and the same four basis fields. Unknown, stale, or incomparable costs cannot satisfy it.
Without a hard cap, unknown costs require `allow_unknown_cost: true` and do not establish savings.
When costs cannot be compared, use the explicit profile preference or the single eligible configuration.
If neither resolves the choice, return `owner_review`. Never rank models by their names or release dates.
`automatic_substitution: false` retains the profile preference. It blocks another choice when that preference is unavailable.
API token prices and subscription credits are different units. This package does not convert them or run paid comparisons.

Exit code 0 means a configuration was selected, including a fixture. Exit code 2 means no executable selection was returned.
Blocked decisions have no parameters. A serial or manual fallback does not satisfy a hard parallel requirement.
Missing execution tools require manual work or planning through the [host workflow](host-adapters.md#execution-operations).
The helper does not create workers, update models, install an IDE, or schedule follow-up.

## Bounded quality escalation

Use `--escalate-from PATH` with an object containing `reason_kind`, `reason`, `evidence`, `previous_selection`, and `previous_outcome`.
The previous outcome must have `request_accepted: true` and nonempty `execution_evidence`.
Keep the complete selector result as `previous_selection`. Its native payload, host, pin state, and quality history must remain consistent.
Permitted reasons are `acceptance_failure`, `repeated_no_progress`, `constraint_conflict`, and `cross_module_complexity`.
A missing environment, configuration error, or single failed shell command is not quality evidence.

The selector follows `policy.quality_steps` and retains the prior request, reason, and outcome in `quality_history`.
It permits at most two quality upgrades, or a smaller user limit. A pin, missing history, endpoint, or unchanged settings requires owner review.
Each upgraded candidate must pass the normal capability, authority, and budget gates. Escalation does not bypass them.

## Capacity retry

Use `--retry-from PATH` with the verified retry envelope:

```json
{
  "host": "HOST_FROM_PRIOR_REQUEST",
  "failed_turn_id": "FAILED_TURN_FROM_EVIDENCE",
  "verified_request": true,
  "authorization_evidence": "PRIVATE_EVIDENCE_REFERENCE",
  "request": {"model": "ORIGINAL_MODEL", "native_settings": {"effort": "ORIGINAL_VALUE"}}
}
```

Include the unchanged previous selector result as `previous_selection` when available. The helper preserves its quality history and count.
Without that history, exact recovery can proceed, but a later automatic quality upgrade is blocked until reconciliation.
All native fields, including supported speed settings, must survive. Unsupported keys block replay rather than being discarded.
The retry host and supplied history must match the verified original request.
Ordinary catalog absence, expiry, or price uncertainty does not replace or revoke that request.
Use `catalog: null` when no ordinary catalog is available for exact retry. Ordinary selection still requires a fresh catalog.
Represent a source-backed revocation or new user hard constraint in `request.stop`, with nonempty `reason` and `evidence`.
A hard stop blocks replay. It does not authorize a substitute.
Quality and retry modes are mutually exclusive. The caller still applies [recovery.md](recovery.md) before sending.
The public schema adds retry host/history, a nullable retry catalog, and this hard-stop field to the reviewed seven-part contract.

## Compatibility profile

These are explicit existing routes, not universal defaults or an account availability claim.
The [profile file](../assets/compatibility-6.1.json) keeps the model names outside core organization instructions.

| Route | Task | Model | Reasoning |
| --- | --- | --- | --- |
| `coordination_research` | Routine PM coordination and research across sources | `gpt-6.1-sol` | `high` |
| `scoped_engineering` | Scoped fixes, UI implementation, visual checks, and computer actions with a clear target | `gpt-6.1-terra` | `high` |
| `extraction` | Simple structured extraction or routine summaries from supplied material | `gpt-6.1-terra` | `medium` |
| `complex_engineering` | Complex coding, architecture, transactions, permissions, critical review, and releases across systems | `gpt-6.1-sol` | `xhigh` |
| `mechanical_supervision` | Routine status checks, deterministic retry bookkeeping, deduplication, and routing completion candidates | `gpt-6-luna` | `low` |

For substantive tasks, escalate within the approved scope when needed:

- For conflicting constraints, a critical decision, or acceptance with high impact, use Sol / `xhigh`.
- For complex state across modules or a substantive acceptance failure, use Sol / `xhigh`.
- For ambiguity in extraction, first use Terra / `high`. For complex analysis, use Sol / `high` or Sol / `xhigh` as appropriate.

Here, Sol means `gpt-6.1-sol` and Terra means `gpt-6.1-terra`. Use the current user policy for candidate authority. A new name alone does not require repeated approval within that authority. If a configuration is unavailable, preserve the task and report the limitation. Do not silently substitute a configuration to obtain capacity.

## Record dispatch and supervision

Pass exact native settings through the current supported tool. Record the route, reason, policy revision, input evidence, request, and outcome.
Tool acceptance does not independently verify the backend model. Retain earlier records and report any observed host fallback.
The old role helper keeps PM Sol/high and engineer Terra/high as registration snapshots. It neither selects nor applies task settings.
Old private snapshots remain valid. Do not migrate or rewrite them to match a new catalog.

Within the compatibility profile, mechanical supervision retains the approved Luna/low route.
Use another host's supervision route only through its supported parameters and authorized policy.
Read back monitor configuration or verify documented inheritance. A prompt label does not configure a model.
If settings cannot be applied or verified, record the limit. Do not add a more expensive workaround or standalone job without authority.
Use bounded status snapshots, saved cursors, and one logical retry/notification owner per task.
Keep unchanged checks quiet. Mechanical routing does not replace substantive acceptance.
The supervisor's route never replaces a failed worker's exact native request or quality history.
