"""
Enhanced MCP Client Implementation
Provides robust communication with MCP servers with improved error handling and recovery
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("mcp_client.log")
    ]
)
logger = logging.getLogger(__name__)


class MCPError(Exception):
    """Base exception for MCP client errors"""
    pass


class ConnectionError(MCPError):
    """Exception raised for connection errors"""
    pass


class CommunicationError(MCPError):
    """Exception raised for communication errors"""
    pass


class ToolError(MCPError):
    """Exception raised for tool execution errors"""
    pass


class ResourceError(MCPError):
    """Exception raised for resource access errors"""
    pass


class MCPMessageType(Enum):
    """MCP message types with improved organization"""
    # Core protocol messages
    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    
    # Tool-related messages
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    
    # Resource-related messages
    LIST_RESOURCES = "resources/list"
    LIST_RESOURCE_TEMPLATES = "resources/templates/list"
    READ_RESOURCE = "resources/read"
    
    # Error handling
    ERROR = "error"


@dataclass
class MCPMessage:
    """
    Enhanced representation of an MCP protocol message
    Includes validation and improved error handling
    """
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> dict:
        """Convert message to dictionary with validation"""
        # Validate required fields
        if self.method and (self.result is not None or self.error is not None):
            raise ValueError("Message cannot have both method and result/error")
        
        if self.result is not None and self.error is not None:
            raise ValueError("Message cannot have both result and error")
        
        # Build message
        msg = {"jsonrpc": self.jsonrpc}
        
        if self.id is not None:
            msg["id"] = self.id
            
        if self.method:
            msg["method"] = self.method
            
        if self.params is not None:
            msg["params"] = self.params
            
        if self.result is not None:
            msg["result"] = self.result
            
        if self.error is not None:
            msg["error"] = self.error
            
        return msg
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MCPMessage':
        """Create message from dictionary with validation"""
        # Validate required fields
        if "jsonrpc" not in data:
            raise ValueError("Missing required field 'jsonrpc'")
        
        # Create message
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method"),
            params=data.get("params"),
            result=data.get("result"),
            error=data.get("error")
        )


class MCPClient:
    """
    Enhanced MCP Client for communicating with MCP servers
    Includes improved error handling, reconnection logic, and performance optimizations
    """
    
    def __init__(self, server_command: List[str], max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize MCP client with enhanced options
        
        Args:
            server_command: Command to start the MCP server (e.g., ["python", "server.py"])
            max_retries: Maximum number of retries for operations
            retry_delay: Delay between retries in seconds
        """
        self.server_command = server_command
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.process: Optional[subprocess.Popen] = None
        self.message_id = 0
        self.tools: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []
        self.resource_templates: List[Dict[str, Any]] = []
        self.initialized = False
        self.last_activity = time.time()
        
        logger.info(f"MCP Client initialized with command: {' '.join(server_command)}")
        logger.info(f"Retry settings: max_retries={max_retries}, retry_delay={retry_delay}s")
    
    def _next_id(self) -> int:
        """Get next message ID"""
        self.message_id += 1
        return self.message_id
    
    async def connect(self) -> bool:
        """
        Connect to the MCP server with retry logic
        Starts the server process and performs initialization handshake
        
        Returns:
            True if connection successful, False otherwise
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Starting MCP server process (attempt {attempt}/{self.max_retries})...")
                
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
                init_msg = MCPMessage(
                    id=self._next_id(),
                    method=MCPMessageType.INITIALIZE.value,
                    params={
                        "protocolVersion": "1.0",
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "clientInfo": {
                            "name": "Enhanced MCP Client",
                            "version": "2.0.0"
                        }
                    }
                )
                
                response = await self._send_message(init_msg)
                
                if response and "result" in response:
                    logger.info("MCP server initialized successfully")
                    self.initialized = True
                    self.last_activity = time.time()
                    
                    # Discover available tools and resources
                    await self._discover_capabilities()
                    return True
                else:
                    logger.error("Failed to initialize MCP server")
                    await self.disconnect()
                    
                    if attempt < self.max_retries:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"Failed to connect to MCP server: {str(e)}")
                logger.error(traceback.format_exc())
                await self.disconnect()
                
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
        
        logger.error(f"Failed to connect after {self.max_retries} attempts")
        return False
    
    async def disconnect(self):
        """Disconnect from the MCP server with improved cleanup"""
        if self.process:
            logger.info("Disconnecting from MCP server...")
            
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Server process did not terminate, forcing kill")
                    self.process.kill()
                    self.process.wait(timeout=2)
            except Exception as e:
                logger.error(f"Error during disconnect: {str(e)}")
            
            self.process = None
            self.initialized = False
            logger.info("Disconnected from MCP server")
    
    async def _send_message(self, message: MCPMessage) -> Optional[dict]:
        """
        Send a message to the MCP server and wait for response with improved error handling
        
        Args:
            message: MCP message to send
        
        Returns:
            Response dictionary or None if error
            
        Raises:
            ConnectionError: If server process is not running
            CommunicationError: If error communicating with server
        """
        if not self.process or not self.process.stdin or not self.process.stdout:
            raise ConnectionError("Server process not running")
        
        try:
            # Send message
            msg_dict = message.to_dict()
            msg_json = json.dumps(msg_dict)
            logger.debug(f"Sending: {msg_json}")
            
            self.process.stdin.write(msg_json + "\n")
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            
            if not response_line:
                raise CommunicationError("No response from server")
            
            try:
                response = json.loads(response_line)
                logger.debug(f"Received: {response}")
                
                # Update last activity timestamp
                self.last_activity = time.time()
                
                # Check for error
                if "error" in response:
                    error_data = response["error"]
                    logger.warning(f"Server returned error: {error_data}")
                
                return response
            except json.JSONDecodeError as e:
                raise CommunicationError(f"Invalid JSON response: {e}")
                
        except ConnectionError:
            # Re-raise connection errors
            raise
        except CommunicationError:
            # Re-raise communication errors
            raise
        except Exception as e:
            # Wrap other exceptions
            raise CommunicationError(f"Error communicating with server: {str(e)}")
    
    async def _discover_capabilities(self):
        """
        Discover available tools and resources from the server
        Includes improved error handling and logging
        """
        logger.info("Discovering server capabilities...")
        
        # List tools
        try:
            tools_msg = MCPMessage(
                id=self._next_id(),
                method=MCPMessageType.LIST_TOOLS.value,
                params={}
            )
            
            response = await self._send_message(tools_msg)
            if response and "result" in response:
                self.tools = response["result"].get("tools", [])
                logger.info(f"Discovered {len(self.tools)} tools")
                for tool in self.tools:
                    logger.info(f"  - {tool['name']}: {tool['description']}")
            else:
                logger.warning("Failed to discover tools")
        except Exception as e:
            logger.error(f"Error discovering tools: {str(e)}")
        
        # List resources
        try:
            resources_msg = MCPMessage(
                id=self._next_id(),
                method=MCPMessageType.LIST_RESOURCES.value,
                params={}
            )
            
            response = await self._send_message(resources_msg)
            if response and "result" in response:
                self.resources = response["result"].get("resources", [])
                logger.info(f"Discovered {len(self.resources)} resources")
                for resource in self.resources:
                    logger.info(f"  - {resource['uri']}: {resource['name']}")
            else:
                logger.warning("Failed to discover resources")
        except Exception as e:
            logger.error(f"Error discovering resources: {str(e)}")
        
        # List resource templates
        try:
            templates_msg = MCPMessage(
                id=self._next_id(),
                method=MCPMessageType.LIST_RESOURCE_TEMPLATES.value,
                params={}
            )
            
            response = await self._send_message(templates_msg)
            if response and "result" in response:
                self.resource_templates = response["result"].get("resourceTemplates", [])
                logger.info(f"Discovered {len(self.resource_templates)} resource templates")
                for template in self.resource_templates:
                    logger.info(f"  - {template['uriTemplate']}: {template['name']}")
            else:
                logger.warning("Failed to discover resource templates")
        except Exception as e:
            logger.error(f"Error discovering resource templates: {str(e)}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """
        Call a tool on the MCP server with retry logic
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
        
        Returns:
            Tool result as string or None if error
            
        Raises:
            ToolError: If tool execution fails
        """
        if not self.initialized:
            raise ToolError("Client not initialized")
        
        # Check if tool exists
        tool_exists = any(tool["name"] == tool_name for tool in self.tools)
        if not tool_exists:
            raise ToolError(f"Tool '{tool_name}' not found")
        
        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
        
        # Try with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                tool_msg = MCPMessage(
                    id=self._next_id(),
                    method=MCPMessageType.CALL_TOOL.value,
                    params={
                        "name": tool_name,
                        "arguments": arguments
                    }
                )
                
                response = await self._send_message(tool_msg)
                
                if response and "result" in response:
                    content = response["result"].get("content", [])
                    if content and len(content) > 0:
                        return content[0].get("text", "")
                    else:
                        logger.warning("Tool returned empty content")
                        return ""
                elif response and "error" in response:
                    error_data = response["error"]
                    error_msg = f"Tool error: {error_data.get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    
                    if attempt < self.max_retries:
                        logger.info(f"Retrying tool call (attempt {attempt}/{self.max_retries})...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise ToolError(error_msg)
                else:
                    logger.error("Invalid response format")
                    
                    if attempt < self.max_retries:
                        logger.info(f"Retrying tool call (attempt {attempt}/{self.max_retries})...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise ToolError("Invalid response format")
                    
            except (ConnectionError, CommunicationError) as e:
                logger.error(f"Communication error: {str(e)}")
                
                if attempt < self.max_retries:
                    logger.info(f"Retrying tool call (attempt {attempt}/{self.max_retries})...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise ToolError(f"Communication error: {str(e)}")
        
        return None
    
    async def read_resource(self, uri: str) -> Optional[str]:
        """
        Read a resource from the MCP server with retry logic
        
        Args:
            uri: Resource URI
        
        Returns:
            Resource content as string or None if error
            
        Raises:
            ResourceError: If resource access fails
        """
        if not self.initialized:
            raise ResourceError("Client not initialized")
        
        logger.info(f"Reading resource: {uri}")
        
        # Try with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                resource_msg = MCPMessage(
                    id=self._next_id(),
                    method=MCPMessageType.READ_RESOURCE.value,
                    params={"uri": uri}
                )
                
                response = await self._send_message(resource_msg)
                
                if response and "result" in response:
                    contents = response["result"].get("contents", [])
                    if contents and len(contents) > 0:
                        return contents[0].get("text", "")
                    else:
                        logger.warning("Resource returned empty content")
                        return ""
                elif response and "error" in response:
                    error_data = response["error"]
                    error_msg = f"Resource error: {error_data.get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    
                    if attempt < self.max_retries:
                        logger.info(f"Retrying resource read (attempt {attempt}/{self.max_retries})...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise ResourceError(error_msg)
                else:
                    logger.error("Invalid response format")
                    
                    if attempt < self.max_retries:
                        logger.info(f"Retrying resource read (attempt {attempt}/{self.max_retries})...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise ResourceError("Invalid response format")
                    
            except (ConnectionError, CommunicationError) as e:
                logger.error(f"Communication error: {str(e)}")
                
                if attempt < self.max_retries:
                    logger.info(f"Retrying resource read (attempt {attempt}/{self.max_retries})...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise ResourceError(f"Communication error: {str(e)}")
        
        return None
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return self.tools
    
    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources"""
        return self.resources
    
    def get_resource_templates(self) -> List[Dict[str, Any]]:
        """Get list of resource templates"""
        return self.resource_templates
    
    def is_connected(self) -> bool:
        """Check if client is connected and initialized"""
        return self.initialized and self.process is not None
    
    def get_last_activity_time(self) -> float:
        """Get timestamp of last activity"""
        return self.last_activity


