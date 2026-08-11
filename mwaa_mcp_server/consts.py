"""Constants for the MWAA MCP Server."""

# Environment variable names
ENV_AWS_REGION = 'AWS_REGION'
ENV_AWS_PROFILE = 'AWS_PROFILE'
ENV_LOG_LEVEL = 'FASTMCP_LOG_LEVEL'
ENV_MWAA_ENVIRONMENT = 'MWAA_ENVIRONMENT'

# Default values
DEFAULT_REGION = 'us-east-1'

# Environment name validation pattern (1-80 chars, starts with letter)
ENVIRONMENT_NAME_PATTERN = r'^[a-zA-Z][0-9a-zA-Z\-_]{0,79}$'

# Airflow REST API path templates
# The AWS invoke_rest_api handles API version routing internally,
# so paths should not include /api/v1 or /api/v2 prefixes.

# DAG endpoints
DAGS_PATH = '/dags'
DAG_PATH = '/dags/{dag_id}'
DAG_SOURCE_PATH = '/dagSources/{file_token}'
DAG_SOURCE_PATH_V3 = '/dagSources/{dag_id}'

# DAG run endpoints
DAG_RUNS_PATH = '/dags/{dag_id}/dagRuns'
DAG_RUN_PATH = '/dags/{dag_id}/dagRuns/{dag_run_id}'

# Task instance endpoints
TASK_INSTANCES_PATH = '/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances'
TASK_INSTANCE_PATH = '/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}'
MAPPED_TASK_INSTANCE_PATH = (
    '/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/{map_index}'
)
LIST_MAPPED_TASK_INSTANCES_PATH = (
    '/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/listMapped'
)
TASK_LOGS_PATH = '/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{try_number}'
CLEAR_TASK_INSTANCES_PATH = '/dags/{dag_id}/clearTaskInstances'

# Other endpoints
CONNECTIONS_PATH = '/connections'
VARIABLES_PATH = '/variables'
IMPORT_ERRORS_PATH = '/importErrors'

# Sensitive fields to redact from connection responses
CONNECTION_SENSITIVE_FIELDS = ('password', 'extra')

# Patterns for identifying sensitive variable keys (case-insensitive substrings)
# Matches Airflow UI behavior for masking sensitive variables
VARIABLE_SENSITIVE_KEY_PATTERNS = (
    'secret',
    'password',
    'passwd',
    'token',
    'api_key',
    'apikey',
    'conn',
    'credential',
    'private_key',
)
