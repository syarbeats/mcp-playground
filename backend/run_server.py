#!/usr/bin/env python3
"""
Enhanced entry point for running the MCP server
This script can be used to start the MCP server standalone for testing or integration
"""

import sys
import os
import logging
import argparse
import traceback

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server.server import main
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("mcp_server_run.log")
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run the enhanced MCP server")
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--server-name",
        type=str,
        default="task-management-server",
        help="Name of the MCP server"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Print startup messages to stderr instead of stdout
    print("Starting Enhanced MCP Task Management Server...", file=sys.stderr)
    print("This server communicates via stdio (standard input/output)", file=sys.stderr)
    print("It provides tools and resources for task management", file=sys.stderr)
    print(f"Server name: {args.server_name}", file=sys.stderr)
    print("-" * 50, file=sys.stderr)
    
    try:
        # Run the server
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
