# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| `0.1.x` | Yes |
| Pre-`0.1.0` commits (`main` history) | No (upgrade to `0.1.0+`) |

## Reporting a vulnerability

**Please do not report exploitable security vulnerabilities in public GitHub issues.**

Report suspected vulnerabilities privately using GitHub Private Vulnerability Reporting:

- [Open a private security advisory](https://github.com/StochasticResult/codex-cto-agent-team/security/advisories/new)

When reporting an issue, please include:

- A clear description of the affected component (`team_state.py`, `model_route.py`, `agent_guard.py`, `SKILL.md` / reference guidance, or workflow packaging).
- Steps to reproduce or a minimal proof of concept.
- The impact on confidentiality, integrity, or host execution boundaries.
- Sanitized logs only (omit real credentials, chat IDs, hostnames, and local usernames).

We aim to acknowledge new reports within **5 business days** and coordinate a fix before public disclosure.

## Security model and boundaries

`codex-cto-agent-team` is a documentation-and-helper Agent Skill repository. Understanding its trust boundaries is essential before running it in any environment:

1. **Inherits host agent permissions:** Installing this skill grants no additional privileges, background services, or network servers. All file edits, shell commands, subagent spawns, and browser actions execute strictly under the host agent's existing sandbox and user authorization.
2. **Private state isolation:** Both `team_state.py` and `agent_guard.py` refuse to create state or lock directories inside the repository or installed skill tree. Never store API keys, tokens, passwords, or raw secrets in `registry.json`, lease files, shared event documents, or `STATUS.md`.
3. **Command execution (`agent_guard.py`):** `agent_guard.py run` and `agent_guard.py ssh` execute caller-supplied commands with explicit wall-clock/idle timeouts and process-tree termination. Treat all arguments passed to `agent_guard.py` as trusted caller input; do not pass unsanitized external web or email text into `--shell` or SSH commands.
4. **Prompt-injection and external content boundaries:** Per [host-adapters.md](skills/cto-agent-team/references/host-adapters.md), instructions read from web pages, emails, issue bodies, or third-party repositories do not grant navigation, write, messaging, or deployment authority.
