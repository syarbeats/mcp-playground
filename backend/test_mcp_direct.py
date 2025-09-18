"""
Direct test of MCP SDK functionality
"""

import asyncio
import sys
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleServer:
    """Simple MCP server for testing"""
    
    def __init__(self):
        """Initialize the server"""
        self.server = Server("test-server")
        self._setup_handlers()
        logger.info("Simple test server initialized")
    
    def _setup_handlers(self):
        """Set up basic handlers"""
        
        @self.server.list_tools()
        async def list_tools():
            """List available tools"""
            return [
                Tool(
                    name="echo",
                    description="Echo back the input",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to echo"
                            }
                        },
                        "required": ["message"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name, arguments):
            """Handle tool calls"""
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            if name == "echo":
                message = arguments.get("message", "No message provided")
                return [TextContent(
                    type="text",
                    text=f"Echo: {message}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
    
    async def run(self):
        """Run the server"""
        logger.info("Starting simple MCP server...")
        
        try:
            # Run with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                logger.debug("Stdio server created")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)

async def main():
    """Main entry point"""
    try:
        server = SimpleServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Print startup messages to stderr instead of stdout
    print("Starting simple MCP test server...", file=sys.stderr)
    print("This server communicates via stdio", file=sys.stderr)
    print("-" * 50, file=sys.stderr)
    asyncio.run(main())
