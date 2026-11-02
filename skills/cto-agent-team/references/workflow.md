# Team workflow

## Responsive intake and independent delivery

Use the CTO chat as the user's continuing intake point. Accept a new request without discarding existing tasks.
Before or at dispatch, find the canonical task record in the private state directory.
If it does not exist, make one.
Keep a stable task ID and the source request reference, when available.
Record the goal, observable acceptance criteria, owning PM, dependencies, and resources.

A practical ID combines the intake date with a short unique suffix. Acknowledge with a short user summary, for example: “任务 TASK-ID 已派给 PM04。” Chinese summaries do not carry a claim of English-standard compliance.

Dispatch a complete handoff to the owning PM, then end the CTO turn without waiting for implementation. Include the task ID, user request, clarifications, goal, scope, explicit product direction, constraints, and observable acceptance. Include prior results, authorization limits, target host and absolute paths, input files, dependencies, exclusive writable resources, and expected evidence. Name the owners of validation, installation or publication, and result delivery. The PM must have enough context and authority to close the task independently. Missing optional details can be resolved by the PM; ask the user a short question only for a necessary decision.

For user-facing work, name the primary task, starting context, useful default, and understandable result. Include a scenario that does not need its author's explanation. The PM and engineer use the [usability baseline](ui-design.md#usability-baseline) for implementation and actual artifact acceptance. Record the kind of walkthrough or research performed and its limits.

Apply [the ASD-STE100 handoff guidance](handoffs.md) to English CTO-to-PM instructions, PM-to-engineer handoffs, and questions for other people. Use both parts of the official standard. Keep the complete task context as labeled data and separate work steps, rather than removing information to shorten a sentence. Record the source issue, terminology decisions, review status, and unresolved checks in private task state. This language check does not grant permission for the action or its recipient.

For applicable frontend work, consider Anthropic Frontend Design and select it, Emil, or both using [the UI handoff requirements](ui-design.md). Include the selected skills and reasons in the handoff. The assigned role must read their actual content and relevant references, then apply and record decisions for the specific interface. Naming a skill alone is not evidence of use. Preserve product requirements, the design system, accessibility, and task speed. Apply the selection to unfinished work without repeating passed acceptance merely because a preference changed.

For coding or code review by any team role, require the assigned role to read and apply the core Ponytail skill and [coding.md](coding.md). Put this requirement in each applicable new or resumed agent handoff. Reuse valid reading evidence within the same context; do not claim all existing chats have loaded it. Mechanical monitoring does not require a fresh skill load on each tick. Include the affected behavior and known callers, existing helpers, required quality checks, and complete acceptance criteria. Record relevant reuse and scope decisions privately. Do not replace a complete implementation with a shorter stub or remove necessary checks to reduce code. UI coding also uses the selected UI guidance.

Select a Superpowers module only when it adds useful guidance to the task. Check its actual source and availability using [coding.md](coding.md). Carry applicable source and compatibility decisions into the handoff. The module does not add permission for an action, a new agent tree, a worktree, or a separate approval process. Preserve existing release ownership and proportional checks.

PMs scope work for their own engineers, read and review shared evidence, repair failures, and complete authorized delivery. Keep implementation details in task evidence and source events. The CTO's user-facing messages stay brief: start acknowledgment, completion with a usable result, or a failure that requires user action. Delegating delivery does not grant new permission for external messages, publication, devices, or purchases.

Multiple independent requests can proceed through their owning PMs in parallel within actual tool and account capacity. Track each task's status, dependencies, write resources, and current owner; a new user message does not replace an earlier task.

For follow-up instructions about the same deliverable, change the same task record. Increase its revision.
Give its PM the change with that revision. This includes clarifications, scope changes, and cancellation.
Give a separate deliverable a new task ID and an applicable parent link.
If the relationship is unclear, preserve existing work and clarify only what affects execution.

## Task-scoped execution context

Keep role identity in the roster, role instructions, and registry. Treat a conversation or agent run as an execution context, not as the role itself. A long-lived PM chat can coordinate work while separate task-scoped contexts handle execution.

