# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.x     | ✅ Current |

## Reporting a Vulnerability

Please report security issues privately:

1. Do **not** open a public GitHub issue.
2. Email gotexis@users.noreply.github.com.
3. Include impact, reproduction steps, and affected version/commit when possible.

## Security Considerations

- lazylinear stores optional local tokens at `~/.config/lazylinear/token`.
- Tokens are sent only to Linear's GraphQL API endpoint.
- Restrict token-file permissions: `chmod 600 ~/.config/lazylinear/token`.
- Prefer environment variables or roblocks-backed retrieval for agent workflows.
