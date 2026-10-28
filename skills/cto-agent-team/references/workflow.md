# Team workflow

## Responsive intake and independent delivery

Use the CTO chat as the user's continuing intake point. Accept a new request without discarding existing tasks. For each independent request, create a unique task ID in the private state directory, record the goal and observable acceptance criteria, choose an owning PM, and identify dependencies and resources. A practical ID combines the intake date with a short unique suffix. Acknowledge with a short user summary, for example: “任务 TASK-ID 已派给 PM04。” Chinese summaries do not carry a claim of English-standard compliance.

Dispatch a complete handoff to the owning PM, then end the CTO turn without waiting for implementation. Include the task ID, user request, clarifications, goal, scope, explicit product direction, constraints, and observable acceptance. Include prior results, authorization limits, target host and absolute paths, input files, dependencies, exclusive writable resources, and expected evidence. Name the owners of validation, installation or publication, and result delivery. The PM must have enough context and authority to close the task independently. Missing optional details can be resolved by the PM; ask the user a short question only for a necessary decision.

For user-facing work, name the primary task, starting context, useful default, and understandable result. Include a scenario that does not need its author's explanation. The PM and engineer use the [usability baseline](ui-design.md#usability-baseline) for implementation and actual artifact acceptance. Record the kind of walkthrough or research performed and its limits.

Apply [the ASD-STE100 handoff guidance](handoffs.md) to English CTO-to-PM instructions, PM-to-engineer handoffs, and questions for other people. Use both parts of the official standard. Keep the complete task context as labeled data and separate work steps, rather than removing information to shorten a sentence. Record the source issue, terminology decisions, review status, and unresolved checks in private task state. This language check does not grant permission for the action or its recipient.

For applicable frontend work, consider Anthropic Frontend Design and select it, Emil, or both using [the UI handoff requirements](ui-design.md). Include the selected skills and reasons in the handoff. The assigned role must read their actual content and relevant references, then apply and record decisions for the specific interface. Naming a skill alone is not evidence of use. Preserve product requirements, the design system, accessibility, and task speed. Apply the selection to unfinished work without repeating passed acceptance merely because a preference changed.

For coding or code review by any team role, require the assigned role to read and apply the core Ponytail skill and [coding.md](coding.md). Put this requirement in each applicable new or resumed agent handoff. Reuse valid reading evidence within the same context; do not claim all existing chats have loaded it. Mechanical monitoring does not require a fresh skill load on each tick. Include the affected behavior and known callers, existing helpers, required quality checks, and complete acceptance criteria. Record relevant reuse and scope decisions privately. Do not replace a complete implementation with a shorter stub or remove necessary checks to reduce code. UI coding also uses the selected UI guidance.

Select a Superpowers module only when it adds useful guidance to the task. Check its actual source and availability using [coding.md](coding.md). Carry applicable source and compatibility decisions into the handoff. The module does not add permission for an action, a new agent tree, a worktree, or a separate approval process. Preserve existing release ownership and proportional checks.

PMs scope work for their own engineers, collect and review evidence, repair failures, and complete authorized delivery in their own chats. Keep implementation details and routine progress there. The CTO's user-facing messages stay brief: start acknowledgment, completion with a usable result, or a failure that requires user action. Delegating delivery does not grant new permission for external messages, publication, devices, or purchases.

Multiple independent requests can proceed through their owning PMs in parallel within actual tool and account capacity. Track each task's status, dependencies, write resources, and current owner; a new user message does not replace an earlier task. For a clarification, scope change, or cancellation concerning an existing request, update that task and forward the change to its PM with a revision. An unrelated request gets a new task. If the relationship is unclear, preserve existing work and clarify only what affects execution.

Before assigning overlapping files, devices, desktops, applications, or deployment environments, the CTO coordinates order or isolation with the owners. Record which task holds the resource and which is waiting. On cancellation, stop further dependent work through the available task controls, release ownership after checking actual execution, and retain evidence of completed or irreversible actions. Do not report a task cancelled while its worker is still performing it.

## Completion follow-up and notification

