<div align="center">

```
 _                 _ _
| | __ _ _____   _| (_)_ __   ___  __ _ _ __
| |/ _` |_  / | | | | | '_ \ / _ \/ _` | '__|
| | (_| |/ /| |_| | | | | | |  __/ (_| | |
|_|\__,_/___|\__, |_|_|_| |_|\___|\__,_|_|
             |___/
```

**Zero-dependency Python CLI for Linear's GraphQL API.**

[![Python](https://img.shields.io/pypi/pyversions/lazylinear)](https://pypi.org/project/lazylinear/)
[![License](https://img.shields.io/github/license/exisz/lazylinear)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/exisz/lazylinear/ci.yml)](https://github.com/exisz/lazylinear/actions)

[Installation](#installation) · [Quick Start](#quick-start) · [Commands](#commands) · [Auth](#auth) · [Contributing](CONTRIBUTING.md)

</div>

---

## Why lazylinear?

Linear's app is excellent, but agents and terminal workflows need a tiny, inspectable CLI.
`lazylinear` keeps the runtime dependency graph at **zero**: no `requests`, no `click`, no `rich` — only Python's standard library.

Branding is `lazylinear`; the installed day-to-day command shim is `linear`.
Both entrypoints are supported:

```bash
linear --version
lazylinear --version
```

## Installation

```bash
# From GitHub
pipx install git+https://github.com/exisz/lazylinear.git

# From source
git clone https://github.com/exisz/lazylinear.git
cd lazylinear
pip install .
```

This installs both `linear` and `lazylinear` commands.

## Quick Start

```bash
# 1. Authenticate
export LINEAR_API_KEY="lin_api_..."

# 2. Inspect account and team setup
linear viewer
linear teams
linear states EDU

# 3. Work with issues
linear issues --team EDU --limit 20
linear read EDU-123
linear create "Write merchant onboarding story" --team EDU --description "Phase 1 scope" --label phase-1
linear move EDU-123 "In Progress"
linear comment EDU-123 "Fixed in commit abc123"
```

## Auth

Auth lookup order:

1. `LINEAR_API_KEY` or `LINEAR_TOKEN`
2. `~/.config/lazylinear/token` (or `LAZYLINEAR_TOKEN_FILE`)
3. `roblocks get ${LAZYLINEAR_ROBLOCKS_STORE:-edux} ${LAZYLINEAR_ROBLOCKS_KEY:-linear_app_token}`

Agent default for Edu X is roblocks store `edux`, key `linear_app_token`.

## Commands

```bash
linear viewer                                      # Show authenticated user/org
linear teams [--limit 50]                         # List teams
linear states EDU                                 # List workflow states for a team
linear issues --team EDU --limit 20               # List issues
linear issues --limit 20                          # List recent visible issues across teams
linear read EDU-123                               # Read one issue
linear create "Title" --team EDU --description "..." --label phase-1
linear move EDU-123 "In Progress"                # Move issue to workflow state by name
linear comment EDU-123 "Done in abc123"          # Add comment
linear comments EDU-123 --limit 10                # List comments
linear query '{ viewer { id name } }'             # Raw GraphQL escape hatch
```

Use `--json` before the subcommand for machine-readable output:

```bash
linear --json issues --team EDU --limit 5
```

Full generated command reference: [`docs/commands.md`](docs/commands.md).

## Philosophy

- Small, inspectable, no runtime dependencies.
- Human-friendly output by default; JSON with `--json`.
- Same spirit as `lazyjira`, but for Linear.
- Command surface is intentionally narrow; raw GraphQL is available via `linear query` when needed.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
python -m pytest
linear --help
python scripts/generate_docs.py > docs/commands.md
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for project standards.
