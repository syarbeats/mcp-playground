#!/usr/bin/env python3
"""
Enhanced MCP Server Implementation
Provides tools and resources for task management with improved error handling and logging
"""

import asyncio
import json
import sys
import logging
import traceback
from typing import Any, Dict, List, Optional, Union
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    Resource,
    ResourceTemplate,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .task_storage import get_storage, Task, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("mcp_server.log")
    ]
)
logger = logging.getLogger(__name__)


class TaskManagementServer:
    """
    Enhanced MCP Server for Task Management
    Provides tools and resources with improved error handling and performance
    """
    
    def __init__(self, server_name: str = "task-management-server"):
        """
        Initialize the MCP server
        
        Args:
            server_name: Name of the server
        """
        self.storage = get_storage()
        self.server = Server(server_name)
        self.setup_handlers()
        logger.info(f"Task Management MCP Server '{server_name}' initialized")
    
    def setup_handlers(self):
        """Set up all MCP protocol handlers with improved error handling"""
        
        # Tool handlers
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """
            List all available tools
            This is called by the MCP client to discover available tools
            """
            logger.info("Listing available tools")
            return [
                Tool(
                    name="create_task",
                    description="Create a new task with validation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title (required)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description (required)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Task priority",
                                "default": "medium"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                                "description": "Task status",
                                "default": "pending"
                            }
                        },
                        "required": ["title", "description"]
                    }
                ),
                Tool(
                    name="list_tasks",
                    description="List all tasks with optional status filter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                                "description": "Filter by status (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_task",
                    description="Get a specific task by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID (required)"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="update_task",
                    description="Update an existing task with validation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID (required)"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description (optional)"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                                "description": "New status (optional)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "New priority (optional)"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="delete_task",
                    description="Delete a task by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to delete (required)"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="get_statistics",
                    description="Get comprehensive task statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """
            Handle tool execution with improved error handling
            This is called when the MCP client wants to execute a tool
            
            Args:
                name: Tool name
                arguments: Tool arguments
                
            Returns:
                List of content items (text, images, etc.)
            """
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            try:
                # Create task
                if name == "create_task":
                    # Extract and validate required arguments
                    if "title" not in arguments:
                        return [TextContent(
                            type="text",
                            text="Error: Missing required argument 'title'"
                        )]
                    
                    if "description" not in arguments:
                        return [TextContent(
                            type="text",
                            text="Error: Missing required argument 'description'"
                        )]
                    
                    # Create task with validation
                    try:
                        task = self.storage.create_task(
                            title=arguments["title"],
                            description=arguments["description"],
                            status=arguments.get("status", "pending"),
                            priority=arguments.get("priority", "medium")
                        )
                        
                        return [TextContent(
                            type="text",
                            text=f"Task created successfully!\n{json.dumps(task.to_dict(), indent=2)}"
                        )]
                    except ValidationError as e:
                        logger.warning(f"Validation error in create_task: {str(e)}")
                        return [TextContent(
                            type="text",
                            text=f"Validation error: {str(e)}"
                        )]
                
                # List tasks
                elif name == "list_tasks":
                    try:
                        status_filter = arguments.get("status")
                        tasks = self.storage.list_tasks(status=status_filter)
                        tasks_data = [task.to_dict() for task in tasks]
                        
                        # Add summary information
                        result = {
                            "tasks": tasks_data,
                            "count": len(tasks_data),
                            "filter": status_filter if status_filter else "all"
                        }
                        
                        return [TextContent(
                            type="text",
                            text=json.dumps(result, indent=2)
                        )]
                    except ValidationError as e:
                        logger.warning(f"Validation error in list_tasks: {str(e)}")
                        return [TextContent(
                            type="text",
                            text=f"Validation error: {str(e)}"
                        )]
                
                # Get task
                elif name == "get_task":
                    # Validate required arguments
                    if "task_id" not in arguments:
                        return [TextContent(
                            type="text",
                            text="Error: Missing required argument 'task_id'"
                        )]
                    
                    try:
                        task = self.storage.get_task(arguments["task_id"])
                        return [TextContent(
                            type="text",
                            text=json.dumps(task.to_dict(), indent=2)
                        )]
                    except ValidationError as e:
                        logger.warning(f"Task not found: {arguments['task_id']}")
                        return [TextContent(
                            type="text",
                            text=f"Task not found: {arguments['task_id']}"
                        )]
                
                # Update task
                elif name == "update_task":
                    # Validate required arguments
                    if "task_id" not in arguments:
                        return [TextContent(
                            type="text",
                            text="Error: Missing required argument 'task_id'"
                        )]
                    
                    try:
                        # Extract task_id and prepare updates
                        task_id = arguments.pop("task_id")
                        updates = {k: v for k, v in arguments.items() if v is not None}
                        
                        # Update task
                        task = self.storage.update_task(task_id, **updates)
                        
                        return [TextContent(
                            type="text",
                            text=f"Task updated successfully!\n{json.dumps(task.to_dict(), indent=2)}"
                        )]
                    except ValidationError as e:
                        logger.warning(f"Validation error in update_task: {str(e)}")
                        return [TextContent(
                            type="text",
                            text=f"Validation error: {str(e)}"
                        )]
                
                # Delete task
                elif name == "delete_task":
                    # Validate required arguments
                    if "task_id" not in arguments:
                        return [TextContent(
                            type="text",
                            text="Error: Missing required argument 'task_id'"
                        )]
                    
                    try:
                        # Delete task
                        success = self.storage.delete_task(arguments["task_id"])
                        
                        return [TextContent(
                            type="text",
                            text=f"Task deleted successfully: {arguments['task_id']}"
                        )]
                    except ValidationError as e:
                        logger.warning(f"Task not found: {arguments['task_id']}")
                        return [TextContent(
                            type="text",
                            text=f"Task not found: {arguments['task_id']}"
                        )]
                
                # Get statistics
                elif name == "get_statistics":
                    stats = self.storage.get_statistics()
                    return [TextContent(
                        type="text",
                        text=json.dumps(stats, indent=2)
                    )]
                
                # Unknown tool
                else:
                    logger.warning(f"Unknown tool requested: {name}")
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                # Log the full exception with traceback
                logger.error(f"Error executing tool {name}: {str(e)}")
                logger.error(traceback.format_exc())
                
                return [TextContent(
                    type="text",
                    text=f"Error executing tool: {str(e)}"
                )]
        
        # Resource handlers
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """
            List static resources
            These are resources with fixed URIs
            """
            logger.info("Listing available resources")
            return [
                Resource(
                    uri="tasks://all",
                    name="All Tasks",
                    description="Get all tasks in the system",
                    mimeType="application/json"
                ),
                Resource(
                    uri="tasks://statistics",
                    name="Task Statistics",
                    description="Get statistics about tasks",
                    mimeType="application/json"
                ),
                Resource(
                    uri="tasks://pending",
                    name="Pending Tasks",
                    description="Get all pending tasks",
                    mimeType="application/json"
                ),
                Resource(
                    uri="tasks://in_progress",
                    name="In Progress Tasks",
                    description="Get all in-progress tasks",
                    mimeType="application/json"
                ),
                Resource(
                    uri="tasks://completed",
                    name="Completed Tasks",
                    description="Get all completed tasks",
                    mimeType="application/json"
                )
            ]
        
        @self.server.list_resource_templates()
        async def list_resource_templates() -> List[ResourceTemplate]:
            """
            List resource templates
            These are dynamic resources with URI templates
            """
            logger.info("Listing available resource templates")
            return [
                ResourceTemplate(
                    uriTemplate="task://{task_id}",
                    name="Individual Task",
                    description="Get a specific task by ID",
                    mimeType="application/json"
                ),
                ResourceTemplate(
                    uriTemplate="tasks://status/{status}",
                    name="Tasks by Status",
                    description="Get tasks filtered by status",
                    mimeType="application/json"
                ),
                ResourceTemplate(
                    uriTemplate="tasks://priority/{priority}",
                    name="Tasks by Priority",
                    description="Get tasks filtered by priority",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> Union[str, Dict[str, Any]]:
            """
            Read a resource by URI with improved error handling
            This handles both static resources and template-based resources
            
            Args:
                uri: Resource URI
                
            Returns:
                Resource content as string or dictionary
            """
            logger.info(f"Resource requested: {uri}")
            
            try:
                # Handle static resources
                if uri == "tasks://all":
                    return self.storage.get_all_tasks_json()
                
                elif uri == "tasks://statistics":
                    stats = self.storage.get_statistics()
                    return json.dumps(stats, indent=2)
                
                elif uri == "tasks://pending":
                    return self.storage.get_tasks_by_status_json("pending")
                
                elif uri == "tasks://in_progress":
                    return self.storage.get_tasks_by_status_json("in_progress")
                
                elif uri == "tasks://completed":
                    return self.storage.get_tasks_by_status_json("completed")
                
                # Handle template-based resources
                elif uri.startswith("task://"):
                    # Extract task ID from URI
                    task_id = uri.replace("task://", "")
                    task_json = self.storage.get_task_json(task_id)
                    
                    if task_json:
                        return task_json
                    else:
                        return json.dumps({"error": f"Task not found: {task_id}"})
                
                elif uri.startswith("tasks://status/"):
                    # Extract status from URI
                    status = uri.replace("tasks://status/", "")
                    
                    try:
                        return self.storage.get_tasks_by_status_json(status)
                    except ValidationError as e:
                        return json.dumps({"error": str(e)})
                
                elif uri.startswith("tasks://priority/"):
                    # Extract priority from URI
                    priority = uri.replace("tasks://priority/", "")
                    
                    # Validate priority
                    valid_priorities = ["low", "medium", "high"]
                    if priority not in valid_priorities:
                        return json.dumps({"error": f"Invalid priority: {priority}. Must be one of {valid_priorities}"})
                    
                    # Get tasks with the specified priority
                    tasks = [t for t in self.storage.list_tasks() if t.priority == priority]
                    tasks_data = [task.to_dict() for task in tasks]
                    
                    return json.dumps(tasks_data, indent=2)
                
                # Unknown resource
                else:
                    logger.warning(f"Unknown resource URI: {uri}")
                    return json.dumps({"error": f"Unknown resource URI: {uri}"})
                    
            except Exception as e:
                # Log the full exception with traceback
                logger.error(f"Error reading resource {uri}: {str(e)}")
                logger.error(traceback.format_exc())
                
                return json.dumps({"error": str(e)})
    
    async def run(self):
        """
        Run the MCP server
        Uses stdio transport for communication
        """
        logger.info("Starting MCP server on stdio transport...")
        
        try:
            # Run the server with stdio transport
            # This allows the server to communicate via standard input/output
            async with stdio_server() as (read_stream, write_stream):
                logger.info("Stdio server created successfully")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Error running server: {str(e)}")
            logger.error(traceback.format_exc())
            raise


async def main():
    """Main entry point with improved error handling"""
    try:
        # Create and run the server
        server = TaskManagementServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    # Print startup messages to stderr instead of stdout
    print("Starting enhanced MCP Task Management Server...", file=sys.stderr)
    print("This server communicates via stdio (standard input/output)", file=sys.stderr)
    print("It provides tools and resources for task management", file=sys.stderr)
    print("-" * 50, file=sys.stderr)
    
    # Run the async main function
    asyncio.run(main())