class MCPClientManager:
    """
    Enhanced manager for MCP client instances
    Handles client lifecycle and provides high-level operations with improved error handling
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize the client manager with enhanced options
        
        Args:
            max_retries: Maximum number of retries for operations
            retry_delay: Delay between retries in seconds
        """
        self.client: Optional[MCPClient] = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.initialized = False
        
        logger.info(f"MCP Client Manager initialized with retry settings: max_retries={max_retries}, retry_delay={retry_delay}s")
    
    async def start_client(self, server_path: str) -> bool:
        """
        Start an MCP client connected to a server with improved error handling
        
        Args:
            server_path: Path to the server script
        
        Returns:
            True if client started successfully
        """
        try:
            # Create client with server command
            server_command = [sys.executable, server_path]
            self.client = MCPClient(
                server_command,
                max_retries=self.max_retries,
                retry_delay=self.retry_delay
            )
            
            # Connect to server
            success = await self.client.connect()
            
            if success:
                logger.info("MCP client started successfully")
                self.initialized = True
            else:
                logger.error("Failed to start MCP client")
                self.client = None
                self.initialized = False
            
            return success
            
        except Exception as e:
            logger.error(f"Error starting client: {str(e)}")
            logger.error(traceback.format_exc())
            self.client = None
            self.initialized = False
            return False
    
    async def stop_client(self):
        """Stop the MCP client with improved cleanup"""
        if self.client:
            try:
                await self.client.disconnect()
                self.client = None
                self.initialized = False
                logger.info("MCP client stopped")
            except Exception as e:
                logger.error(f"Error stopping client: {str(e)}")
                logger.error(traceback.format_exc())
                self.client = None
                self.initialized = False
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """
        Execute a tool via the MCP client with improved error handling
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
        
        Returns:
            Tool result or None if error
        """
        if not self.client:
            logger.error("No active client")
            return None
        
        try:
            return await self.client.call_tool(tool_name, arguments)
        except ToolError as e:
            logger.error(f"Tool error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error executing tool: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    async def fetch_resource(self, uri: str) -> Optional[str]:
        """
        Fetch a resource via the MCP client with improved error handling
        
        Args:
            uri: Resource URI
        
        Returns:
            Resource content or None if error
        """
        if not self.client:
            logger.error("No active client")
            return None
        
        try:
            return await self.client.read_resource(uri)
        except ResourceError as e:
            logger.error(f"Resource error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching resource: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get current client capabilities with improved error handling
        
        Returns:
            Dictionary with tools, resources, and templates
        """
        if not self.client:
            return {
                "tools": [],
                "resources": [],
                "resource_templates": []
            }
        
        try:
            return {
                "tools": self.client.get_available_tools(),
                "resources": self.client.get_available_resources(),
                "resource_templates": self.client.get_resource_templates()
            }
        except Exception as e:
            logger.error(f"Error getting capabilities: {str(e)}")
            return {
                "tools": [],
                "resources": [],
                "resource_templates": []
            }
    
    def is_connected(self) -> bool:
        """Check if client is connected and initialized"""
        return self.client is not None and self.client.is_connected()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get detailed connection status
        
        Returns:
            Dictionary with connection status details
        """
        if not self.client:
            return {
                "connected": False,
                "initialized": False,
                "message": "No client instance"
            }
        
        connected = self.client.is_connected()
        last_activity = self.client.get_last_activity_time()
        last_activity_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_activity))
        
        return {
            "connected": connected,
            "initialized": self.client.initialized,
            "last_activity": last_activity_str,
            "message": "Connected and operational" if connected else "Disconnected"
        }


