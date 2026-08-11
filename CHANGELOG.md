# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.2.0] - 2026-08-11

### Added

- Airflow version-aware compatibility layer: the server detects each
  environment's Airflow major version via `get_environment` (cached per
  environment/region/profile) and adapts API calls for Airflow 3.x
- `list-dag-runs` translates `execution_date` order-by and date filters to
  `logical_date` on Airflow 3.x environments
- `trigger-dag-run` sends an explicit `logical_date: null` on Airflow 3.x,
  where the field is required-but-nullable

### Changed

- **Breaking**: `get-dag-source` now takes `dag_id` instead of `file_token`.
  On Airflow 3.x the source is fetched by DAG ID directly; on 2.x the server
  resolves the file token internally

## [0.1.0] - 2026-02-24

### Added

- Initial project setup
- MWAA environment management tools (list, get, create, update, delete)
- Airflow REST API tools via invoke_rest_api (DAGs, DAG runs, task instances, logs, connections, variables, import errors)
- Read-only mode by default with --allow-write flag for mutations
- Secure design: no CLI/web token exposure, all operations via invoke_rest_api
