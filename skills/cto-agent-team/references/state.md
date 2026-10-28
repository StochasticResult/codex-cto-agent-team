# Private team state

Use a user-controlled state directory outside the public repository and outside the installed skill directory. The public skill contains only generic rules and a de-identified roster. Keep actual chat IDs, host IDs, runtime state, and local paths private. Never place passwords, keys, or tokens in state; store only references to the user's credential system if needed. Do not copy private operating files or existing chat registries into the public skill.

`scripts/team_state.py` requires Python 3.11 or later and the standard library. It operates locally; it does not connect to a service or create chats. Run it from the skill directory, substituting a private directory and actual tool-returned values:

- `python scripts/team_state.py init --state-dir DIR` initializes `org.json` and `registry.json` from `assets/roster.json`, with 55 PM and CS roles marked `planned` and `unregistered`. The CTO continues in the current chat and is not one of these 55 entries. Optional `--pm-model`, `--engineer-model`, and `--effort` override defaults.
- `python scripts/team_state.py register --state-dir DIR --role ROLE --thread-id ID --host-id HOST --status created|ready` records a verified chat and its status. Use a valid UUID thread ID and host ID returned by the tool as evidence; mark `ready` only after a readiness acknowledgment.
- `python scripts/team_state.py validate --state-dir DIR [--require-ready]` checks role hierarchy, duplicates, models, and readiness counts. Ordinary validation permits roles that are not yet created; `--require-ready` requires all 55 subordinate roles to be `ready`. Inspect the command result for details.

The placeholders above describe arguments, not real identifiers or paths. `created` and `ready` are recorded evidence; active execution is a current tool-observed state, not a registry status. The registry's `model` fields and `model_status: requested` are role-registration snapshots. New state defaults to PM Sol / `high` and engineer Terra / `high`. These fields do not track per-task dispatch or prove a current chat configuration. Validation checks snapshot consistency; it cannot prove the backend model, activity, or availability. Use [model-routing.md](model-routing.md) for task configuration.

Existing private snapshots remain valid when defaults change. Do not rewrite historical requests to match new defaults. `validate` reads them without migration. Repeated `init` retains a compatible organization and rejects a different requested configuration. For an older snapshot, keep using `validate`; if repeating `init`, supply its original overrides, such as `--effort xhigh` for an earlier all-xhigh snapshot. This does not change any chat.

Each PM is responsible for its own team's logical records and any team-specific files. The helper uses the shared `registry.json`, so the CTO must coordinate one writer and serialize all helper operations that modify it; the helper does not provide a cross-process lock. Verify an unknown creation outcome before registering or retrying.

## Task and notification records

The helper manages role registration only. It does not create task tickets, dispatch work, schedule follow-up, or send notifications. The CTO or designated PM maintains small task records separately, for example `tasks/TASK-ID.json` inside the same private state directory. These records and their evidence must remain outside the public repository and installed skill. Use one writer per record and serialize shared-index updates.

Each independent request needs a unique ID. A useful record contains:

| Field | Purpose |
| --- | --- |
| `id`, `revision`, `objective`, `acceptance` | Stable identity, changes, goal, and observable completion conditions. |
| `owner_pm`, `status`, `depends_on` | Responsible PM, progress, and dependencies on other task IDs. |
| `target`, `write_resources`, `lease_owner` | Authorized host and paths, shared resources, and current exclusive owner. |
| `authorization`, `handoff` | Existing user authorization and limits, context, input files, and final delivery responsibility. |
| `dispatches` | Per-item route, reason, policy revision, model, thinking, tool outcome, and turn reference where available. Retain earlier requests. |
| `changes`, `evidence`, `result`, `blocker` | Linked clarifications or cancellations, validation evidence, useful result links, and unresolved decisions. |
| `notification` | Requested follow-up, its owner and monitor, cursors, result revision, delivery state, and notification evidence. |

Use task statuses such as `queued`, `ready`, `running`, `review`, `done`, `blocked`, and `cancelled`. Keep the reason for a blocked task and the dependency it is waiting on. Mark `done` only after the designated owner verifies acceptance and authorized delivery. Role registration's `planned/created/ready` statuses describe chats, not business-task progress.

For tasks with independent outputs, keep a small `work_items` list. Record each item's owner, output, dependencies, acceptance, write resources, evidence, and actual state. Distinguish ready but unassigned work from a dependency wait or a capacity failure. Record why a serial item must wait and which event permits it to start. These task records do not change the helper's role-registration schema.

For notification bookkeeping, keep `requested`, `owner`, `monitor_id`, `wait_cursors`, `result_revision`, `key`, `status`, `notified_at`, and `message_ref` where relevant. Suggested notification states are `pending`, `monitoring`, `sending`, `notified`, `unavailable`, and `cancelled`. Store actual tool identifiers only in this private record. When monitoring is unavailable, record the reason instead of recording an imaginary scheduled check. After a notification is verified delivered, retain the result evidence and mark `notified`. Remove that duty; disable a one-time monitor only when no duties remain. Reconcile unknown delivery before retrying.

For shared supervision, retain the supervisor route, requested model and thinking, tool acceptance, configuration readback or verified inheritance, task coverage, and sole retry executor. Keep retry sends and event-delivery keys separate. Record pending, sent, and acknowledged outcomes where available. A model name in a prompt is not evidence of a configured monitor. Remove only completed duties from a shared monitor. Preserve other tasks and follow-up until their own completion. The supervisor's mechanical route does not replace task acceptance or the failed worker's configuration.

Preserve earlier open tasks when a new request arrives. Append changes to their original task and advance its revision; create a different ID for independent work. The CTO owns cross-task resource ordering and the notification index. A saved task is durable context, not evidence of a live scheduler or simultaneous computation.

Keep recovery state in these private records too. Record the recovery owner, task revision, failed turn's verified requested model and effort, failure cause, failed turn ID, recovery-chain attempt count, provider retry-after, next eligible time, pending-send key, tool outcome, and observed resumed turn. Never substitute a new route default for that failed-turn request. Use the chat ID and failed turn ID to identify a retry record. Preserve the chain's backoff across related failed turns. An uncertain send remains pending until the owner reconciles actual chat state. See [recovery.md](recovery.md). The helper does not execute retries or run a scheduler.