For a new independent deliverable, use a fresh execution context by default when the user or organization has authorized it and the host supports it. Do not reuse an old task's execution context only because the same role is assigned. Start without unrelated prior turns where the supported tool permits. Never treat a full-history fork as a fresh context.

Keep persistent role chats for coordination. The team dispatch generator defaults a new task to a task-scoped subagent with `fork_turns: "none"` and a bounded handoff. A dispatch preview is not proof that the tool ran or that an agent started. Continue the exact recorded task context. Verify that its task, role, host, and execution reference match. Use a role chat only when the recorded reference exactly matches that role's registered thread. Use an agent follow-up only with the actual returned agent path. If the context does not match or the host cannot continue it, stop and record the blocker. Never fall back to another role chat. The follow-up tool cannot change model settings; continue with the saved settings or use a supported, authorized escalation route. Do not put arbitrary task notes or unrelated history in a fresh handoff.

For a clarification, correction, recovery, or remaining work under the same task ID, continue the same task and reuse valid evidence. Do not create duplicate workers or repeat side effects. If a long task needs a new context, first save a checkpoint with exact input versions, decisions, active effects, evidence, and next actions.

Keep the handoff in the private canonical task record. Record `context_mode` (`fresh`, `continue`, or `recovery`), execution-context reference, and continuation source where applicable. Keep an uncreated execution-context reference null until the host returns a real reference. Include only the role and task identities, goal, scope, permissions, target paths and input versions, owners and resource locks, accepted facts, evidence pointers, open work, acceptance, necessary rollback and recovery evidence, and explicit model settings needed for the next action. Keep `work_items` limited to the current role's relevant assignment. Read referenced evidence only when needed. Do not copy the old transcript or assume that “ignore old context” removes it.

If the tool, authorization, or account limit does not allow a fresh context, use the authorized assigned role chat with a clear task boundary and record the isolation limit. Preserve historical conversations and task evidence. Record usage only from supported measurements. If task-level input, cache, output, or cost data is unavailable, state that savings are unmeasured; a fresh context can also repeat setup or recovery work.

