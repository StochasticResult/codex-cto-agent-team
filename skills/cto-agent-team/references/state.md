# Private team state

Use a user-controlled state directory outside the public repository and outside the installed skill directory. The public skill contains only generic rules and a de-identified roster. Keep actual chat IDs, host IDs, runtime state, and local paths private. Never place passwords, keys, or tokens in state; store only references to the user's credential system if needed. Do not copy private operating files or existing chat registries into the public skill.

`scripts/team_state.py` requires Python 3.11 or later and the standard library. It operates locally; it does not connect to a service or create chats. Run it from the skill directory, substituting a private directory and actual tool-returned values:

- `python scripts/team_state.py init --state-dir DIR` initializes `org.json` and `registry.json` from `assets/roster.json`, with 55 PM and CS roles marked `planned` and `unregistered`. The CTO continues in the current chat and is not one of these 55 entries. Optional `--pm-model`, `--engineer-model`, and `--effort` override defaults.
- `python scripts/team_state.py register --state-dir DIR --role ROLE --thread-id ID --host-id HOST --status created|ready` records a verified chat and its status. This version supports UUID thread IDs. Use actual thread and host IDs as evidence; mark `ready` only after a readiness acknowledgment.
- `python scripts/team_state.py validate --state-dir DIR [--require-ready]` checks role hierarchy, duplicates, models, and readiness counts. Ordinary validation permits roles that are not yet created; `--require-ready` requires all 55 subordinate roles to be `ready`. Inspect the command result for details.

The placeholders above describe arguments, not real identifiers or paths. `created` and `ready` are recorded evidence; active execution is a current tool-observed state, not a registry status. The registry's `model` fields and `model_status: requested` are role-registration snapshots. For the explicit compatibility profile, new state defaults to PM Sol / `high` and engineer Terra / `high`. These fields do not track per-task dispatch or prove a current chat configuration. Validation checks snapshot consistency; it cannot prove the backend model, activity, or availability. Use [model-routing.md](model-routing.md) for task configuration.

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
| `dispatches` | Per-item route, reason, policy revision, model, complete native settings, tool outcome, and turn reference where available. Retain earlier requests. |
| `changes`, `evidence`, `result`, `blocker` | Linked clarifications or cancellations, validation evidence, useful result links, and unresolved decisions. |
| `notification` | Requested follow-up, its owner and monitor, cursors, result revision, delivery state, and notification evidence. |

Use task statuses such as `queued`, `ready`, `running`, `review`, `done`, `blocked`, and `cancelled`. Keep the reason for a blocked task and the dependency it is waiting on. Mark `done` only after the designated owner verifies acceptance and authorized delivery. Role registration's `planned/created/ready` statuses describe chats, not business-task progress.

For tasks with independent outputs, keep a small `work_items` list. Record each item's owner, output, dependencies, acceptance, write resources, evidence, and actual state. Distinguish ready but unassigned work from a dependency wait or a capacity failure. Record why a serial item must wait and which event permits it to start. These task records do not change the helper's role-registration schema.

For notification bookkeeping, keep `requested`, `owner`, `monitor_id`, `wait_cursors`, `result_revision`, `key`, `status`, `notified_at`, and `message_ref` where relevant. Suggested notification states are `pending`, `monitoring`, `sending`, `notified`, `unavailable`, and `cancelled`. Store actual tool identifiers only in this private record. When monitoring is unavailable, record the reason instead of recording an imaginary scheduled check. After a notification is verified delivered, retain the result evidence and mark `notified`. Remove that duty; disable a one-time monitor only when no duties remain. Reconcile unknown delivery before retrying.

For shared supervision, retain the supervisor route, requested model and thinking, tool acceptance, configuration readback or verified inheritance, task coverage, and sole retry executor. Keep retry sends and event-delivery keys separate. Record pending, sent, and acknowledged outcomes where available. A model name in a prompt is not evidence of a configured monitor. Remove only completed duties from a shared monitor. Preserve other tasks and follow-up until their own completion. The supervisor's mechanical route does not replace task acceptance or the failed worker's configuration.

Preserve earlier open tasks when a new request arrives. Append changes to their original task and advance its revision; create a different ID for independent work. The CTO owns cross-task resource ordering and the notification index. A saved task is durable context, not evidence of a live scheduler or simultaneous computation.