# Example usage for testing
async def test_client():
    """Test the enhanced MCP client"""
    import os
    
    # Get path to server
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    server_path = os.path.join(backend_dir, "run_server.py")
    
    # Create client manager
    manager = MCPClientManager(max_retries=2, retry_delay=0.5)
    
    try:
        # Start client
        print("Starting MCP client...")
        success = await manager.start_client(server_path)
        
        if success:
            print("\nClient started successfully!")
            
            # Get capabilities
            capabilities = manager.get_capabilities()
            print(f"\nAvailable tools: {len(capabilities['tools'])}")
            print(f"Available resources: {len(capabilities['resources'])}")
            
            # Test tool call
            print("\n--- Testing Tool Call ---")
            result = await manager.execute_tool(
                "create_task",
                {
                    "title": "Test Task from Enhanced Client",
                    "description": "This task was created via enhanced MCP client",
                    "priority": "high"
                }
            )
            print(f"Tool result: {result}")
            
            # Test resource read
            print("\n--- Testing Resource Read ---")
            resource_content = await manager.fetch_resource("tasks://all")
            print(f"Resource content: {resource_content[:200]}...")  # Show first 200 chars
            
            # Get connection status
            print("\n--- Connection Status ---")
            status = manager.get_connection_status()
            print(f"Status: {status}")
            
        else:
            print("Failed to start client")
    
    finally:
        # Stop client
        await manager.stop_client()
        print("\nClient stopped")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_client())