When the user requests completion notification, arrange follow-up before ending the CTO turn if an available, authorized monitoring capability can provide it. Discover the current automation tool and schema first. Use the supported follow-up operation on a suitable supervisor. Read [host-adapters.md](host-adapters.md) for host-specific operations. Apply the `mechanical_supervision` route and verify supported settings as described in [model-routing.md](model-routing.md). A prompt label does not configure the model. Check for existing supervision and reuse or update it instead of creating duplicates. Persist its identifier, target chats, and latest wait cursors in private task state. Use supported scheduling tools rather than inventing a background service.

Give the monitor the task ID, owning PM chat, acceptance criteria, private record location, retry executor, and notification owner. Its instructions should read bounded task status or wait snapshots with saved cursors, advance the private record, and stay quiet while nothing actionable changes. Check each shared PM only once per cycle. Leave actual implementation with suitable agents. Do not use a recurring high-cost CTO loop to supervise this monitor. If the PM can resolve a blocker within its authority, leave the repair with the PM.

Route a meaningful failure or completed-result candidate to the responsible decision maker. A completion candidate must match the task and result revision and include artifact and acceptance evidence. The mechanical supervisor does not grant final acceptance or take over a release owner. Sending an event to the CTO or another chat requires explicit authorization for that recipient and scope. Preserve that authorization in the handoff. Without it, retain the event privately for authorized collection. Do not send pending, unchanged, or ordinary retry updates.

Before announcing completion, inspect the PM's final result and relevant evidence: acceptance outcome, artifact or repository link, revision or commit where applicable, tests, and material limitations. A completed tool call or an idle chat alone does not establish acceptance. The notification should be concise and include the useful result link or artifact and any necessary limitation.

Use one notification owner and one logical monitoring assignment per task. One shared monitor may serve several tasks. Record a result revision and a notification key so repeated checks of the same result can be skipped. Track retry sends and CTO events separately with pending, sent, and acknowledged evidence where available. After successful delivery to the intended chat, mark the private record `notified` with the result evidence and message reference where available. Remove that completed duty; disable or delete a one-time monitor only when no duties remain. If delivery or the state write has an uncertain outcome, inspect the destination and saved record before retrying; do not blindly resend. If a crash leaves `sending` or an unknown outcome, reconcile it first. Persisted state and serialized ownership reduce duplicates; do not claim transactional exactly-once delivery across tools.

If the required monitoring capability or authorization is missing, say so briefly and record follow-up as unavailable or pending. Offer a concrete supported way to check the task later. Ending a turn does not by itself schedule another turn, and an existing chat is not a permanently running worker. Task and notification records are described in [state.md](state.md); the role helper does not perform this monitoring.

For a confirmed temporary model-capacity failure, use [the recovery workflow](recovery.md). The CTO owns PM recovery and may designate one authorized supervisor as its sole retry executor. The owning PM resumes engineers. The supervisor's route never replaces the failed turn's model, native settings, or quality history. A failed shell command or a quiet chat alone does not establish model-capacity failure. Reuse the task's existing authorized monitor when delayed follow-up is necessary. Do not create competing recovery monitors or notify the user about each ordinary retry.

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
For initialization, request only a readiness acknowledgment with the role and understood responsibility.
Do not have initializing workers write shared state. Record only actual tool-returned identifiers.
Reconcile an unknown creation result before retrying. A role definition is not evidence of a real worker.

The PM collects engineer results, and the CTO collects PM results through the host's supported result operation.
Use saved cursors where available. Keep waits bounded. A dispatch does not authorize a subordinate to send another chat a reply.
Keep independent chats, subagents, readiness, and actual computation distinct. Missing tools do not authorize private API workarounds.

## Coordinate work

### Schedule useful parallel work

Engineer specialties guide assignment but do not prevent suitable work outside a title. Keep five PM teams with ten engineer roles each, and preserve requested models and reasoning. Each PM schedules its own engineers. The CTO coordinates help between teams. Do not impose a fixed one- or two-engineer wave or apply a collaboration-tree limit to independent chats. Follow the current tools and actual account capacity.

