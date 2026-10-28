# Work records

Use this guidance when the user requests work records or synchronization with an authorized record system.
The [host adapter](host-adapters.md) establishes the target schema, owner identity, available API, and operation permissions.
This skill does not supply a personal timeline backend, collector, importer, or automatic synchronization.
The record owner controls writes. Keep ongoing implementation and authorized delivery independent of record preparation.

## Scope and evidence

Keep user-configured project inclusion and exclusion rules in private configuration.
Include evidenced formal work across the selected projects, including team and skill maintenance when in scope.
Do not publish a particular user's exclusions. A formal game or entertainment business can be included under another user's policy.
An unknown classification remains pending until the authorized owner resolves it.

Record actual work from bounded, relevant sources. A project directory does not prove work occurred.
A message, engineer assignment, or tool call does not automatically become a separate achievement.
Use a meaningful task or output as the record unit. Keep only the source detail needed for identity and evidence.
Do not collect unrelated private conversations, credentials, or business data outside the authorized scope.

## Identity, status, and manual changes

Use a durable source identity together with the source system, project identity, and task identity.
Keep the source revision and evidence reference for each observed change.
A new revision updates the same logical record or adds a linked historical event. It does not automatically create another achievement.
Repeated input for the same identity and revision must have no additional effect.
Similar titles do not establish identity. Keep records from different projects separate unless evidence establishes that they represent the same task.

Keep overall task status separate from delivery stages and subtask status:

| Dimension | Meaning |
| --- | --- |
| Overall status | Distinguish complete, incomplete, reopened, cancelled, queued, and blocked work. Keep the supporting task revision. |
| Work stage | Distinguish discussion, research, implementation, verification, source push, build, deployment, actual acceptance, and recovery. |
| Historical result | Keep a prior completed or accepted result when a later revision reopens the work. Show the current rework separately. |
| Partial scope | A completed component or recovery step does not establish completion of the full task. |
| Time | Keep unknown dates and work duration unknown. Observation time does not prove the work date or hours spent. |

A source push does not prove deployment. A build does not prove actual acceptance.
Record the observed facts and their limits. Do not convert an old `done` value into completion of a newer revision.
Keep source-observed facts separate from a user's displayed status when the target supports both.

Preserve manual status, notes, priorities, order, additions, and deletion tombstones.
A source update must not silently undo those changes or recreate a deleted record.
On a conflict, read the current target and reconcile the source revision with the manual changes.
Keep unresolved conflicts pending. Do not replace current records with an older snapshot.

## Incremental synchronization

Use an existing authorized scheduler or relevant source-change event when ongoing synchronization is requested.
Use bounded incremental inputs and small batches. Do not add a poller, a model call per message, or repeated full-history scans.
Keep source coverage and successful cursors separate so one unavailable source does not erase another source's valid history.

Before an authorized write:

1. Read the target's current schema, revision, and relevant records.
2. Prepare the smallest identity-based changes within the configured scope.
3. Preserve manual changes and historical evidence.
4. Validate the schema, payload size, unique identities, status, and evidence against the actual target contract.
5. If supported, use a dry run and an expected-revision condition.
6. Apply the authorized changes through the available supported operation.
7. Read back the committed revision and relevant content.
8. After successful validation and readback, record the new successful cursor only for the verified source coverage.

A prepared file, successful dry run, or accepted request alone does not prove that the target contains the records.
On a revision conflict, read and reconcile before another write. Do not overwrite newer work.
On failure or remote unavailability, keep valid history, pending coverage, and the previous successful cursor.
Keep an unprocessed gap pending. Keep the successful cursor before that gap.
Record the failure and supported continuation path. Do not label unavailable coverage complete or change its successful cutoff.
Preserve newer committed records, tombstones, and acknowledgments during recovery.
Keep actual identifiers, paths, source proofs, user scope rules, and synchronization state private as described in [state.md](state.md).
