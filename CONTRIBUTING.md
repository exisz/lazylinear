# Contributing to lazylinear

Thanks for helping improve lazylinear: a small, zero-runtime-dependency Python CLI for Linear's GraphQL API.

## Development setup

```bash
git clone https://github.com/exisz/lazylinear.git
cd lazylinear
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[test]'
```

## Validate changes

```bash
python -m pytest
linear --help
lazylinear --version
python scripts/generate_docs.py > docs/commands.md
git diff --exit-code docs/commands.md
```

## Golden rule: zero runtime dependencies

Runtime code under `src/lazylinear/` must use only the Python standard library.
Test-only dependencies belong in `[project.optional-dependencies].test`.

## Project structure

```
src/lazylinear/
├── __init__.py      # version
├── __main__.py      # python -m lazylinear
├── cli.py           # argparse command surface
└── client.py        # urllib GraphQL client + auth resolution
```

## Command naming

- Package/repo name: `lazylinear`
- Installed commands: `linear` and `lazylinear`
- Prefer `linear` in day-to-day docs because it mirrors the target service.

## Auth notes

Do not commit Linear tokens. The CLI resolves auth in this order:

1. `LINEAR_API_KEY` or `LINEAR_TOKEN`
2. `~/.config/lazylinear/token`
3. `roblocks get ${LAZYLINEAR_ROBLOCKS_STORE:-edux} linear_app_token`

## Pull requests

- Keep PRs focused.
- Add/adjust tests for command behavior.
- Update `README.md`, `docs/commands.md`, and `skill/SKILL.md` when command usage changes.
