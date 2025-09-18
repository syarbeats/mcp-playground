"""
Simple MCP client test
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleClient:
    """Simple MCP client for testing"""
    
    def __init__(self, server_command):
        """Initialize the client"""
        self.server_command = server_command
        self.process = None
        self.message_id = 0
        logger.info(f"Simple client initialized with command: {' '.join(server_command)}")
    
    def _next_id(self):
        """Get next message ID"""
        self.message_id += 1
        return self.message_id
    
    async def start(self):
        """Start the server process"""
        try:
            logger.info("Starting server process...")
            
            # Start the server process
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # Unbuffered
            )
            
            # Send initialization message
            init_msg = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "1.0",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "clientInfo": {
                        "name": "Simple Test Client",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self._send_message(init_msg)
            
            if response and "result" in response:
                logger.info("Server initialized successfully")
                return True
            else:
                logger.error("Failed to initialize server")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}", exc_info=True)
            return False
    
    async def stop(self):
        """Stop the server process"""
        if self.process:
            logger.info("Stopping server process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            logger.info("Server process stopped")
    
    async def _send_message(self, message):
        """Send a message to the server and get response"""
        if not self.process or not self.process.stdin or not self.process.stdout:
            logger.error("Server process not running")
            return None
        
        try:
            # Send message
            msg_json = json.dumps(message)
            logger.debug(f"Sending: {msg_json}")
            
            # Print the raw bytes being sent for debugging
            msg_bytes = (msg_json + "\n").encode('utf-8')
            logger.debug(f"Sending raw bytes: {msg_bytes}")
            
            self.process.stdin.write(msg_json + "\n")
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            logger.debug(f"Received raw: {response_line}")
            
            if response_line:
                try:
                    response = json.loads(response_line)
                    logger.debug(f"Parsed response: {response}")
                    return response
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse response: {e}")
                    logger.error(f"Raw response: {response_line!r}")
                    return None
            else:
                logger.error("No response from server")
                return None
                
        except Exception as e:
            logger.error(f"Error communicating with server: {str(e)}", exc_info=True)
            return None
    
    async def list_tools(self):
        """List available tools"""
        tools_msg = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        }
        
        response = await self._send_message(tools_msg)
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            logger.info(f"Discovered {len(tools)} tools")
            for tool in tools:
                logger.info(f"  - {tool['name']}: {tool['description']}")
            return tools
        else:
            logger.error("Failed to list tools")
            return []
    
    async def call_tool(self, tool_name, arguments):
        """Call a tool"""
        tool_msg = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_message(tool_msg)
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "")
            return "No content returned"
        else:
            logger.error("Failed to call tool")
            return None

async def main():
    """Main entry point"""
    # Get path to test server
    server_command = [sys.executable, "test_mcp_direct.py"]
    
    client = SimpleClient(server_command)
    
    try:
        # Start client
        print("Starting client...")
        success = await client.start()
        
        if success:
            print("\nClient started successfully!")
            
            # List tools
            print("\n--- Listing Tools ---")
            tools = await client.list_tools()
            
            if tools:
                # Call echo tool
                print("\n--- Calling Echo Tool ---")
                result = await client.call_tool(
                    "echo",
                    {"message": "Hello, MCP!"}
                )
                print(f"Tool result: {result}")
            
        else:
            print("Failed to start client")
    
    finally:
        # Stop client
        await client.stop()
        print("\nClient stopped")

if __name__ == "__main__":
    asyncio.run(main())
