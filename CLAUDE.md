# CLAUDE.md — mwaa-mcp-server

Conventions and traps specific to this repo. Read before you change code here.

## Commands

```bash
uv run pytest -q              # full suite, must stay green
uv run ruff check .           # lint
uv run ruff format .          # format (single quotes, line length 99)
uv lock                       # re-lock after a version bump
```

There is no Makefile and no CI. The local run is the only evidence a change works.

## Architecture

- `server.py` — builds the MCPServer, parses `--allow-write`, wires the two handler classes.
- `environment_tools.py` — `EnvironmentTools`, the MWAA control plane (`boto3` calls).
- `airflow_tools.py` — `AirflowTools`, every Airflow REST call.
- `aws_client.py` — the single `get_mwaa_client` factory. Tests patch this name.
- `consts.py` — API path templates and redaction patterns.

Each handler registers its tools inside `__init__` with `self.mcp.tool(name='...')`.

All Airflow access goes through `invoke_rest_api` (ADR 0001). Never add `create_cli_token` or `create_web_login_token`.

## Adding a tool

1. Add the path template to `consts.py`.
2. Write the failing test in `tests/test_airflow_tools.py` first.
3. Add the method to the handler and register it in `__init__`.
4. Update the hardcoded tool counts in `tests/test_server.py`. Three assertions carry a number.
5. Add the row to the README tool table.
6. Follow the release steps below.

Write tools must call `self._check_write_access()` first.

## Traps

**Tool counts are hardcoded.** `tests/test_server.py` asserts an exact count in three places. A new tool fails those tests until you bump each number.

**Unset `Field()` defaults are not `None` in tests.** Tests call handler methods directly, with no FastMCP in front. An omitted parameter therefore arrives as a Pydantic `FieldInfo`, not `None`. Pass `limit=None` explicitly when a test needs to simulate what a real client sends.

**API paths carry no version prefix.** `invoke_rest_api` routes the version itself. `/pools` works. `/api/v2/pools` and `/v2/pools` both answer 404.

**`GET /pools` needs a `limit`.** On Airflow 3.2.1 the bare path answers HTTP 500. `list_pools` always sends the parameter.

**The version compat layer is narrow.** `_get_airflow_major_version` exists for three differences only: date vocabulary (`execution_date` vs `logical_date`), `order_by` values, and DAG source lookup. Do not add a version branch to a new tool unless you have confirmed a real difference.

## Release steps

Every user-visible change needs all four, split into three commits. Check `git log` for the 0.2.0 release as the reference shape.

1. `feat:` — code and tests.
2. `docs:` — a `CHANGELOG.md` section, plus the README tool table.
3. `chore: bump version to X.Y.Z` — three places, then `uv lock`:
   - `pyproject.toml` `[project] version`
   - `pyproject.toml` `[tool.commitizen] version`
   - `mwaa_mcp_server/__init__.py` `__version__`

A new tool is a minor bump. A changed tool signature is breaking, so record it under `### Changed` with a **Breaking** marker, as `get-dag-source` did in 0.2.0.

Add an ADR under `docs/adr/` only for an architectural decision. A new tool does not need one.
