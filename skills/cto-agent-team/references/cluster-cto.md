# Cluster CTO across hosts

Use this reference when the user runs more than one agent host on the same product, for example Claude Code, Codex, and one or more Google Antigravity instances, and wants one CTO to control all of them. Keep single-writer ownership, acceptance, and private state boundaries from [workflow.md](workflow.md) and [state.md](state.md).

## Why a shared board

The hosts have no interface to call each other. A CTO session in one host cannot start or wake an agent in another host. The only channel that all hosts have is a local folder that each of them can read and write. [scripts/cluster.py](../scripts/cluster.py) keeps a task board in that folder. It needs Python 3.11 or later and only the standard library.

One host is the cluster CTO. The other hosts are members. A member is still the CTO of its own subagents; the cluster CTO decides what each host works on.

## Board folder

Make one private folder outside every public repository and outside every installed skill folder. Each host account must have read and write permission for it. A sandboxed host can have read-only access; check this before you depend on that host.

Put a `policy.json` in the folder. Start from [assets/cluster-policy.example.json](../assets/cluster-policy.example.json). Then select the folder in one of two ways:

- Set the `CLUSTER_DIR` environment variable to the folder.
- Copy `cluster.py` into the folder. The script uses its own folder when a `policy.json` is next to it.

The script makes these subfolders. Do not edit them by hand; the commands lock the board and write each file atomically.

| Folder | Contents | Writer |
| --- | --- | --- |
| `tasks/` | One JSON file per task, with its history | CTO and the assignee, through commands |
| `status/` | One file per agent: current work, files, next step | That agent |
| `capacity/` | One file per agent: remaining usage, state, model tiers | That agent |
| `inbox/<agent>/` | Unread messages; read messages move to `read/` | Any agent |

Give each running instance its own agent name in `policy.json`. Two instances of the same host under different accounts are two agents, for example `antigravity-a` and `antigravity-b`.

## Commands

Each command names the caller: `python cluster.py --agent NAME COMMAND`.

| Command | Use |
| --- | --- |
| `poll` | Show what needs this agent's attention. It prints `NOTHING` when there is none. |
| `wait --interval 10 --timeout 3600` | Block with no model call until new work or a message arrives, then print it and exit. |
| `board` | Show each agent's capacity and current work, and all open tasks. |
| `route --type T --tier TIER` | Show which agent a new task would go to, without making a task. |
| `task new --title --goal --accept ... --type --tier --project --paths ...` | Make a task. The CTO can add `--assign NAME`; the default is automatic routing. |
| `task claim`, `task done --result --evidence`, `task block`, `task release` | The assignee moves its task. |
| `task accept`, `task rework --note`, `task assign --to`, `task cancel` | The CTO only. |
| `task note ID "text"`, `task show ID`, `task list [--all]` | Notes and reading. |
| `status --doing "..." --task ID --files ... --next "..."` | Tell the other agents what you are doing. |
| `capacity --remaining N --state ok\|low\|exhausted\|paused --tier heavy=MODEL:EFFORT` | Report usage and model tiers. |
| `msg send --to NAME\|all [--task ID] "text"`, `msg read` | Messages between agents. |

Task states: `open` (no assignee), `assigned`, `in_progress`, `review` (submitted to the CTO), `rework`, `blocked`, `done`, `cancelled`.

## Central change control

Give every member these rules in its host's always-on instruction file:

1. Do not change the product without a task on the board. This includes code, configuration, and releases.
2. When the user gives a direct instruction in a member's session, the member first records it with `task new --assign` and its own name. The command prints a warning when the task's write paths overlap another open task. On a warning, stop and send a message to the CTO.
3. A member does not decide architecture, data structures, external interfaces, dependencies, or the release method. It sends the options and a recommendation to the CTO and continues with unaffected work. The CTO records each decision in one decisions file in the board folder. Members read that file before they start.
4. Write only the files in the task's `paths`. Propose other work with `task new` and no assignee.
5. Only a task of type `release` permits a release. Keep one release owner at a time, and keep the user's freeze windows.
6. Run `poll` at the start of each session and on each scheduled wakeup. Update `status` at milestones. Submit with `task done` and real evidence: files changed, commands, and actual output.

The script trusts `--agent`. These permissions are a convention between cooperating agents, not a security boundary.

## Routing by capacity, model, and effort

Each agent reports its own capacity. No agent guesses for another agent.

- `--remaining` is the percentage of usage that remains. An agent that cannot read it reports only `--state`.
- `--state exhausted` means a rate limit or an empty quota. `--state paused` means the user told the cluster not to use that agent. Only the user's instruction removes `paused`.
- Each `--tier` gives the model and effort that the agent uses for `heavy`, `standard`, or `light` work. The names are that host's own names. This package asserts no equivalence between vendors' models or effort words.

For a new task, the script reads the order for the task's type from `type_preferences`, or `default_order`. It skips an agent that is `exhausted` or `paused`, or that has less than `min_remaining_pct`. It puts an agent with capacity data older than `capacity_stale_hours` after agents with fresh data, and it moves an agent with three or more unfinished tasks to the end. The task then gets the `model` and `effort` of the selected agent's tier. The assignee uses those settings, or writes the settings it actually used in its `task claim` note. The user's explicit choice of an agent overrides routing.

List an agent in `unmetered` when the user states that its quota is not a constraint. Routing then ignores that agent's remaining percentage and the age of its report. A reported `exhausted` or `paused` state still stops it.

The order in `type_preferences` is the user's policy. The example file is a starting point, not a measured ranking.

## Wakeups

A message does not wake an agent. Use two mechanisms, with the user's authorization.

**Background wait (fast).** Run `wait` as a background command in a host that wakes its agent when a background command exits. The script reads the board at each interval and makes no model call, so a short interval such as 10 seconds costs no quota. It exits when there is new work, a message, or, for the CTO, a task to review or assign. Tasks that the agent already holds do not end the wait. After the agent handles the output, it starts the wait again. Keep one wait for each agent. Confirm on each host that the exit of a background command does wake the agent; if it does not, that host has only the scheduled check.

**Scheduled check (fallback).** Each host also keeps a scheduled check that runs `poll` and starts the wait again when it is not running:

- Claude Code: a scheduled task where the session exposes one.
- Google Antigravity: a `schedule` daemon, as [antigravity-workflow.md](antigravity-workflow.md) describes.
- Codex: an automation or thread heartbeat.

On `NOTHING`, the check ends quietly. With a running wait, the delay between agents is about the wait interval; without it, the delay equals the scheduled interval. The board is for assignment and handoff, not for conversation. Each host application must be running for its check to start.

## CTO duties

- Read `board` before dispatch. Make tasks with a goal, observable acceptance criteria, type, tier, project path, and write paths.
- For a task in `review`, read the actual diff or artifact and the check output. Then use `task accept` or `task rework`. A member's `result` text is a claim, not proof.
- For a stale task, send a message first. Reassign only when the member cannot continue.
- Keep user reports short: start, accepted result, and decisions that need the user.

## Limits

- No file in the board folder can contain a password, key, or token.
- Usage that a host does not expose to its agent stays unknown until the agent meets a limit or the user enters it.
- Each scheduled check uses some quota.
- This is a local, single-machine board. Hosts on other machines need a shared or synchronized folder, which this package does not supply.
