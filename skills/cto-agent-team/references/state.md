# Private team state

Use a user-controlled state directory outside the public repository and outside the installed skill directory. The public skill contains only generic rules and a de-identified roster. Keep actual chat IDs, host IDs, runtime state, and local paths private. Never place passwords, keys, or tokens in state; store only references to the user's credential system if needed. Do not copy private operating files or existing chat registries into the public skill.

`scripts/team_state.py` requires Python 3.11 or later and the standard library. It operates locally; it does not connect to a service or create chats. Run it from the skill directory, substituting a private directory and actual tool-returned values:

- `python scripts/team_state.py init --state-dir DIR` initializes `org.json` and `registry.json` from `assets/roster.json`, with 55 PM and CS roles marked `planned` and `unregistered`. The CTO continues in the current chat and is not one of these 55 entries. Optional `--pm-model`, `--engineer-model`, and `--effort` override defaults.
- `python scripts/team_state.py register --state-dir DIR --role ROLE --thread-id ID --host-id HOST --status created|ready` records a verified chat and its status. Use a valid UUID thread ID and host ID returned by the tool as evidence; mark `ready` only after a readiness acknowledgment.
- `python scripts/team_state.py validate --state-dir DIR [--require-ready]` checks role hierarchy, duplicates, models, and readiness counts. Ordinary validation permits roles that are not yet created; `--require-ready` requires all 55 subordinate roles to be `ready`. Inspect the command result for details.

The placeholders above describe arguments, not real identifiers or paths. `created` and `ready` are recorded evidence; active execution is a current tool-observed state, not a registry status. Validation checks requested model settings but cannot prove the backend actually resolved a model, that a chat is active, or that it remains online.

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
| `changes`, `evidence`, `result`, `blocker` | Linked clarifications or cancellations, validation evidence, useful result links, and unresolved decisions. |
| `notification` | Requested follow-up, its owner and monitor, cursors, result revision, delivery state, and notification evidence. |

Use task statuses such as `queued`, `ready`, `running`, `review`, `done`, `blocked`, and `cancelled`. Keep the reason for a blocked task and the dependency it is waiting on. Mark `done` only after the designated owner verifies acceptance and authorized delivery. Role registration's `planned/created/ready` statuses describe chats, not business-task progress.

For notification bookkeeping, keep `requested`, `owner`, `monitor_id`, `wait_cursors`, `result_revision`, `key`, `status`, `notified_at`, and `message_ref` where relevant. Suggested notification states are `pending`, `monitoring`, `sending`, `notified`, `unavailable`, and `cancelled`. Store actual tool identifiers only in this private record. When monitoring is unavailable, record the reason instead of recording an imaginary scheduled check. After a notification is verified delivered, retain the result evidence, mark `notified`, and clear or disable the one-time monitor. Reconcile unknown delivery before retrying.

Preserve earlier open tasks when a new request arrives. Append changes to their original task and advance its revision; create a different ID for independent work. The CTO owns cross-task resource ordering and the notification index. A saved task is durable context, not evidence of a live scheduler or simultaneous computation.
