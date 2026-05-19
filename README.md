# lazylinear

Zero-dependency CLI for Linear's GraphQL API. Branding is `lazylinear`; the installed command shim is `linear` for day-to-day use.

## Install

```bash
pipx install git+https://github.com/exisz/lazylinear.git
```

This installs both `linear` and `lazylinear` commands.

## Auth

Auth lookup order:

1. `LINEAR_API_KEY` or `LINEAR_TOKEN`
2. `~/.config/lazylinear/token`
3. `roblocks get ${LAZYLINEAR_ROBLOCKS_STORE:-edux} linear_app_token`

## Commands

```bash
linear viewer
linear teams
linear states EDU
linear issues --team EDU --limit 20
linear read EDU-123
linear create "Title" --team EDU --description "..." --label phase-1
linear move EDU-123 "In Progress"
linear comment EDU-123 "Done in abc123"
linear query '{ viewer { id name } }'
```

## Philosophy

- Small, inspectable, no runtime dependencies.
- Human-friendly output by default; JSON with `--json`.
- Same spirit as `lazyjira`, but for Linear.
