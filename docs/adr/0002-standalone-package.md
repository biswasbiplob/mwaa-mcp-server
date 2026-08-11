# ADR 0002: Standalone package outside the awslabs namespace

- **Status:** Accepted
- **Date:** 2026-08-11

## Context

The server was developed inside a fork of the awslabs/mcp monorepo, with the
intent to contribute it upstream. The upstream PR path died (the comparable
community PR awslabs/mcp#2600 was closed as stale), and internal distribution
became the goal. The code carried awslabs packaging identity
(`awslabs.mwaa-mcp-server`, Amazon authorship metadata, awslabs URLs) that it
never officially had.

## Decision

Extract `src/mwaa-mcp-server` into its own repository
(`biswasbiplob/mwaa-mcp-server`) with `git filter-repo`, preserving commit
history. Rename the distribution and module to `mwaa-mcp-server` /
`mwaa_mcp_server`. Keep the Apache-2.0 LICENSE. Strip vendored Amazon license
headers from Python sources written for this project; keep them on the two
files genuinely derived from the awslabs template (`Dockerfile`,
`docker-healthcheck.sh`) and say so in NOTICE.

Distribution is `uvx --from git+https://github.com/biswasbiplob/mwaa-mcp-server`;
a package index (CodeArtifact/PyPI) is deferred until there is a consumer that
git installs cannot serve.

## Consequences

- Public repo needs truthful provenance: authorship is Biplob Biswas, with a
  NOTICE line attributing template-derived scaffolding to awslabs (Apache-2.0
  requires retaining attribution on derived files).
- Installing from a moving `main` requires `--reinstall` in MCP client config
  (or pinning a tag) to pick up updates.
- If awslabs ever ships an official MWAA server, migration is a config swap.
