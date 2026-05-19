---
name: lazylinear
description: Linear issue tracking via the `linear` CLI shim (lazylinear package). Use for Edu X Linear board operations.
---

# lazylinear / `linear`

Use `linear` for Edu X issue tracking. The package/repo is `lazylinear`; the CLI command is `linear`.

Auth lookup order:
1. `LINEAR_API_KEY` or `LINEAR_TOKEN`
2. `~/.config/lazylinear/token`
3. `roblocks get ${LAZYLINEAR_ROBLOCKS_STORE:-edux} linear_app_token`

Common commands:

```bash
linear viewer
linear teams
linear states EDU
linear issues --team EDU --limit 20
linear read EDU-123
linear create "Title" --team EDU --description "..." --label phase-1
linear move EDU-123 "In Progress"
linear comment EDU-123 "Done in commit abc123"
```

Rules for Station/Edu X:
- Edu X uses Linear via `linear`.
- Nexus continues to use Jira via `lazyjira`.
- Do not use deprecated `lin`; it is currently a Jira shim and conflicts with Linear naming.
