"""Tests for the main function in server.py."""

from mwaa_mcp_server.server import create_server, main
from unittest.mock import MagicMock, patch


class TestMain:
    """Tests for the main function."""

    @patch('mwaa_mcp_server.server.AirflowTools')
    @patch('mwaa_mcp_server.server.EnvironmentTools')
    @patch('mwaa_mcp_server.server.create_server')
    @patch('sys.argv', ['mwaa-mcp-server'])
    def test_main_default(self, mock_create_server, mock_env_tools, mock_airflow_tools):
        """Test main function with default arguments (read-only mode)."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server

        main()

        mock_create_server.assert_called_once()
        mock_env_tools.assert_called_once_with(mock_server, False)
        mock_airflow_tools.assert_called_once_with(mock_server, False)
        mock_server.run.assert_called_once()

    @patch('mwaa_mcp_server.server.AirflowTools')
    @patch('mwaa_mcp_server.server.EnvironmentTools')
    @patch('mwaa_mcp_server.server.create_server')
    @patch('sys.argv', ['mwaa-mcp-server', '--allow-write'])
    def test_main_allow_write(self, mock_create_server, mock_env_tools, mock_airflow_tools):
        """Test main function with --allow-write flag."""
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server

        main()

        mock_create_server.assert_called_once()
        mock_env_tools.assert_called_once_with(mock_server, True)
        mock_airflow_tools.assert_called_once_with(mock_server, True)
        mock_server.run.assert_called_once()

    def test_module_execution(self):
        """Test the module execution when run as __main__."""
        import inspect
        from mwaa_mcp_server import server

        source = inspect.getsource(server)
        assert "if __name__ == '__main__':" in source
        assert 'main()' in source

    def test_create_server(self):
        """Test that create_server creates a FastMCP instance with correct parameters."""
        with patch('mwaa_mcp_server.server.MCPServer') as mock_mcpserver:
            create_server()

            mock_mcpserver.assert_called_once()
            args, kwargs = mock_mcpserver.call_args
            assert args[0] == 'mwaa-mcp-server'
            assert 'instructions' in kwargs
            assert 'dependencies' in kwargs
            assert 'MWAA MCP Server' in kwargs['instructions']
            assert 'boto3' in kwargs['dependencies']
