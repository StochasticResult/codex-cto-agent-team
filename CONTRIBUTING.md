# Contributing to codex-cto-agent-team

Thank you for helping improve `codex-cto-agent-team`. This repository contains both the distributable Agent Skill package and its engineering test, validation, and documentation harness.

## Repository layout

- `skills/cto-agent-team/` — The self-contained, installable skill folder:
  - `SKILL.md` — Entry point, workflow triggers, and policy boundaries
  - `agents/openai.yaml` — Skill UI metadata
  - `assets/` — Sanitized role roster (`roster.json`), explicit routing profile (`compatibility-6.1.json`), JSON schema (`routing.schema.json`), and offline routing fixture (`routing.example.json`)
  - `references/` — Topic-specific workflow, host adapter, recovery, handoff, and state guides
  - `scripts/` — Standard-library Python 3.11+ helpers (`team_state.py`, `model_route.py`, `agent_guard.py`)
- `examples/` — Reproducible offline demonstrations (kept outside `skills/cto-agent-team/` so installations remain minimal)
- `scripts/` — Repository-level maintenance helpers (`validate_repo.py`)
- `tests/` — Standard-library `unittest` suite covering helper contracts, state boundaries, demo execution, and package validation
- `README.md` / `README.zh-CN.md` — Bilingual entry documentation

## Prerequisites

- **Runtime helpers & tests:** Python 3.11 or later using only the Python standard library.
- **Optional local quality checks:** `ruff` and `mypy` (configured in [pyproject.toml](pyproject.toml) and run automatically in GitHub Actions).

## Local verification workflow

Run all of the following checks from the repository root before opening a pull request:

```sh
python -m unittest discover -s tests -v
python scripts/validate_repo.py --verify-package
python examples/end_to_end_demo/run_demo.py --verify
```

If `ruff` and `mypy` are installed in your environment, also run:

```sh
ruff check .
mypy skills scripts examples tests
```

## Contribution guidelines

1. **Preserve the skill package boundary:** Keep runtime state, tests, examples, and CI tooling outside `skills/cto-agent-team/`. Both `team_state.py` and `agent_guard.py` reject `--state-dir` and `--lock-dir` paths inside the repository or skill tree; always use temporary directories outside the repo in tests and demos.
2. **Never commit private or machine-specific data:** Do not commit credentials, tokens, real chat/thread UUIDs, host IDs, personal filesystem paths, internal network hostnames, or unpublished company project data.
3. **Preserve evidence levels:** Follow the six-tier evidence discipline in [host-adapters.md](skills/cto-agent-team/references/host-adapters.md#evidence-levels). Clearly separate documentation guidance, offline fixtures, locally executed scripts, and verified live host execution. Do not fabricate adopters, issue activity, or unmeasured performance claims.
4. **Keep bilingual docs synchronized:** Update both [README.md](README.md) and [README.zh-CN.md](README.zh-CN.md) when changing user-facing workflows, installation steps, CLI behavior, or compatibility boundaries.
5. **Follow ASD-STE100 for English handoff examples:** When editing English handoff templates or instructions intended for cross-role transfer, review terminology and rules per [handoffs.md](skills/cto-agent-team/references/handoffs.md).
6. **Add regression tests:** Any change to `scripts/` or `assets/` schemas should include matching `unittest` coverage under `tests/`.
7. **Keep line endings consistent:** Follow `.gitattributes` (`LF` line endings across Python, Markdown, JSON, and YAML files).

## Pull request process

1. Fork the repository and create a focused branch from `main`.
2. Make minimal, well-scoped changes and run the local verification suite.
3. Complete the checklist in [the PR template](.github/PULL_REQUEST_TEMPLATE.md).
4. Wait for the `Tests` GitHub Actions workflow (`quality` + cross-platform `unit-and-demo` matrix) to pass.
