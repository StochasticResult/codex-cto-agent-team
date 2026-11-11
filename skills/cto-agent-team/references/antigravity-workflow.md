# Google Antigravity and dual-runtime workflow

Use this reference when running `cto-agent-team` in Google Antigravity or sharing one skill catalog across Codex and Google Antigravity. Keep core organization, acceptance, single-writer ownership, and private state boundaries from [workflow.md](workflow.md) and [state.md](state.md).

## Shared Codex and Antigravity skill topology

Maintain one canonical local skill directory (such as `~/.codex/skills` or `~/.agents/skills`) rather than duplicating third-party skill trees.

- **Global skill sharing:** Register the shared skill root in `~/.gemini/config/skills.json` under `entries` so Google Antigravity discovers the same `SKILL.md` directories that Codex uses.
- **Rules and workspace overrides:** Keep machine-local execution rules in `~/.gemini/config/rules/*.md` and repository-scoped rules or skills in `AGENTS.md`, `GEMINI.md`, or `.agents/`.
- **Tool mapping check:** Shared skills can name Codex-specific tools, plugins, or connectors. Inspect the active Antigravity session's tool declarations first and map each step to its supported Antigravity equivalent before declaring a capability unavailable.

## Antigravity execution primitives

Map team delegation, research, UI verification, and background execution to supported Antigravity tools:

| Operation | Antigravity tool and boundary |
| --- | --- |
| Scoped engineering or PM execution | `invoke_subagent` with `TypeName: "self"`. Use `Workspace: "share"` (worktree-like shared repo) or `"branch"` (isolated clone) when parallel writers edit or build concurrently; keep `"inherit"` for read-only or single-writer work. |
| Read-only codebase survey | `invoke_subagent` with `TypeName: "research"` (read-only sandbox with no network access). Prefer direct `read_file` calls for quick targeted lookups. |
| Live web or local UI verification | `invoke_subagent` with `TypeName: "browser"`. Stage upload files in `<ArtifactDir>/browser_sandbox/uploads/<filename>` and reference images/files in `<ArtifactDir>/browser_sandbox/references/<filename>`. Verify subagent claims against the host's `BROWSER_HOST_FACTS` system receipt before presenting outcomes or screenshots as verified. |
| Visual asset generation | `invoke_subagent` with `TypeName: "image-generator"` when authorized for visual moments or empty states. |
| Same-task continuation | `send_message` targeting the subagent's existing `conversationId`. Reuse the same subagent for follow-up work on that task rather than spawning duplicate workers. |
| Peer board collaboration | Optional `swarm` tool (`add`, `status`, `model`, `kill`) when shared-board parallel execution fits the user's request and quota policy. |
| Reactive background wakeup | `run_command`, `manage_task`, and `schedule` (`DurationSeconds` with `TimerCondition` for one-shot watchdogs, or `CronExpression` with `IsDaemon` for authorized standing watchers). End the turn after launching asynchronous work; never run shell `sleep` polling loops. |

## Execution cadence, progress visibility, and stop-loss

1. **No silent tool chains:** Do not hide ten or more consecutive tool calls inside internal reasoning without user-visible output. Emit a concise 1–2 sentence milestone update after completing localization/diagnosis, before major edits, before test/build runs, or every 3–5 tool calls. When an authorized remote channel (such as Discord) is active, mirror each milestone update in real time rather than posting only the final summary.
2. **Minimal necessary path:** Read, edit, and verify along the shortest direct path that satisfies acceptance. Record unrelated pre-existing warnings briefly without opening side-quest refactors or full-repository scans.
3. **Fast stop-loss:** If the same failure, test error, or environment block persists after 2–3 targeted attempts, stop and report the exact state, evidence, and options to the user instead of looping silently in the background.
4. **Immediate delivery on green mainline:** Once core requirements and directly affected checks pass, deliver the verified result promptly and leave optional follow-up scope to the user.
5. **Complexity-tiered orchestration:**
   - **Single-point or routine change:** Execute directly in the CTO session or dispatch one scoped high-tier subagent without extra ceremony.
   - **Cross-layer concurrency, state machine, or elusive root cause:** Use multi-perspective hypothesis testing and strict root-cause verification before patching.
   - **Large multi-module frontend, backend, and E2E scope:** Decompose into parallel subagent tracks with disjoint write sets, isolated worktrees, and explicit integration acceptance under direct CTO supervision.

