"""Shared test fixtures for the MWAA MCP Server tests."""

import pytest
from mcp.server.mcpserver import Context
from mwaa_mcp_server.airflow_tools import AirflowTools
from unittest.mock import AsyncMock, MagicMock


def make_mock_client(airflow_version='2.7.2'):
    """Create a mock MWAA boto3 client with a stubbed environment version."""
    client = MagicMock()
    client.get_environment.return_value = {
        'Environment': {'AirflowVersion': airflow_version},
    }
    return client


@pytest.fixture
def mock_ctx():
    """Create a mock MCP Context with async methods."""
    ctx = MagicMock(spec=Context)
    ctx.error = AsyncMock()
    ctx.info = AsyncMock()
    ctx.warning = AsyncMock()
    return ctx


@pytest.fixture
def mock_mwaa_client():
    """Create a mock MWAA boto3 client."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_mcp():
    """Create a mock MCP server instance."""
    mcp = MagicMock()
    return mcp


@pytest.fixture
def handler_readonly(mock_mcp):
    """AirflowTools registered in read-only mode."""
    return AirflowTools(mock_mcp)


@pytest.fixture
def handler_writable(mock_mcp):
    """AirflowTools registered with write access."""
    return AirflowTools(mock_mcp, allow_write=True)
