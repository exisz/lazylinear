---
name: lazylinear
description: Linear issue tracking via the `linear` CLI shim (lazylinear package). Use for Edu X Linear board operations.
---

# lazylinear / `linear`

Use `linear` for Edu X issue tracking. The package/repo is `lazylinear`; installed commands are `linear` and `lazylinear`.

## Setup

```bash
pipx install git+https://github.com/exisz/lazylinear.git
# or, from a checkout:
pip install -e .
```

## Auth

Resolution order:

1. `LINEAR_API_KEY` or `LINEAR_TOKEN`
2. `~/.config/lazylinear/token` (or `LAZYLINEAR_TOKEN_FILE`)
3. `roblocks get ${LAZYLINEAR_ROBLOCKS_STORE:-edux} ${LAZYLINEAR_ROBLOCKS_KEY:-linear_app_token}`

Edu X agent default: roblocks store `edux`, key `linear_app_token`.

## Common Commands

```bash
linear viewer
linear teams
linear states EDU
linear issues --team EDU --limit 20
linear read EDU-123
linear create "Title" --team EDU --description "..." --label phase-1
linear move EDU-123 "In Progress"
linear comment EDU-123 "Done in commit abc123"
linear comments EDU-123 --limit 10
linear --json issues --team EDU --limit 5
```

Raw GraphQL escape hatch:

```bash
linear query '{ viewer { id name } }'
linear query 'query($id:String!){ issue(id:$id){ identifier title } }' --variables '{"id":"EDU-123"}'
```

## Rules for Station/Edu X

- Edu X uses Linear via `linear`.
- Nexus/Station Jira work continues to use Jira via `lazyjira`.
- Do not use deprecated `lin`; it is a Jira shim and conflicts with Linear naming.
- Prefer `--json` for automation and plain output for human inspection.
- Never commit Linear API tokens; use environment variables, token file with `chmod 600`, or roblocks.

## Project Standards

- Zero runtime dependencies: stdlib only under `src/lazylinear/`.
- Preserve both CLI shims: `linear` and `lazylinear`.
- When command usage changes, update README, `docs/commands.md`, and this skill.
