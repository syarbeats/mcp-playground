"""
Mock MCP Client Implementation
Provides mock data for testing without a real MCP server
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockMCPClientManager:
    """
    Mock implementation of MCPClientManager for testing
    Provides mock data for all API endpoints
    """
    
    def __init__(self):
        """Initialize the mock client manager"""
        self.initialized = True
        self.client = "mock"
        self.last_activity = time.time()
        
        # Mock tasks
        self.tasks = [
            {
                "id": str(uuid.uuid4()),
                "title": "Mock Task 1",
                "description": "This is a mock task for testing",
                "status": "pending",
                "priority": "high",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Mock Task 2",
                "description": "Another mock task for testing",
                "status": "in_progress",
                "priority": "medium",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Mock Task 3",
                "description": "A completed mock task",
                "status": "completed",
                "priority": "low",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]
        
        logger.info("Mock MCP Client Manager initialized with sample tasks")
    
    def is_connected(self) -> bool:
        """Check if client is connected and initialized"""
        return True
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get detailed connection status
        
        Returns:
            Dictionary with connection status details
        """
        return {
            "connected": True,
            "initialized": True,
            "last_activity": datetime.fromtimestamp(self.last_activity).strftime("%Y-%m-%d %H:%M:%S"),
            "message": "Mock client connected and operational"
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get current client capabilities
        
        Returns:
            Dictionary with tools, resources, and templates
        """
        return {
            "tools": [
                {
                    "name": "create_task",
                    "description": "Create a new task with validation"
                },
                {
                    "name": "list_tasks",
                    "description": "List all tasks with filtering and pagination"
                },
                {
                    "name": "get_task",
                    "description": "Get a specific task by ID"
                },
                {
                    "name": "update_task",
                    "description": "Update an existing task with validation"
                },
                {
                    "name": "delete_task",
                    "description": "Delete a task by ID"
                },
                {
                    "name": "get_statistics",
                    "description": "Get comprehensive task statistics"
                }
            ],
            "resources": [
                {
                    "name": "All Tasks",
                    "uri": "tasks://all"
                },
                {
                    "name": "Task Statistics",
                    "uri": "tasks://statistics"
                },
                {
                    "name": "Pending Tasks",
                    "uri": "tasks://pending"
                },
                {
                    "name": "In Progress Tasks",
                    "uri": "tasks://in_progress"
                },
                {
                    "name": "Completed Tasks",
                    "uri": "tasks://completed"
                }
            ],
            "resource_templates": [
                {
                    "name": "Individual Task",
                    "uriTemplate": "task://{task_id}"
                },
                {
                    "name": "Tasks by Status",
                    "uriTemplate": "tasks://status/{status}"
                },
                {
                    "name": "Tasks by Priority",
                    "uriTemplate": "tasks://priority/{priority}"
                }
            ]
        }
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """
        Execute a mock tool
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
        
        Returns:
            Tool result or None if error
        """
        self.last_activity = time.time()
        logger.info(f"Mock executing tool: {tool_name} with arguments: {arguments}")
        
        if tool_name == "create_task":
            return await self._create_task(arguments)
        elif tool_name == "list_tasks":
            return await self._list_tasks(arguments)
        elif tool_name == "get_task":
            return await self._get_task(arguments)
        elif tool_name == "update_task":
            return await self._update_task(arguments)
        elif tool_name == "delete_task":
            return await self._delete_task(arguments)
        elif tool_name == "get_statistics":
            return await self._get_statistics(arguments)
        else:
            logger.warning(f"Unknown tool: {tool_name}")
            return None
    
    async def fetch_resource(self, uri: str) -> Optional[str]:
        """
        Fetch a mock resource
        
        Args:
            uri: Resource URI
        
        Returns:
            Resource content or None if error
        """
        self.last_activity = time.time()
        logger.info(f"Mock fetching resource: {uri}")
        
        if uri == "tasks://all":
            return json.dumps(self.tasks)
        elif uri == "tasks://statistics":
            return json.dumps(self._calculate_statistics())
        elif uri == "tasks://pending":
            return json.dumps([t for t in self.tasks if t["status"] == "pending"])
        elif uri == "tasks://in_progress":
            return json.dumps([t for t in self.tasks if t["status"] == "in_progress"])
        elif uri == "tasks://completed":
            return json.dumps([t for t in self.tasks if t["status"] == "completed"])
        elif uri.startswith("task://"):
            task_id = uri.replace("task://", "")
            task = next((t for t in self.tasks if t["id"] == task_id), None)
            if task:
                return json.dumps(task)
            else:
                return json.dumps({"error": f"Task not found: {task_id}"})
        elif uri.startswith("tasks://status/"):
            status = uri.replace("tasks://status/", "")
            if status in ["pending", "in_progress", "completed"]:
                return json.dumps([t for t in self.tasks if t["status"] == status])
            else:
                return json.dumps({"error": f"Invalid status: {status}"})
        elif uri.startswith("tasks://priority/"):
            priority = uri.replace("tasks://priority/", "")
            if priority in ["low", "medium", "high"]:
                return json.dumps([t for t in self.tasks if t["priority"] == priority])
            else:
                return json.dumps({"error": f"Invalid priority: {priority}"})
        else:
            logger.warning(f"Unknown resource URI: {uri}")
            return json.dumps({"error": f"Unknown resource URI: {uri}"})
    
    async def _create_task(self, arguments: Dict[str, Any]) -> str:
        """Create a mock task"""
        # Validate required arguments
        if "title" not in arguments:
            return "Error: Missing required argument 'title'"
        if "description" not in arguments:
            return "Error: Missing required argument 'description'"
        
        # Create task
        task = {
            "id": str(uuid.uuid4()),
            "title": arguments["title"],
            "description": arguments["description"],
            "status": arguments.get("status", "pending"),
            "priority": arguments.get("priority", "medium"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add to tasks
        self.tasks.append(task)
        
        return f"Task created successfully!\n{json.dumps(task, indent=2)}"
    
    async def _list_tasks(self, arguments: Dict[str, Any]) -> str:
        """List mock tasks"""
        # Filter by status if provided
        status = arguments.get("status")
        if status:
            filtered_tasks = [t for t in self.tasks if t["status"] == status]
        else:
            filtered_tasks = self.tasks
        
        # Create response
        response = {
            "tasks": filtered_tasks,
            "count": len(filtered_tasks),
            "filter": status if status else "all"
        }
        
        return json.dumps(response, indent=2)
    
    async def _get_task(self, arguments: Dict[str, Any]) -> str:
        """Get a mock task"""
        # Validate required arguments
        if "task_id" not in arguments:
            return "Error: Missing required argument 'task_id'"
        
        # Find task
        task_id = arguments["task_id"]
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        
        if task:
            return json.dumps(task, indent=2)
        else:
            return f"Task not found: {task_id}"
    
    async def _update_task(self, arguments: Dict[str, Any]) -> str:
        """Update a mock task"""
        # Validate required arguments
        if "task_id" not in arguments:
            return "Error: Missing required argument 'task_id'"
        
        # Find task
        task_id = arguments["task_id"]
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        
        if not task:
            return f"Task not found: {task_id}"
        
        # Update task
        if "title" in arguments:
            task["title"] = arguments["title"]
        if "description" in arguments:
            task["description"] = arguments["description"]
        if "status" in arguments:
            task["status"] = arguments["status"]
        if "priority" in arguments:
            task["priority"] = arguments["priority"]
        
        # Update timestamp
        task["updated_at"] = datetime.utcnow().isoformat()
        
        return f"Task updated successfully!\n{json.dumps(task, indent=2)}"
    
    async def _delete_task(self, arguments: Dict[str, Any]) -> str:
        """Delete a mock task"""
        # Validate required arguments
        if "task_id" not in arguments:
            return "Error: Missing required argument 'task_id'"
        
        # Find task
        task_id = arguments["task_id"]
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        
        if not task:
            return f"Task not found: {task_id}"
        
        # Delete task
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        
        return f"Task deleted successfully: {task_id}"
    
    async def _get_statistics(self, arguments: Dict[str, Any]) -> str:
        """Get mock statistics"""
        return json.dumps(self._calculate_statistics(), indent=2)
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate mock statistics"""
        # Count tasks by status
        status_counts = {
            "pending": len([t for t in self.tasks if t["status"] == "pending"]),
            "in_progress": len([t for t in self.tasks if t["status"] == "in_progress"]),
            "completed": len([t for t in self.tasks if t["status"] == "completed"])
        }
        
        # Count tasks by priority
        priority_counts = {
            "low": len([t for t in self.tasks if t["priority"] == "low"]),
            "medium": len([t for t in self.tasks if t["priority"] == "medium"]),
            "high": len([t for t in self.tasks if t["priority"] == "high"])
        }
        
        # Calculate completion rate
        completion_rate = 0
        if self.tasks:
            completion_rate = (status_counts["completed"] / len(self.tasks)) * 100
        
        # Get most recent tasks
        recent_tasks = sorted(self.tasks, key=lambda t: t["created_at"], reverse=True)[:5]
        recent_task_ids = [t["id"] for t in recent_tasks]
        
        return {
            "total": len(self.tasks),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "completion_rate": round(completion_rate, 2),
            "recent_task_ids": recent_task_ids
        }
