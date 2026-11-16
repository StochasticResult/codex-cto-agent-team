# Claude Code workflow

Use this reference when the CTO session runs in Claude Code (CLI, desktop app, web, or IDE extension). Keep core organization, acceptance, single-writer ownership, and private state boundaries from [workflow.md](workflow.md) and [state.md](state.md). Tool names and fields differ between Claude Code surfaces and versions. Inspect the active session's tool declarations before you use a name from this file.

## Installation and instruction files

- **Personal skill:** Copy the complete skill folder to `~/.claude/skills/cto-agent-team`. Use `.claude/skills/cto-agent-team` for one project. Claude Code loads the skill from its description, or the user starts it with `/cto-agent-team`.
- **One canonical copy:** Claude Code reads its own skill locations. It does not read `~/.gemini/config/skills.json`. When Codex or Google Antigravity share another directory, update both copies from the same source revision and record that revision. Do not edit one installed copy only.
- **Project rules:** Claude Code reads `CLAUDE.md`. It does not read `AGENTS.md` unless `CLAUDE.md` imports it, for example with an `@AGENTS.md` line. When the target project has only `AGENTS.md`, read that file directly and apply it. Do not change the project's instruction files without authorization.
- **Optional role agents:** [assets/claude-agents](../assets/claude-agents) has two subagent definitions. Copy them to `~/.claude/agents/` or `.claude/agents/` when the user wants named team roles. New definitions load in the next session. The built-in general-purpose subagent is sufficient when they are absent.
- **Helpers:** Run the three scripts with the available shell tool. On Windows, the Bash tool is Git Bash and PowerShell is a separate tool; use the syntax of the tool you call.

## Role topology in Claude Code

A subagent starts with only the prompt it receives. It cannot see the CTO conversation. A subagent usually cannot start its own subagents. Thus a three-level CTO, PM, and engineer tree of nested subagents is not available. Use one of these two shapes and record which one applies:

1. **Collapsed tree (default).** The CTO session dispatches engineer subagents directly. The CTO session does the owning PM's scoping before dispatch, and a separate PM-review subagent or the CTO session does acceptance. Keep the owning PM in the task record so that ownership and evidence stay traceable.
2. **PM sessions.** When the user requests independent chats, each PM is its own Claude Code session and dispatches its own engineer subagents. Use the host's session tool, or separate `claude` processes in separate worktrees. Create sessions only with that user request.

Do not present the collapsed tree as 55 running workers. Role definitions, started subagents, and actual computation stay separate claims.

## Execution primitives

Map team operations to the tools the session exposes:

