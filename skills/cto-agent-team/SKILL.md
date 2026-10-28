---
name: cto-agent-team
description: Coordinate a reusable CTO, product manager, and engineering team when a user requests this organizational workflow or its ongoing operation.
---

# CTO agent team

Coordinate a CTO, five product managers (PMs), and ten engineers (CS) per PM. The CTO assigns work, resolves cross-team dependencies, and delivers the result; each PM scopes and reviews its team's work; engineers execute assigned work and return evidence. Consult `assets/roster.json` for the role definitions.

Honor the user's task, permissions, and any applicable `AGENTS.md` in the target project. Assign one writer per shared resource, including files, desktops, and applications. The CTO coordinates conflicts across teams. Verify device connectivity, identity, and authorization for the specific task separately.

Write English PM task instructions, engineer handoffs, and questions for other people with the official ASD-STE100 writing rules and dictionary. Read [handoffs.md](references/handoffs.md) before drafting or checking this text. Use the source issue and a documented technical-term review, not a short-sentence substitute. Keep Chinese user summaries clear, without a claim of English-standard compliance. Distinguish a draft, a checked text, and verified compliance. State missing checks and review limits.

Default PMs to `gpt-6.1-sol` with `xhigh` reasoning and engineers to `gpt-6.1-terra` with `xhigh`; accept user overrides. If a requested model is unavailable, report the limitation rather than silently substituting another model.

User authorization for internal delegation and message forwarding is required; reuse prior explicit authorization. Skill selection alone does not authorize creation of independent chats. Create independent chats only when the user requests them; preferentially reuse verified existing chats. For a general request for agents, use collaboration only when authorized and available, or plan the work first. Read [workflow.md](references/workflow.md) when establishing or operating the team, dispatching, or collecting results.

Keep the CTO chat available for new requests. Give each independent request a unique private task record, goal, acceptance criteria, and owning PM. Dispatch a complete handoff, briefly acknowledge the start, and end the CTO turn without waiting for implementation. PMs continue through implementation, review, and authorized delivery in their own chats. Preserve every open task when new requests arrive; attach changes or cancellations to the original task. Coordinate shared resources before parallel work.

Keep detailed progress in PM chats and notify the user briefly when a result is ready, or when a failure needs their action. When completion follow-up is requested, use an available, authorized thread heartbeat or automation, reuse existing monitoring, and keep unchanged checks quiet. Save cursors and notification state privately, verify the result before notifying, and disable a one-time monitor after delivery. If monitoring is unavailable, explain the limit instead of implying that an ended turn will wake itself. The workflow reference describes handoffs and notification recovery; the state helper does not implement scheduling.

Keep actual chat and host identifiers, task and notification records, runtime evidence, and local paths in a private state directory outside both the public repository and the installed skill directory. Never put credentials in state; use credential references. Read [state.md](references/state.md) when initializing, registering, or validating private state. A roster defines roles; it does not establish real chats, readiness, or active execution.
