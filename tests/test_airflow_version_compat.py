# ruff: noqa: D101, D102, D103
"""Tests for the Airflow 2.x/3.x version-aware compatibility layer (ADR 0004)."""

import pytest
from tests.conftest import make_mock_client
from unittest.mock import patch


class TestAirflowVersionDetection:
    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    def test_parses_major_version(self, mock_get_client, handler_readonly):
        mock_get_client.return_value = make_mock_client(airflow_version='3.2.1')

        assert handler_readonly._get_airflow_major_version('test-env') == 3

    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    def test_caches_per_environment(self, mock_get_client, handler_readonly):
        mock_client = make_mock_client(airflow_version='2.7.2')
        mock_get_client.return_value = mock_client

        assert handler_readonly._get_airflow_major_version('test-env') == 2
        assert handler_readonly._get_airflow_major_version('test-env') == 2
        assert mock_client.get_environment.call_count == 1

    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    def test_unparseable_version_raises(self, mock_get_client, handler_readonly):
        mock_get_client.return_value = make_mock_client(airflow_version='weird')

        with pytest.raises(ValueError, match='AirflowVersion'):
            handler_readonly._get_airflow_major_version('test-env')


class TestListDagRunsVersionAware:
    @pytest.mark.asyncio
    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    async def test_v3_translates_order_by_and_date_filters(
        self, mock_get_client, handler_readonly, mock_ctx
    ):
        mock_client = make_mock_client(airflow_version='3.2.1')
        mock_client.invoke_rest_api.return_value = {
            'RestApiResponse': {'dag_runs': [], 'total_entries': 0},
        }
        mock_get_client.return_value = mock_client

        result = await handler_readonly.list_dag_runs(
            mock_ctx,
            environment_name='test-env',
            dag_id='my_dag',
            limit=None,
            offset=None,
            state=None,
            order_by='-execution_date',
            execution_date_gte='2026-01-01T00:00:00+00:00',
            execution_date_lte='2026-01-02T00:00:00+00:00',
        )

        assert not result.is_error
        call_kwargs = mock_client.invoke_rest_api.call_args[1]
        assert call_kwargs['QueryParameters'] == {
            'order_by': '-logical_date',
            'logical_date_gte': '2026-01-01T00:00:00+00:00',
            'logical_date_lte': '2026-01-02T00:00:00+00:00',
        }

    @pytest.mark.asyncio
    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    async def test_v2_keeps_execution_date_vocabulary(
        self, mock_get_client, handler_readonly, mock_ctx
    ):
        mock_client = make_mock_client(airflow_version='2.7.2')
        mock_client.invoke_rest_api.return_value = {
            'RestApiResponse': {'dag_runs': [], 'total_entries': 0},
        }
        mock_get_client.return_value = mock_client

        result = await handler_readonly.list_dag_runs(
            mock_ctx,
            environment_name='test-env',
            dag_id='my_dag',
            limit=None,
            offset=None,
            state=None,
            order_by='-execution_date',
            execution_date_gte='2026-01-01T00:00:00+00:00',
            execution_date_lte=None,
        )

        assert not result.is_error
        call_kwargs = mock_client.invoke_rest_api.call_args[1]
        assert call_kwargs['QueryParameters'] == {
            'order_by': '-execution_date',
            'execution_date_gte': '2026-01-01T00:00:00+00:00',
        }


class TestGetDagSourceVersionAware:
    @pytest.mark.asyncio
    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    async def test_v3_uses_dag_id_path_directly(self, mock_get_client, handler_readonly, mock_ctx):
        mock_client = make_mock_client(airflow_version='3.2.1')
        mock_client.invoke_rest_api.return_value = {
            'RestApiResponse': {'content': 'import airflow'},
        }
        mock_get_client.return_value = mock_client

        result = await handler_readonly.get_dag_source(
            mock_ctx, environment_name='test-env', dag_id='my_dag'
        )

        assert not result.is_error
        assert mock_client.invoke_rest_api.call_count == 1
        call_kwargs = mock_client.invoke_rest_api.call_args[1]
        assert call_kwargs['Path'] == '/dagSources/my_dag'

    @pytest.mark.asyncio
    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    async def test_v2_resolves_file_token_from_dag_details(
        self, mock_get_client, handler_readonly, mock_ctx
    ):
        mock_client = make_mock_client(airflow_version='2.7.2')
        mock_client.invoke_rest_api.side_effect = [
            {'RestApiResponse': {'dag_id': 'my_dag', 'file_token': 'tok123'}},
            {'RestApiResponse': {'content': 'import airflow'}},
        ]
        mock_get_client.return_value = mock_client

        result = await handler_readonly.get_dag_source(
            mock_ctx, environment_name='test-env', dag_id='my_dag'
        )

        assert not result.is_error
        assert mock_client.invoke_rest_api.call_count == 2
        first_path = mock_client.invoke_rest_api.call_args_list[0][1]['Path']
        second_path = mock_client.invoke_rest_api.call_args_list[1][1]['Path']
        assert first_path == '/dags/my_dag'
        assert second_path == '/dagSources/tok123'

    @pytest.mark.asyncio
    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    async def test_v2_missing_file_token_is_error(
        self, mock_get_client, handler_readonly, mock_ctx
    ):
        mock_client = make_mock_client(airflow_version='2.7.2')
        mock_client.invoke_rest_api.return_value = {
            'RestApiResponse': {'dag_id': 'my_dag'},
        }
        mock_get_client.return_value = mock_client

        result = await handler_readonly.get_dag_source(
            mock_ctx, environment_name='test-env', dag_id='my_dag'
        )

        assert result.is_error
        assert 'file_token' in result.content[0].text

    @pytest.mark.asyncio
    async def test_dag_id_path_traversal_rejected(self, handler_readonly, mock_ctx):
        result = await handler_readonly.get_dag_source(
            mock_ctx, environment_name='test-env', dag_id='../bad'
        )

        assert result.is_error
        assert 'path traversal' in result.content[0].text


class TestTriggerDagRunVersionAware:
    @pytest.mark.asyncio
    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    async def test_v3_always_sends_logical_date_key(
        self, mock_get_client, handler_writable, mock_ctx
    ):
        mock_client = make_mock_client(airflow_version='3.2.1')
        mock_client.invoke_rest_api.return_value = {
            'RestApiResponse': {'dag_run_id': 'run-1', 'state': 'queued'},
        }
        mock_get_client.return_value = mock_client

        result = await handler_writable.trigger_dag_run(
            mock_ctx,
            environment_name='test-env',
            dag_id='my_dag',
            conf=None,
            logical_date=None,
        )

        assert not result.is_error
        call_kwargs = mock_client.invoke_rest_api.call_args[1]
        assert call_kwargs['Body']['logical_date'] is None

    @pytest.mark.asyncio
    @patch('mwaa_mcp_server.airflow_tools.get_mwaa_client')
    async def test_v2_omits_logical_date_when_not_provided(
        self, mock_get_client, handler_writable, mock_ctx
    ):
        mock_client = make_mock_client(airflow_version='2.7.2')
        mock_client.invoke_rest_api.return_value = {
            'RestApiResponse': {'dag_run_id': 'run-1', 'state': 'queued'},
        }
        mock_get_client.return_value = mock_client

        result = await handler_writable.trigger_dag_run(
            mock_ctx,
            environment_name='test-env',
            dag_id='my_dag',
            conf=None,
            logical_date=None,
        )

        assert not result.is_error
        assert 'logical_date' not in (mock_client.invoke_rest_api.call_args[1].get('Body') or {})