## Subagent model floor

Honor the user's subagent model floor in Antigravity:

- Default engineering, architecture, domain localization, and code-review `invoke_subagent` calls to `Model: "inherit"` or `"pro"` unless the user explicitly requests another tier in the current prompt or a host-documented tool rule requires a specific setting that user policy preserves.
- Do not silently downgrade engineering or translation subagents to `flash` or `flash_lite` to save quota.
- On model quota or temporary capacity failure, report the block and apply [recovery.md](recovery.md) rather than switching models on your own or treating a subagent's text reply as authority to change models.

## Process watchdog and advisory resource leases

Use [scripts/agent_guard.py](../scripts/agent_guard.py) (Python 3.11+ standard library) with a private `--lock-dir` inside `<PRIVATE_STATE_DIR>/locks`:

1. **Non-interactive shell PATH recovery:** On Windows non-interactive PowerShell sessions where user/machine `PATH` entries are incomplete, reconstruct `PATH` from `Machine` and `User` environment variables before invoking developer tools.
2. **Bounded process-tree and SSH execution (`run` and `ssh`):**
   - Never run unbounded `ssh` commands with open `stdin` or hang-prone test/browser scripts without explicit wall-clock (`--timeout`) and output-silence (`--idle-timeout`) watchdogs.
   - `agent_guard.py ssh` enforces `-n -o BatchMode=yes -o ConnectTimeout=...` and optional PowerShell `-EncodedCommand` transport; `agent_guard.py run` drains `stdout`/`stderr` on background threads and terminates the full process tree (`taskkill /F /T` on Windows, process-group `SIGKILL` on POSIX) with exit code `124` on timeout.
   - Browser and Node verification scripts must always close browsers/servers in `finally` blocks and exit deterministically.
3. **Advisory file and resource leases (`acquire`, `release`, `locks`):**
   - Before parallel subagents or peer sessions edit shared files, release manifests, or deployment targets, run `python scripts/agent_guard.py --lock-dir "<PRIVATE_STATE_DIR>/locks" acquire --owner "<ROLE>" --task "<TASK_ID>" --ttl 600 "<RESOURCE>"` and `release` when finished.
   - Exit code `2` (`RESOURCE_LOCKED`) blocks overwriting and blind waiting. Coordinate through the CTO/PM or move to a disjoint file or isolated worktree.

## Multi-CTO peer queues and production freeze windows

When the user operates multiple CTO sessions across accounts or profiles (for example, an intake/coordinator CTO and a secondary execution CTO):

- **Shared private queue and inbox:** Coordinate through `<PRIVATE_STATE_DIR>/dispatch/<peer>-queue.json` (`DISPATCHED` -> `IN_PROGRESS` -> `READY_FOR_DEPLOY` -> `COMPLETED`), append-only peer handoff notes (`inbox/to-<peer>.md`), a concise live sync board, isolated per-account `git worktree` directories, and `agent_guard.py` resource leases.
- **Standing daemon queue watcher:** When authorized, the peer CTO can register a `schedule(CronExpression="*/2 * * * *", IsDaemon=True, ...)` watcher on the private dispatch queue and re-mount it after workstation or server restarts.
- **Production release freeze windows:** When user policy defines a production freeze window (for example, prohibiting live production restarts or cutovers before a designated evening hour on weekdays unless the current user prompt explicitly overrides it), complete coding, unit tests, UI verification, and staging builds in isolated worktrees during freeze hours (`READY_FOR_DEPLOY`), then bundle verified branches under one deployment lease during the authorized cutover window while avoiding scheduled background refresh jobs.

## Multi-language UI localization and geometry verification

When localizing technical or operational interfaces across languages:

- **Domain subagent translation:** When user policy forbids machine translation, author and tighten locale dictionaries directly through contextual high-tier AI subagents that preserve domain terminology, identifiers, units, and `{{placeholders}}` verbatim rather than calling machine-translation APIs or blind character-conversion scripts.
- **Zero-shift and zero-overlap geometry gate:** Alongside dictionary key/placeholder parity checks, verify rendered screens across all supported locales to confirm fixed control heights/widths where intended, zero text clipping on stacked diacritics, and zero sibling bounding-box overlap (`rectA` intersecting `rectB` on adjacent `<select>`, `<input>`, `<button>`, or `<label>` controls) across desktop and compact viewports.