Keep recovery state in these private records too. Record the recovery owner, task revision, failed turn's verified requested model and effort, failure cause, failed turn ID, recovery-chain attempt count, provider retry-after, next eligible time, pending-send key, tool outcome, and observed resumed turn. Never substitute a new route default for that failed-turn request. Use the chat ID and failed turn ID to identify a retry record. Preserve the chain's backoff across related failed turns. An uncertain send remains pending until the owner reconciles actual chat state. See [recovery.md](recovery.md). The helper does not execute retries or run a scheduler.

## Shared supervisor state

For a separate monitoring integration, preserve unknown fields, unselected tasks, cursors, completed groups, and notification evidence during updates. Apply bounded changes to current state instead of replacing it with an initialization snapshot. Use task/result revisions for completion events and failed-turn identities for retries. Keep group keys tied to member revisions. Record pending before an effect, sent after tool acceptance, and acknowledgment separately. Substantive acceptance stays with the business owner. It does not prevent a supervisor from delivering an accepted result within explicit message authorization.

Use supported concurrency controls for a separately supplied state writer. Check the expected state digest before saving. Cooperative writers should use the same exclusive lock, a temporary file, and atomic replacement. Preserve a backup under the original data's access and retention rules. A stale digest requires rereading and reconciliation. Atomic replacement does not stop a writer that ignores the lock. Remove a stale lock only after confirming that no writer remains active.

Before recovery, save current state. Inspect the backup and preserve newer sent, acknowledged, and notified evidence. Do not blindly restore an older snapshot. These are integration requirements. The public `team_state.py` helper does not implement a supervisor-state patch tool, optimistic concurrency control, or a cross-process lock. Its role registry still requires one serialized writer.

## Decision and resume checkpoints

At an actual turning point in a long task, append a short checkpoint to existing private task evidence. Record the time, input version, decision and reason, evidence pointer, and next unfinished action. Use another append-only entry for a correction so the earlier decision remains traceable. On resume, read the latest applicable checkpoint and confirm its pointers and input versions before continuing. Reuse valid acceptance. Do not create heartbeat logs, require full-transcript reads, add agents, or install a logging service for this method. See the [method source and boundaries](coding.md#consumer-contract-evidence).

## Portable setup and resume

1. Choose explicit paths for the target project, skill directory, and private state directory.
2. Read the target project's applicable instructions.
3. Discover current tools and account capabilities.
4. Before protected operations, establish any missing required credentials or device authorization.
5. Install the CTO skill with its complete supporting folders.
6. Select only the task dependencies that are needed.
7. Validate private role records before dispatch.

For each dependency, retain its repository, skill path, reviewed commit or version, license, file hashes, and compatibility differences privately. Find `skill-installer` through the current skill catalog. Read its actual instructions and use its supported repository/path/ref options within authorization. Preserve licenses and required supporting references, including sibling modules when referenced. Do not run unknown bootstrap scripts or assume a host plugin exists. The linked sources in [coding.md](coding.md) and [ui-design.md](ui-design.md) identify reviewed dependencies. Their installation is separate from this skill.

Preserve existing valid authorization in the project and environment. A local public-repository or temporary-folder check needs no unrelated device credentials. Do not infer credentials, device permission, active processes, or monitor availability from copied state. Confirm only the capabilities and permissions needed for the operation. Copy private records only through an authorized private channel. Keep them outside both the public repository and installed skill. Retain historical requests. Then inspect real chats, task revisions, resources, and notification state before resuming. Reconcile old identifiers against the new host instead of recreating chats or resending effects blindly.

For an isolated local check, install the complete folder into a temporary skill root. Discover its `SKILL.md` and resolve its references. Use a different private path for `init` and `validate`. Synthetic chat IDs can test registration locally, but they are not evidence of real chats. A successful temporary-directory check does not verify another physical device, Codex catalog refresh, credentials, or remote execution. No background scheduler is installed by these steps.

## Separate routing input

The [routing helper](model-routing.md#local-selector) reads a separate seven-part document. It does not modify `org.json` or `registry.json`.
Keep model catalogs, user policy, exact requests, quality history, and actual receipts private. A declared model does not establish account availability.
The v1 role helper retains its existing overrides and validation behavior. It is not a universal host identity registry.
For a host with non-UUID worker IDs, use separate private task records. Do not invent a UUID or claim the helper registered that worker.
Keep optional research-extension records separate from the 55 core entries.
