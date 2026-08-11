# ADR 0003: Target the mcp 2.x SDK

- **Status:** Accepted
- **Date:** 2026-08-11

## Context

The server was written against mcp 1.x (`mcp.server.fastmcp.FastMCP`). mcp
2.0.0 renamed the high-level class to `MCPServer`, moved `Context` to
`mcp.server.mcpserver`, moved wire types to the `mcp-types` package (with
`mcp.types` kept as a permanent alias), and switched model fields to
snake_case (`isError` -> `is_error`). Fresh installs resolved 2.0.0 and
crashed on import while the lockfile kept local tests green.

## Decision

Migrate to mcp 2.x and require `mcp>=2.0.0,<3.0.0`. Drop the unused `[cli]`
extra. Add a registration test against a real `MCPServer` instance so tool
schema building runs in CI instead of being mocked away.

## Consequences

- Fresh consumer installs and the lockfile now resolve the same major version.
- The real-server registration test fails loudly on the next breaking SDK
  change.
- Post-publish verification rule: after any release-affecting change, run one
  fresh install from the published source (`uvx --refresh --from <url>`) —
  local suites validate the locked environment, not the consumer's resolution.