| Operation | Claude Code tool and boundary |
| --- | --- |
| Scoped engineering | The subagent tool (`Agent`, in some versions `Task`) with a complete handoff. A new subagent is the fresh, no-history task context that [workflow.md](workflow.md#task-scoped-execution-context) asks for. |
| Full-history fork | A `fork` subagent inherits the whole conversation. It is not a fresh context. Use it only when the task needs that history. |
| Read-only survey | A read-only search subagent such as `Explore`. For a known file or a small lookup, read it directly. |
| Parallel writers | One subagent per disjoint write set. Use worktree isolation (`isolation: "worktree"` where supported) when two writers build or edit the same repository. Add `agent_guard.py` leases for shared files outside one worktree. |
| Same-task continuation | Send a message to the existing subagent with its returned identifier. Do not start a duplicate worker for the same task. |
| Background work | Subagents and shell commands that run in the background report on completion. Start them, give a short acknowledgment, and end the turn or continue independent work. Do not run `sleep` polling loops. |
| Independent PM or task chats | The host's session tool, only when the user requests separate sessions. A session needs a brief that stands alone. |
| Scripted fan-out | A deterministic multi-agent workflow tool, only when the user explicitly requests that scale. |
| Follow-up and schedules | Scheduled tasks, cron entries, or self-paced wakeups where the session exposes them and the user authorized them. If none exist, save a checkpoint and state the limit. |
| User-visible progress | The session's task-list tool shows progress to the user. It is not the canonical task record. |

Send independent tool calls together in one message so that they run concurrently. A message that starts several subagents at once is the normal way to schedule parallel engineers.

## Handoffs and acceptance

The handoff prompt is the only context a subagent has. Put the fields from [workflow.md](workflow.md#responsive-intake-and-independent-delivery) in it: task ID and revision, role, goal, scope, absolute paths, input versions, permissions, exclusive write resources, selected skills to read, acceptance, and expected evidence. Give file paths instead of pasted file contents. State what is already ruled out.

A subagent's final report goes to the CTO session, not to the user. It is that subagent's claim, not proof. Before acceptance:

1. Read the diff or the produced artifact.
2. Run the checks that the change affects, or read the exact output of the checks the subagent ran.
3. Record acceptance in the task record, then give the user a short result.

A subagent that receives a hypothesis tends to confirm it. For review, give the reviewer the code and the acceptance criteria, not the author's conclusion.

Write [shared events](shared-handoffs.md) for work that continues across sessions or must survive context compaction. A short single-session task can keep its evidence in the task record only; record that choice.

## Models and effort

The `compatibility-6.1` profile names models of another vendor. It does not apply to Claude Code, and its role snapshots are not Claude model identifiers. This package asserts no equivalence between vendors' model tiers or effort words.

- Leave the subagent's model unset, or use `inherit`, so that it runs on the session model. This is the default.
- Use a model alias (`opus`, `sonnet`, `haiku`, or another alias the tool lists) only when user policy or a subagent definition names it.
- Do not move engineering, review, or translation work to a smaller model to save quota without the user's instruction.
- Set an effort override only when the user or project instructions request one. Do not pass `reasoning_effort` or another vendor's field.
- `model_route.py` does not emit Claude Code tool parameters. To use the selector, make a private routing input for a Claude consumer with its verified `mapping` keys, as [model-routing.md](model-routing.md#local-selector) describes.
- Record the requested model and the tool result. Tool acceptance does not prove the backend model.

On a temporary capacity failure, apply [recovery.md](recovery.md). Do not change the model on your own.

## Permissions and authorization

Subagent tool calls run under the session's permission mode. A denied call is the user's decision; change the approach instead of repeating the call. Keep these as separate confirmations unless the user gave durable authorization: push, publication, external messages, deletion, production changes, and account or settings changes. A plan the user approved covers its listed steps only.

Use plan mode for a large or unclear request before dispatch. Ask the user only for a decision that the request, the code, and sensible defaults cannot settle.

## State, memory, and compaction

- **Private state directory:** Keep task records, the registry, leases, and events there, outside the repository and outside `~/.claude/skills`. `team_state.py register` accepts UUID thread IDs only. Keep a subagent or session identifier of another form in the task record's execution-context reference.
- **Memory:** Where the session has a persistent memory directory, use it for durable user preferences, such as the instruction to operate as CTO and the location of the private state directory. Do not store task status, credentials, or evidence there.
- **Compaction:** A long CTO conversation is summarized by the host. Before a long dispatch wave, write the task record and a [resume checkpoint](state.md#decision-and-resume-checkpoints). After compaction or in a new session, read the task index first. Do not rely on conversation recall for open tasks.

## Remote intake

When the user steers the session from another device, keep CTO turns short: acknowledge, dispatch background work, and end the turn so that the next request can arrive. Send a finished file to the user with the host's file-delivery tool where one exists. Apply the user's reporting hours to proactive reports only.

## Process watchdog and resource leases

Use [scripts/agent_guard.py](../scripts/agent_guard.py) with a private `--lock-dir`, as [antigravity-workflow.md](antigravity-workflow.md#process-watchdog-and-advisory-resource-leases) describes. The same rules apply in Claude Code:

- Run hang-prone tests, browser scripts, and `ssh` through `agent_guard.py run` or `agent_guard.py ssh` with `--timeout` and `--idle-timeout`. The shell tool also has its own timeout; a command that can exceed it must run in the background.
- Acquire a lease before a subagent or peer session edits a shared file, release manifest, or deployment target. Exit code `2` (`RESOURCE_LOCKED`) blocks the write. Coordinate through the CTO or move to a disjoint file.
- Worktree isolation prevents edit collisions inside one repository. It does not protect a shared device, a deployment target, or a file outside the worktree. Use a lease for those.

## Browser work

Follow the [browser-channel rules](host-adapters.md#browser-channels). In Claude Code, the browser extension that acts in the user's own browser and a built-in preview browser are different channels with different sign-in state. Use the channel the user selected. An observation in the built-in preview does not satisfy an acceptance that names the user's signed-in browser. A browser subagent's claim needs the same corroboration as any other subagent report.

## Optional hooks

Hooks in the Claude Code settings file run commands on session and tool events. The harness runs them, not the model. A hook can refresh a shared skill copy at session start or block a write that has no lease. Install a hook only when the user requests it, and record its location. This package ships none.

## Cadence and stop-loss

The cadence rules in [antigravity-workflow.md](antigravity-workflow.md#execution-cadence-progress-visibility-and-stop-loss) apply: short visible milestones, the minimal necessary path, a report after two or three failed attempts at the same failure, and prompt delivery when the main line is verified. Dispatch one subagent, or none, for a routine single-point change. A subagent costs a handoff in each direction; do not delegate a check that takes a few direct tool calls.
