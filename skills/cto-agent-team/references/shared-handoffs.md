# Shared document handoffs

Use shared private documents for routine results, blockers, evidence, and the next action.
Keep the canonical task authoritative for scope, ownership, status, and acceptance.
Events and the summary give exact references to that source.
A document does not establish acceptance, execution, or user delivery.

## Writers and locations

Select paths in the authorized private state directory. These locations are examples:

- Canonical task: `tasks/TASK-ID.json`, with one designated task owner.
- Source events: `shared/events/ROLE/TASK-ID/EVENT-ID.json`, with one writer for each source role.
- Summary: `shared/STATUS.md`, with one designated clerk as writer.
- Consumption and delivery receipts: separate protected private state, with its designated writer.

All authorized roles can read the shared documents. Read access does not grant write or external publication permission.
Keep actual identifiers, paths, business data, and credentials out of the public skill.
Use credential references in private records. Do not put credentials in events.

## Publish a complete event

Write an event for a real result, material change, blocker, or dispatch.
Do not write an event for every read, tool call, or unchanged observation.

1. Read the current task revision and applicable source evidence.
2. Write a complete temporary file in the event's destination directory.
3. Verify the required fields, evidence paths, and SHA-256 values.
4. Publish the complete file with an atomic operation that cannot replace an existing event.
5. If publication has an uncertain result, read the destination before another attempt.

Keep published events immutable. For a correction, write a new event with a reference to the earlier event.
If the host cannot provide atomic publication, record that limit before a consumer uses the file.
Do not present a partial file as a published event.

Each event contains:

| Field | Content |
| --- | --- |
| Identity | Event ID, task ID, task revision, source role, and event kind. |
| Change | Actual change, current status, observation time, and result revision. |
| Evidence | Exact private artifact paths, SHA-256 values, and applicable source versions. |
| Scope | Verified scope, remaining work, and concrete limits. Keep missing facts unknown. |
| Next step | Next responsible owner, action, and any dependency that permits it. |
| Correction | Earlier event identity when this event corrects or replaces a claim. |

Record the actual engineering host, execution context, output location, and exclusive writable resources when applicable.
A dispatch preview, active PM chat, or copied file does not prove execution or delivery.

## Read, accept, and continue

Active recipients read new documents at safe boundaries. Do not interrupt an atomic operation for a handoff.
Idle recipients need a host wakeup only for ready authorized work or required recovery.
Include the task identity and exact shared document pointers in that wakeup.
Do not send routine progress, completion, or relay reports to the CTO, PM, or clerk chats.
Do not wake roles for acknowledgments.

Persist consumed event identities and exact source revisions through the existing protected state writer.
Keep publication, consumption, task acceptance, dispatch, and actual user delivery receipts separate.
Advance a consumption cursor only for documents actually read. Keep gaps and uncertain effects pending.
Retain earlier receipts during migration. Do not replay historical events or repeat completed effects.

The owning PM compares the artifact with acceptance criteria and records the decision against exact evidence.
The clerk updates the summary from new events and exact references. The clerk does not accept product results.
The CTO reads that summary and necessary exact evidence for cross-team decisions and final user delivery.
Record actual user delivery only with the supported user-visible receipt.
Apply the user's reporting hours to proactive user reports. Continue authorized execution and recovery outside those hours.

After an accepted result, continue independently ready authorized work without waiting for a report receipt or the whole batch.
For a serial dependency, record its concrete resource or input and the condition that permits continuation.
Preserve paused work, cancellation, resource ownership, capacity backoff, and current user authorization.

## Host capability limits

Use the existing authorized supervisor to read bounded incremental events and changed task sources.
A separate configured summary reader can read the summary on its host-supported schedule.
Choose intervals from user policy and actual host capabilities. This skill imposes no fixed interval.
Reuse existing duties and durable cursors. Do not add duplicate monitors, periodic agent acknowledgments, or full-history scans.
Required recovery can use minimal current runtime observations. Chat history is not routine handoff transport.
If scheduling is unavailable, record the continuation limit. An ended turn does not schedule its own return.
These instructions define a document contract. The bundled role helper does not publish events or schedule readers.
