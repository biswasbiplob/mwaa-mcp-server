# ADR 0004: Airflow-version-aware compatibility layer

- **Status:** Accepted
- **Date:** 2026-08-11

## Context

MWAA fleets mix Airflow 2.x and 3.x environments (verified live: two 2.7.2 and
two 3.2.1 environments in one account). Airflow 3's `/api/v2` REST API renamed
and reshaped parts of the v1 contract. Tested empirically against Airflow
3.2.1 via `invoke_rest_api`:

| Tool | Airflow 2.x | Airflow 3.x | Verdict |
|------|-------------|-------------|---------|
| list-dag-runs | `order_by=-execution_date`, `execution_date_gte/lte` | HTTP 400: ordering with `execution_date` disallowed; field is `logical_date` | broken by default |
| get-dag-source | `GET /dagSources/{file_token}` | HTTP 404: path segment is `{dag_id}` | broken |
| trigger-dag-run | `logical_date` key optional | `TriggerDAGRunPostBody.logical_date` is required-but-nullable (strict model) | broken when omitted |
| clear-task-instances | body fields we send | same fields exist in `ClearTaskInstancesBody` | no change |
| get-task-logs | chunked + `continuation_token` | returns `content` only in observed runs; params ignored harmlessly | no change |
| everything else | works | verified or passthrough-safe | no change |

## Decision

1. **Detect the Airflow major version server-side** via the MWAA control plane
   (`get_environment` -> `AirflowVersion`), parsed as the integer major.
   Cached per `(environment_name, region, profile_name)` for the lifetime of
   the server process — environments do not change major version without a
   restart-worthy event. An unparseable version raises `ValueError` (fail
   loud, no silent guessing).
2. **Keep the tool interface stable in Airflow 2.x vocabulary** and translate
   for 3.x underneath: `list-dag-runs` keeps `order_by`/`execution_date_gte`/
   `execution_date_lte` parameter names; on a 3.x environment the server
   rewrites `execution_date` -> `logical_date` in the order-by expression and
   the filter keys. One interface, no version knowledge required of the
   caller.
3. **`get-dag-source` takes `dag_id` instead of `file_token`** (breaking tool
   interface change, pre-1.0). On 3.x the path is `/dagSources/{dag_id}`
   directly; on 2.x the server first fetches `GET /dags/{dag_id}` and resolves
   the `file_token` itself. This removes the two-step token dance from every
   caller on both versions.
4. **`trigger-dag-run` always includes the `logical_date` key on 3.x**
   (explicit value or `null`); on 2.x it stays omitted when not provided.

Out of scope, deliberately: response-shape normalization between versions
(responses are passed through as JSON; consumers are LLMs that read either
shape), task-log chunking differences on 3.x (works, returns full content),
and `list-dags`/`list-task-instances`/connections/variables/import-errors
(verified working unchanged).

## Consequences

- One extra `get_environment` call per (environment, region, profile) per
  server process for the three affected tools; cached thereafter.
- `get-dag-source` callers pass a DAG id everywhere; the `file_token` field in
  `get-dag`/`list-dags` responses is no longer needed by any tool.
- Version bumped to 0.2.0 for the interface change.
- If a future Airflow major changes these contracts again, the branch points
  are all guarded by `major >= 3` in one module and covered by version-split
  unit tests.
