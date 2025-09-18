#!/usr/bin/env python3
"""
Enhanced entry point for running the Host Application
This script can be used to start the FastAPI host application
"""

import sys
import os
import logging
import argparse
import traceback

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from host.main import main
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("host_app_run.log")
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run the enhanced Host Application")
    
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to run the host application on"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the application to"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock MCP client for testing"
    )
    
    parser.add_argument(
        "--server-path",
        type=str,
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_server.py"),
        help="Path to the MCP server script"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # Parse arguments
    args = parse_arguments()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Set environment variables for the host application
    os.environ["PORT"] = str(args.port)
    os.environ["HOST"] = args.host
    os.environ["RELOAD"] = str(args.reload).lower()
    os.environ["MCP_USE_MOCK"] = str(args.mock).lower()
    os.environ["MCP_SERVER_PATH"] = args.server_path
    
    # Print startup messages
    print(f"Starting Enhanced Host Application on {args.host}:{args.port}...", file=sys.stderr)
    print(f"Auto-reload: {args.reload}", file=sys.stderr)
    print(f"Mock MCP client: {args.mock}", file=sys.stderr)
    print(f"MCP server path: {args.server_path}", file=sys.stderr)
    print("-" * 50, file=sys.stderr)
    
    try:
        # Run the host application
        main()
    except KeyboardInterrupt:
        print("\nHost application stopped by user", file=sys.stderr)
    except Exception as e:
        logger.error(f"Host application error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
