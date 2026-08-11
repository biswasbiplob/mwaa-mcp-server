"""Shared test fixtures for the MWAA MCP Server tests."""

import pytest
from mcp.server.mcpserver import Context
from unittest.mock import AsyncMock, MagicMock


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