Divide authorized work by useful outputs and dependencies. For each item, name its owner, required inputs, deliverable, acceptance criteria, and writable resources. Dispatch independent ready items in parallel, especially those that hold up integration or delivery. For example, release-policy work, candidate preparation, and a skill update can proceed independently when they have different writers and resources. Only the live release switch needs its one activation owner. Public skill source still has one writer.

When any item completes, review its evidence and assign the next ready item to a suitable free engineer. Do not wait for the rest of a wave. Reuse passed checks for unchanged inputs. Add work or repeat a review only when a changed input, a failure, or an unresolved concern justifies it. Do not occupy every role merely to increase the active-chat count.

Record active items, ready unassigned items, dependency waits, capacity failures, and completed outputs in private task state. If work must be serial, name the actual shared operation or dependency and the next eligible action. Measure delivery and waiting time only from observed evidence. Chat status does not measure simultaneous model computation. Apply [recovery.md](recovery.md) to capacity failures without changing model settings.

The CTO owns cross-team coordination and the aggregate index; each PM manages only its ten engineers and is responsible for its team's logical registration. Coordinate shared registry writes as described in [state.md](state.md). Engineers do not spawn or dispatch subordinates. Give each task one writer for every shared file, desktop, or application; coordinate dependencies and avoid overwriting others' changes. Read the target project's applicable `AGENTS.md`. For a device, separately establish connection, identity, and task authorization; an organization-wide delegation grant does not authorize all devices.

For each business task, the CTO specifies the goal, target host and absolute path, authorization boundary, completion criteria, and cross-team dependencies. The PM assigns each independent work item to a clear owner with explicit writable resources and acceptance criteria. Engineers return deliverables, the few decisions that changed the output, actual validation results, and unfinished work. The PM compares the actual artifact with the task. The PM accepts it or requests scoped rework before authorized delivery. Skill reading or tests alone do not replace applicable visual or business evidence. Use [UI acceptance guidance](ui-design.md) for visual claims. The CTO reviews the accepted result for final delivery when the supervisor routes its evidence, without keeping the intake turn open. Mechanical event routing does not replace substantive acceptance.

Distinguish role definitions, verified real chats, ready acknowledgments, and currently active computation. Readiness and saved chat existence do not imply permanent availability. Parallel execution depends on platform and account capacity; do not promise simultaneous execution for all roles. When there is no business task, end the turn and do not install background monitoring unless the user requests it.

## Evidence-based improvement

Use an existing task-completion or recurring-failure event. Do not add a periodic optimization monitor. Record a short private item with the observation, source evidence, impact, owner, bounded change, validation, decision, and rollback method. Prefer gaps that lose task state, duplicate effects, or block delivery. Extend an existing reference before creating a duplicate skill. Keep ongoing business work moving.

Match context to the item. Simple extraction needs the supplied material. Implementation needs the relevant callers and selected skill content. Complex work needs the affected cross-system evidence. Mechanical supervision needs bounded status and cursors. Use [task routes](model-routing.md) and approved escalation when the evidence warrants it. Installation, distribution, reading, and application are distinct claims. Reuse valid reading and successful checks for unchanged inputs.

Observe first, then verify a concrete hypothesis with proportional evidence. Mark a change `adopted` after relevant checks support its intended scope. Keep limited runtime evidence under `trial`. Record the scope and remaining uncertainty. If new waiting, duplicate effects, or quality loss appears, retire the trial or roll back to a known useful method. Save current state and evidence first. A rollback must preserve newer sent and acknowledged events.

Use measured elapsed time, waits, rework, defects, tool calls, or usage only when available. Missing values remain unknown. Elapsed time is not server computation. Active chat count, prompt length, and author benchmarks do not establish actual costs or savings. Small samples do not establish a general model or skill ranking. With no new evidence, retain the last decision instead of repeating the evaluation.

For a material open question, use [bounded research](research.md). Its optional role does not change core registration or add a release gate.
Host-specific sources and operations are in [host-adapters.md](host-adapters.md).

## Requested work records

Use [work-recording.md](work-recording.md) for configured scope, revision-based identity, truthful stages, manual overrides, and incremental synchronization.
A record update does not replace task acceptance or delivery. Keep failed source coverage pending and preserve the last successful cursor.