Use the existing configured clerk for one private task index. Keep one entry per task ID, with concise task/evidence pointers.
The task owner's canonical file is authoritative for scope, owner, status, acceptance, and evidence.
PMs publish material changes, exact task/revision, and evidence pointers through the [shared event path](#asynchronous-progress-events).
Record completion only with the designated owner's acceptance and exact result evidence.
Keep actual user-visible delivery as a separate receipt under that path.

### Keep unfinished work traceable

The task file is the source record. The task index gives references to source records.
A completed chat turn does not establish task completion.

1. Before dispatch, record the request reference and the task ID.
2. For the same deliverable, keep the same task ID.
3. In the existing task record, record each assigned work item and its owner.
4. For unfinished work, record the next action and the responsible role.
5. For a dependency or deliberate delay, record the condition that permits the next action.
6. At intake, restart, or an actual task change, compare the source record with the existing index.
7. During the existing bounded task rotation, include source records absent from the index.
8. Keep the index entry when its source file is missing or unreadable.
9. Record the gap and the responsible role in that entry.
10. Keep completed, canceled, and replaced task references under the existing retention policy.
11. For replaced work, record the replacement reference and the remaining obligations.
12. For duplicate work, use the owner's explicit source and alias references.

The clerk uses the existing index and schedule. The clerk does not accept product results.
An invalid record remains a visible gap. It is not proof that the task does not exist.
If the source identity remains uncertain, keep the gap pending for its owner.

Use a local team status dashboard as part of task intake and PM updates.
Show projects, user tasks, and the current work of subordinate agents from canonical task records.
Before or at dispatch, the owning PM records meaningful assignments under the [work-item and age rules](state.md#task-and-notification-records).
Keep the dashboard's status, source time, and age labels consistent with those records.

Before assigning overlapping files, devices, desktops, applications, or deployment environments, the CTO coordinates order or isolation with the owners. Record which task holds the resource and which is waiting. On cancellation, stop further dependent work through the available task controls, release ownership after checking actual execution, and retain evidence of completed or irreversible actions. Do not report a task cancelled while its worker is still performing it.

## Completion follow-up and notification

When the user requests completion notification, arrange follow-up before ending the CTO turn if an available, authorized monitoring capability can provide it. Discover the current automation tool and schema first. Use the supported follow-up operation on a suitable supervisor. Read [host-adapters.md](host-adapters.md) for host-specific operations. Apply the `mechanical_supervision` route and verify supported settings as described in [model-routing.md](model-routing.md). A prompt label does not configure the model. Check for existing supervision and reuse or update it instead of creating duplicates. Persist its identifier, target chats, and latest wait cursors in private task state. Use supported scheduling tools rather than inventing a background service.

Give the monitor the task ID, owning PM chat, acceptance criteria, private record location, retry executor, and notification owner. Its instructions should read bounded incremental shared events and changed task sources, retain consumed identities, and stay quiet while nothing actionable changes. Required recovery can use minimal runtime-state observations. Use one logical observation pass per cycle with [current target coverage](recovery.md#current-observation-coverage). Missing results can need bounded follow-up queries. Leave actual implementation with suitable agents. Do not use a recurring high-cost CTO loop to supervise this monitor. If the PM can resolve a blocker within its authority, leave the repair with the PM.

Reporting hours and execution constraints are separate.
Continue authorized unfinished tasks, necessary internal handoffs, background work, and required recovery observation before the proactive user-report sending gate.
Outside reporting hours, continue that authorized work. Keep proactive user reports pending under the user's notification policy.
Do not stop the execution pass at its reporting gate while authorized work or required recovery handling remains.
Keep real execution constraints: cancellation, explicit stops, meeting protection, dependencies, single-writer ownership, capacity, and backoff.
No unfinished work means no new work, busy polling, extra paid monitoring, or repeated effects.
Preserve event/result revisions and delivery evidence. Reconcile uncertain delivery before sending again.
Do not infer a new notification exception from a recovery event.

### Asynchronous progress events

Use the [shared document contract](shared-handoffs.md) for routine handoffs.
Each source role writes complete immutable events in its own private directory.
The designated clerk alone writes the shared summary. The canonical task remains authoritative.
The PM reads exact evidence and records acceptance. The CTO reads the summary and necessary exact references.
Do not relay routine progress or completed results through chats.

Keep publication, consumption, acceptance, dispatch, and actual user delivery receipts separate.
Persist event identities and exact source revisions. Reconcile uncertain effects before another attempt.
Continue independently ready authorized work without waiting for report acknowledgments or the whole batch.
Keep genuine serial dependencies and their next eligible action explicit.

Use existing authorized supervision and summary-reading capabilities. Their intervals are host configuration, not a skill guarantee.
Keep unchanged checks quiet. Do not create another monitor or scan full chat histories for routine handoffs.
Necessary dispatch, continuation, and recovery wakeups contain task identity and exact document pointers.
Active recipients read at safe boundaries. Do not interrupt atomic work or wake idle roles for acknowledgments.

Before a proactive user report, read the accepted result and material limitations from exact task evidence.
Apply the user's reporting hours and retain pending delivery outside that window.
Record user-visible delivery only with actual receipt evidence. A published file or internal acceptance does not prove delivery.
Keep one notification owner and one logical monitoring assignment per task.
Remove only completed duties from shared monitoring. Retire a one-time monitor only when no duties remain.
Preserve recovery ownership, backoff, historical settings, and uncertain-send reconciliation from [recovery.md](recovery.md).
If required follow-up is unavailable, record the limit. An ended turn does not schedule another turn.

## Choose and authorize the mode

Determine the user's goal, applicable project instructions, execution environment, existing authorization, and available tools before dispatching. A request to use this skill does not itself authorize creating independent chats or forwarding tasks between them. Reuse prior explicit authorization for CTO-to-PM and PM-to-CS task forwarding; obtain missing authorization before those messages. Only create independent chats when the user requests them. Reuse verified existing chats where suitable.

If the user asks generally for agents, use authorized host delegation when supported. Otherwise, prepare a plan or proceed serially within scope.
Read [host-adapters.md](host-adapters.md) for actual tool names, parameters, and capability limits.

## Execution through host tools

Discover the current host and its actual schemas before dispatch. Find existing workers and verify the target project before authorized creation.
Choose task settings from [model-routing.md](model-routing.md), current capability evidence, and user policy.
Pass supported native parameters explicitly. Preserve pins, active turns, and earlier requests.
If a requested configuration is unavailable, preserve the task and report the actual limit. Do not silently replace it.

Include the role, reporting relationship, goal, permissions, resources, context, selected skills, and acceptance criteria in each handoff.
For initialization, record actual creation and readiness evidence through the shared event path. Do not wake idle roles only for acknowledgments.
Do not have initializing workers write shared state. Record only actual tool-returned identifiers.
Reconcile an unknown creation result before retrying. A role definition is not evidence of a real worker.

PMs read engineer shared events and exact evidence. The CTO reads the clerk's summary and necessary source references.
Use the [shared event path](#asynchronous-progress-events). Retain durable consumed identities.
Use supported bounded runtime observations only when execution or recovery needs them.
Keep independent chats, subagents, readiness, and actual computation distinct. Missing tools do not authorize private API workarounds.

## Coordinate work

### Schedule useful parallel work

Engineer specialties guide assignment but do not prevent suitable work outside a title. Keep five PM teams with ten engineer roles each, and preserve requested models and reasoning. Each PM schedules its own engineers. The CTO coordinates help between teams. Do not impose a fixed one- or two-engineer wave or apply a collaboration-tree limit to independent chats. Follow the current tools and actual account capacity.

Divide authorized work by useful outputs and dependencies. For each item, name its owner, required inputs, deliverable, acceptance criteria, and writable resources. Dispatch independent ready items in parallel, especially those that hold up integration or delivery. For example, release-policy work, candidate preparation, and a skill update can proceed independently when they have different writers and resources. Only the live release switch needs its one activation owner. Public skill source still has one writer.

When any item completes, review its evidence and assign the next ready item to a suitable free engineer. Do not wait for the rest of a wave. Reuse passed checks for unchanged inputs. Add work or repeat a review only when a changed input, a failure, or an unresolved concern justifies it. Do not occupy every role merely to increase the active-chat count.

1. After a work item ends, compare its result with the remaining task acceptance criteria.
2. Keep the parent task open while required work remains.
3. Before continuation, read the current instructions, task revision, and applicable checkpoint.
4. Compare the recorded dependency with its current evidence.
5. If a new result requires owner action, record that action through the existing authorized path.
6. If the owner has an active turn, keep the action pending.
7. When the owner is idle, combine ready authorized actions into one substantive continuation with exact document pointers.
8. Use the existing chat and the exact task and result references.
9. Before another send, resolve any uncertain outcome through the existing receipt procedure.
10. Keep completed effects and valid acceptance evidence.

Normal continuation and model-capacity recovery are different actions.
Task age alone does not authorize a retry, a new assignment, or a status message.
The existing owner, authority, resource, model, and reporting rules apply.

Record active items, ready unassigned items, dependency waits, capacity failures, and completed outputs in private task state. If work must be serial, name the actual shared operation or dependency and the next eligible action. Measure delivery and waiting time only from observed evidence. Chat status does not measure simultaneous model computation. Apply [recovery.md](recovery.md) to capacity failures without changing model settings.

The CTO owns cross-team coordination and the aggregate index; each PM manages only its ten engineers and is responsible for its team's logical registration. Coordinate shared registry writes as described in [state.md](state.md). Engineers do not spawn or dispatch subordinates. Give each task one writer for every shared file, desktop, or application; coordinate dependencies and avoid overwriting others' changes. Read the target project's applicable `AGENTS.md`. For a device, separately establish connection, identity, and task authorization; an organization-wide delegation grant does not authorize all devices.

For each business task, the CTO specifies the goal, target host and absolute path, authorization boundary, completion criteria, and cross-team dependencies. The PM assigns each independent work item to a clear owner with explicit writable resources and acceptance criteria. Engineers return deliverables, the few decisions that changed the output, actual validation results, and unfinished work. The PM compares the actual artifact with the task. The PM accepts it or requests scoped rework before authorized delivery. Skill reading or tests alone do not replace applicable visual or business evidence. Use [UI acceptance guidance](ui-design.md) for visual claims. The CTO reads the shared summary and accepted result for final delivery without keeping the intake turn open. Mechanical event routing does not replace substantive acceptance.

Distinguish role definitions, verified real chats, ready acknowledgments, and currently active computation. Readiness and saved chat existence do not imply permanent availability. Parallel execution depends on platform and account capacity; do not promise simultaneous execution for all roles. When there is no business task, end the turn and do not install background monitoring unless the user requests it.

## Evidence-based improvement

Use an existing task-completion or recurring-failure event. Do not add a periodic optimization monitor. Record a short private item with the observation, source evidence, impact, owner, bounded change, validation, decision, and rollback method. Prefer gaps that lose task state, duplicate effects, or block delivery. Extend an existing reference before creating a duplicate skill. Keep ongoing business work moving.

Match context to the item. Simple extraction needs the supplied material. Implementation needs the relevant callers and selected skill content. Complex work needs the affected cross-system evidence. Mechanical supervision needs bounded status and cursors. Use [task routes](model-routing.md) and approved escalation when the evidence warrants it. Installation, distribution, reading, and application are distinct claims. Reuse valid reading and successful checks for unchanged inputs.

Keep complete logs and large tool payloads in existing private task evidence.
Give a bounded result with exact input/revision references, actual checks, limits, and next action.
Read relevant artifact sections before printing full logs or inventories.
Keep critical facts, unresolved failures, and required acceptance/recovery evidence even when a longer result is necessary.
Use [bounded continuation context](state.md#bounded-continuation-context) when continuing work.

Observe first, then verify a concrete hypothesis with proportional evidence. Mark a change `adopted` after relevant checks support its intended scope. Keep limited runtime evidence under `trial`. Record the scope and remaining uncertainty. If new waiting, duplicate effects, or quality loss appears, retire the trial or roll back to a known useful method. Save current state and evidence first. A rollback must preserve newer sent and acknowledged events.

Use measured elapsed time, waits, rework, defects, tool calls, or usage only when available. Missing values remain unknown. Elapsed time is not server computation. Active chat count, prompt length, and author benchmarks do not establish actual costs or savings. Small samples do not establish a general model or skill ranking. With no new evidence, retain the last decision instead of repeating the evaluation.

For a material open question, use [bounded research](research.md). Its optional role does not change core registration or add a release gate.
Host-specific sources and operations are in [host-adapters.md](host-adapters.md).

## Requested work records

Use [work-recording.md](work-recording.md) for configured scope, revision-based identity, truthful stages, manual overrides, and incremental synchronization.
A record update does not replace task acceptance or delivery. Keep failed source coverage pending and preserve the last successful cursor.

## Browser task handoffs

Carry the user's browser/channel preference, target and identity, exception limits, and observable evidence through CTO-to-PM and PM-to-engineer handoffs.
Keep this context during reassignment, continuation, and automatic model routing, including Terra routes. Read the [browser-channel rules](host-adapters.md#browser-channels).
Browser policy is task context. Do not put it in the selector's model/native-setting parameters or change model settings to enforce it.
Apply the policy to active work at a safe step boundary. Do not interrupt an action or wake idle workers for acknowledgment.
Retain single-writer ownership and user-activity or meeting holds. Record actual use separately from configuration or dispatch coverage.
