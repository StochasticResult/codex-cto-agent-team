# Task model routing

Use these default routes unless the user supplies another policy. Record the user's approved routing scope in private task state. A role title does not restrict which route its task needs.

| Route | Task | Model | Reasoning |
| --- | --- | --- | --- |
| `coordination_research` | Routine PM coordination and research across sources | `gpt-6.1-sol` | `high` |
| `scoped_engineering` | Scoped fixes, UI implementation, visual checks, and computer actions with a clear target | `gpt-6.1-terra` | `high` |
| `extraction` | Simple structured extraction or routine summaries from supplied material | `gpt-6.1-terra` | `medium` |
| `complex_engineering` | Complex coding, architecture, transactions, permissions, critical review, and releases across systems | `gpt-6.1-sol` | `xhigh` |

Escalate within the approved scope when the task needs it:

- For conflicting constraints, a critical decision, or acceptance with high impact, use Sol / `xhigh`.
- For complex state across modules or a substantive acceptance failure, use Sol / `xhigh`.
- For ambiguity in extraction, first use Terra / `high`. For complex analysis, use Sol / `high` or Sol / `xhigh` as appropriate.

Here, Sol means `gpt-6.1-sol` and Terra means `gpt-6.1-terra`. Obtain user approval for a model or reasoning level outside the approved scope. If a configuration is unavailable, preserve the task and report the limitation. Do not silently substitute a configuration to obtain capacity.

## Apply and record the route

Choose the route for each work item. Record its reason, policy revision, requested model, and requested reasoning. For each authorized chat creation or continuation, pass `model` and `thinking` explicitly where the current tool supports them. For collaboration, use the current schema's `model` and `reasoning_effort` fields where supported. Respect fixed role configurations and tool limits. If the tool cannot apply the route, record the limit instead of claiming a switch.

Record the tool outcome and the affected turn when available. Tool acceptance confirms request acceptance; it does not independently verify the backend model. Retain prior dispatch records. Do not restart active turns or wake idle engineers only to change settings. Critical work already in progress keeps its recorded configuration until its next authorized dispatch.

`assets/roster.json` and the state helper use Sol / `high` for PM role defaults and Terra / `high` for engineer role defaults. These are registration snapshots. They do not replace per-task routes or prove that existing chats changed. The helper does not dispatch tasks or apply model settings. Keep per-task request and outcome evidence separately as described in [state.md](state.md).

For a capacity retry, use the failed turn's verified request, even when it differs from a new default. Read [recovery.md](recovery.md). If that request is unknown, reconcile the evidence before sending a retry. Capacity failure is not a reason to escalate, downgrade, or reset a model.

Keep the CTO's current settings, speed, subscription, and budget unchanged. Do not add model trials or paid benchmarks as a release gate. Preserve required acceptance checks. Reuse passed evidence for unchanged inputs.
