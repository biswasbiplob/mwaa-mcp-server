# ADR 0001: All Airflow access goes through MWAA InvokeRestApi

- **Status:** Accepted
- **Date:** 2026-02 (recorded retroactively 2026-08-11)

## Context

An MCP server for MWAA can reach the Airflow REST API three ways: mint a web
login token, mint a CLI token, or use the AWS-native `invoke_rest_api` SDK
operation. Token-based approaches return credentials into the MCP
conversation, where they land in transcripts, logs, and observability
pipelines.

## Decision

Every Airflow API operation goes through `boto3` `invoke_rest_api`. The server
does not expose `create_cli_token` or `create_web_login_token` as tools, and no
Airflow credential ever appears in a tool response. IAM is the only auth
surface (`airflow:InvokeRestApi` plus the environment read/write actions).

## Consequences

- No credential leakage into conversation history.
- Requires Airflow >= 2.4.3 on MWAA (the floor for `InvokeRestApi`).
- The server inherits MWAA's request/response envelope (`RestApiResponse`),
  including its error wrapping (`RestApiClientException`).
- Connection passwords and sensitive variable values are additionally redacted
  server-side before responses are returned.
