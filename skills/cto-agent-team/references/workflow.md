# Team workflow

## Responsive intake and independent delivery

Use the CTO chat as the user's continuing intake point. Accept a new request without discarding existing tasks. For each independent request, create a unique task ID in the private state directory, record the goal and observable acceptance criteria, choose an owning PM, and identify dependencies and resources. A practical ID combines the intake date with a short unique suffix. Acknowledge with a short user summary, for example: “任务 TASK-ID 已派给 PM04。” Chinese summaries do not carry a claim of English-standard compliance.

Dispatch a complete handoff to the owning PM, then end the CTO turn without waiting for implementation. Include the user request and later clarifications, task ID, goal, scope, acceptance criteria, relevant prior results, existing authorization and its limits, target host and absolute paths, file locations, dependencies, exclusive write resources, expected evidence, and who owns final validation, installation or publication, and the result report. The PM must have enough context and authority to close the task independently. Missing optional details can be resolved by the PM; ask the user a short question only for a necessary decision.

Apply [the ASD-STE100 handoff guidance](handoffs.md) to English CTO-to-PM instructions, PM-to-engineer handoffs, and questions for other people. Use both parts of the official standard. Keep the complete task context as labeled data and separate work steps, rather than removing information to shorten a sentence. Record the source issue, terminology decisions, review status, and unresolved checks in private task state. This language check does not grant permission for the action or its recipient.

PMs scope work for their own engineers, collect and review evidence, repair failures, and complete authorized delivery in their own chats. Keep implementation details and routine progress there. The CTO's user-facing messages stay brief: start acknowledgment, completion with a usable result, or a failure that requires user action. Delegating delivery does not grant new permission for external messages, publication, devices, or purchases.

Multiple independent requests can proceed through their owning PMs in parallel within actual tool and account capacity. Track each task's status, dependencies, write resources, and current owner; a new user message does not replace an earlier task. For a clarification, scope change, or cancellation concerning an existing request, update that task and forward the change to its PM with a revision. An unrelated request gets a new task. If the relationship is unclear, preserve existing work and clarify only what affects execution.

Before assigning overlapping files, devices, desktops, applications, or deployment environments, the CTO coordinates order or isolation with the owners. Record which task holds the resource and which is waiting. On cancellation, stop further dependent work through the available task controls, release ownership after checking actual execution, and retain evidence of completed or irreversible actions. Do not report a task cancelled while its worker is still performing it.

## Completion follow-up and notification

When the user requests completion notification, arrange follow-up before ending the CTO turn if an available, authorized monitoring capability can provide it. Discover the current automation tool and schema first; prefer a thread heartbeat for follow-up on this chat, unless the user requested a standalone job. Check for an existing monitor for the task and reuse or update it instead of creating duplicates. Persist its identifier, target chats, and latest wait cursors in private task state. Use supported scheduling tools rather than inventing a background service.

Give the monitor the task ID, owning PM chat, acceptance criteria, private record location, and notification owner. Its instructions should read bounded task status or wait snapshots with saved cursors, advance the private record, and stay quiet while nothing actionable changes. It may notify on a verified completion, a meaningful failure, or required user action. Do not ask it to post routine status on every run. If the PM is blocked but can resolve the issue within its authority, leave the repair with the PM.

Before announcing completion, inspect the PM's final result and relevant evidence: acceptance outcome, artifact or repository link, revision or commit where applicable, tests, and material limitations. A completed tool call or an idle chat alone does not establish acceptance. The notification should be concise and include the useful result link or artifact and any necessary limitation.

Use one notification owner and one monitor per task. Record a result revision and a notification key so repeated checks of the same result can be skipped. After successful delivery to the intended chat, mark the private record `notified` with the result evidence and message reference where available, then disable or delete its one-time monitor. If delivery or the state write has an uncertain outcome, inspect the destination and saved record before retrying; do not blindly resend. If a crash leaves `sending` or an unknown outcome, reconcile it first. Persisted state and serialized ownership reduce duplicates; do not claim transactional exactly-once delivery across tools.

If the required monitoring capability or authorization is missing, say so briefly and record follow-up as unavailable or pending. Offer a concrete supported way to check the task later. Ending a turn does not by itself schedule another turn, and an existing chat is not a permanently running worker. Task and notification records are described in [state.md](state.md); the role helper does not perform this monitoring.

## Choose and authorize the mode

Determine the user's goal, applicable project instructions, execution environment, existing authorization, and available tools before dispatching. A request to use this skill does not itself authorize creating independent chats or forwarding tasks between them. Reuse prior explicit authorization for CTO-to-PM and PM-to-CS task forwarding; obtain missing authorization before those messages. Only create independent chats when the user requests them. Reuse verified existing chats where suitable.

If the user asks generally for agents, use collaboration only where it is authorized and supported; otherwise produce a plan. When collaboration is selected, discover its current tools and schemas. Where supported, pass the requested `model`, `reasoning_effort`, and `fork_turns="none"` with full task context. Respect applicable platform limits; do not treat a particular child-agent limit as a global independent-chat limit.

## Independent chats

Discover the available thread tools and their actual schemas before calling them; do not assume a tool namespace. Before creating a chat, list projects and use the actual appropriate project identifier. Specify the chosen `model` and `thinking` explicitly for each PM and engineer. A user may override the default models or effort. If the requested configuration is unavailable, report the failure and preserve the task; do not silently replace it.

Each creation prompt should include role, reporting relationship, task goal, permissions, assigned resources, relevant context, and acceptance criteria. For role initialization, request only a reply containing READY, role number, reporting manager, and understood responsibility; do not have the 55 initializing chats write shared state. Record only real identifiers returned by the tool. If a creation outcome is unknown, inspect actual chats and private registration before retrying to avoid duplicates. A configured role or attempted creation is not proof of successful registration. If the independent-chat tools are unavailable, report the limitation; do not use private shell APIs as a workaround.

After authorized task forwarding, when wait_threads is available, each PM reads its engineers' results and the CTO reads PM results through that tool. A dispatch message alone does not authorize a subordinate to send a message back to another chat. Group waits within the current schema's target limit, continue with returned cursors, and keep each wait to at most 60 seconds under this team's convention. Report actual status and evidence rather than assuming a chat is running.

## Coordinate work

The CTO owns cross-team coordination and the aggregate index; each PM manages only its ten engineers and is responsible for its team's logical registration. Coordinate shared registry writes as described in [state.md](state.md). Engineers do not spawn or dispatch subordinates. Give each task one writer for every shared file, desktop, or application; coordinate dependencies and avoid overwriting others' changes. Read the target project's applicable `AGENTS.md`. For a device, separately establish connection, identity, and task authorization; an organization-wide delegation grant does not authorize all devices.

For each business task, the CTO specifies the goal, target host and absolute path, authorization boundary, completion criteria, and cross-team dependencies. The PM assigns a single engineer with explicit writable resources and acceptance criteria. The engineer returns deliverables, actual validation results, and unfinished work; the PM accepts the work or requests rework and closes authorized delivery. The CTO or its authorized completion monitor reviews the final evidence for the user's result notification without keeping the intake turn open.

Distinguish role definitions, verified real chats, ready acknowledgments, and currently active computation. Readiness and saved chat existence do not imply permanent availability. Parallel execution depends on platform and account capacity; do not promise simultaneous execution for all roles. When there is no business task, end the turn and do not install background monitoring unless the user requests it.

Useful references: [Build skills](https://learn.chatgpt.com/docs/build-skills) and [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
