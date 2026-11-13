# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-12

First tagged public release establishing formal licensing, CI quality gates, cross-platform helper verification, reproducible offline end-to-end demonstration, and documented host compatibility boundaries.

### Added

- **License & Governance:** Added [LICENSE](LICENSE) (MIT), `license: MIT` in `skills/cto-agent-team/SKILL.md`, [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), `.github/ISSUE_TEMPLATE/` forms (bug report, feature request, use-case feedback), and `.github/PULL_REQUEST_TEMPLATE.md`.
- **CI/CD & Quality Gates:** Added [tests.yml](.github/workflows/tests.yml) (running `validate_repo.py`, `ruff`, `mypy`, and cross-platform `unittest` + demo across Ubuntu, Windows, and macOS on Python 3.11–3.13), [release.yml](.github/workflows/release.yml) for tag-driven packaging and checksum publishing, [validate_repo.py](scripts/validate_repo.py), [pyproject.toml](pyproject.toml), and `tests/test_repo_and_demo.py`.
- **Reproducible Offline Demo:** Added [examples/end_to_end_demo/](examples/end_to_end_demo/README.md) demonstrating `CTO -> PM02 -> CS0201 -> PM02 Acceptance -> CTO Delivery` with real helper script execution, lock-conflict rejection, watchdog unit testing, SHA-256 verification, and explicit separation of executed, simulated, and host-provided capabilities.
- **Documentation Alignment:** Updated [README.md](README.md), [README.zh-CN.md](README.zh-CN.md), and [host-adapters.md](skills/cto-agent-team/references/host-adapters.md) with empirical vs. documented compatibility tiers, operational prerequisites (permissions, model precedence, session creation, parallelism limits), and commit-grounded maintenance notes.

### Core Capabilities Included (Pre-release `main` history, 2026-10-28 to 2026-11-11)

- **56-role Team Organization & State Helper:** `assets/roster.json` (CTO + 5 PMs + 50 engineers) and Python 3.11+ standard-library `scripts/team_state.py` enforcing private `--state-dir` isolation outside the public repo and skill tree (`33d81f6`).
- **Configurable Model Routing & Capacity Recovery:** `scripts/model_route.py`, `assets/routing.schema.json`, `assets/compatibility-6.1.json`, `assets/routing.example.json`, bounded quality escalation, exact-parameter capacity retries, and Luna supervision boundary (`dbc79a1`, `1bca3a6`, `0f5d533`).
- **Shared Atomic Handoff Contracts & Isolated Task Contexts:** Immutable `shared/events/` contracts, clerk `STATUS.md` summary discipline, and fresh per-task context defaults (`6194560`, `ff3b1cb`, `beb89b5`).
- **Google Antigravity & Advisory Guardrails:** `references/antigravity-workflow.md`, UI skill routing (`Frontend Design`, `emil-design-eng`, `unslop`), ASD-STE100 English handoff checks, and `scripts/agent_guard.py` advisory leases + bounded process/SSH watchdogs (`1ce9ccf`).

### Install & Compatibility Scope

- **Install:** Extract `skills/cto-agent-team` (or the `cto-agent-team-v0.1.0.zip` release archive) into `~/.agents/skills/cto-agent-team` or `.agents/skills/cto-agent-team`. For dual Codex + Antigravity use, register the parent skills directory in `~/.gemini/config/skills.json`.
- **Compatibility:** Standard-library Python scripts are CI-tested on Linux, Windows, and macOS with Python 3.11, 3.12, and 3.13. Multi-session creation, live LLM execution, and completion wakeups depend on host runtime tools and account quota.
