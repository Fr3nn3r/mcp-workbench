#!/usr/bin/env python3
"""Script to start the mock MCP server."""

import argparse
from mock_server.server import run_server


def main():
    """Main entry point for starting the mock server."""
    parser = argparse.ArgumentParser(description="Start Mock MCP Server")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )

    args = parser.parse_args()
    print(f"Starting mock MCP server at http://{args.host}:{args.port}")
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
