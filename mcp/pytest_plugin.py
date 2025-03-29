import pytest
import threading
import time
from flask import Flask
import logging

# Import the mock server implementation
from mcp.mock_server import app as mock_app

logger = logging.getLogger(__name__)


class MockServerThread(threading.Thread):
    """Thread to run the mock MCP server in-process"""

    def __init__(self, host="localhost", port=8000):
        super().__init__(daemon=True)  # Set as daemon so it dies with the main thread
        self.host = host
        self.port = port
        self.is_running = threading.Event()
        self.ready = threading.Event()
        self.app = mock_app

    def run(self):
        """Run the Flask server in this thread"""
        try:
            # Use the Flask test server
            logger.info(f"Starting mock MCP server on {self.host}:{self.port}")
            self.is_running.set()
            self.ready.set()
            self.app.run(
                host=self.host, port=self.port, use_reloader=False, threaded=True
            )
        except Exception as e:
            logger.error(f"Error in mock server thread: {e}")
            self.is_running.clear()
            raise

    def shutdown(self):
        """Shutdown the server"""
        self.is_running.clear()
        # There's no clean way to stop a Flask dev server from another thread
        # Let the daemon thread nature handle the cleanup


@pytest.fixture(scope="session")
def mock_server(request):
    """Start a mock MCP server for testing"""
    # Check if we should use the mock server
    use_mock = request.config.getoption("--mock-server")
    if not use_mock:
        yield None
        return

    # Start the server
    server = MockServerThread()
    server.start()

    # Wait for server to be ready
    server.ready.wait(timeout=5)
    if not server.is_running.is_set():
        raise RuntimeError("Failed to start mock MCP server")

    # Wait a bit for Flask to fully initialize
    time.sleep(1)

    # Return the server information
    yield {
        "url": f"http://{server.host}:{server.port}",
        "host": server.host,
        "port": server.port,
    }

    # Cleanup at the end of the session
    server.shutdown()


def pytest_addoption(parser):
    """Add the --mock-server option"""
    parser.addoption(
        "--mock-server",
        action="store_true",
        default=False,
        help="Use the in-process mock MCP server for testing",
    )


def pytest_configure(config):
    """Configure the pytest session"""
    # If --mock-server is provided, set the server URL to the local mock server
    if config.getoption("--mock-server"):
        # Set environment variable for tests
        import os

        os.environ["MCP_SERVER_URL"] = "http://localhost:8000"


def pytest_report_header(config):
    """Add information to the pytest header"""
    if config.getoption("--mock-server"):
        return "Using in-process mock MCP server at http://localhost:8000"
