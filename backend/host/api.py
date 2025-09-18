"""
Enhanced API Endpoints Module
Defines all REST API endpoints for the host application with improved error handling and validation
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
import json
import logging
import time
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

# Create API router with improved configuration
router = APIRouter(
    prefix="/api",
    tags=["MCP Operations"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "model": dict
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "MCP client not connected",
            "model": dict
        }
    }
)


# Enhanced Pydantic models for request/response with validation
class TaskCreateRequest(BaseModel):
    """Request model for creating a task with enhanced validation"""
    title: str = Field(..., description="Task title", min_length=1, max_length=100)
    description: str = Field(..., description="Task description", min_length=1, max_length=1000)
    priority: str = Field("medium", description="Task priority (low, medium, high)")
    status: str = Field("pending", description="Task status (pending, in_progress, completed)")
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority field"""
        valid_priorities = ['low', 'medium', 'high']
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status field"""
        valid_statuses = ['pending', 'in_progress', 'completed']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v


class TaskUpdateRequest(BaseModel):
    """Request model for updating a task with enhanced validation"""
    title: Optional[str] = Field(None, description="New task title", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="New task description", min_length=1, max_length=1000)
    priority: Optional[str] = Field(None, description="New priority (low, medium, high)")
    status: Optional[str] = Field(None, description="New status (pending, in_progress, completed)")
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority field"""
        if v is None:
            return v
        valid_priorities = ['low', 'medium', 'high']
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status field"""
        if v is None:
            return v
        valid_statuses = ['pending', 'in_progress', 'completed']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v


class TaskResponse(BaseModel):
    """Response model for a task"""
    id: str
    title: str
    description: str
    status: str
    priority: str
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    """Response model for task list with metadata"""
    tasks: List[TaskResponse]
    count: int
    filter: Optional[str] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None


class SystemStatusResponse(BaseModel):
    """Response model for system status with enhanced details"""
    mcp_server: str
    mcp_client: str
    available_tools: int
    available_resources: int
    message: str
    last_activity: Optional[str] = None
    uptime: Optional[float] = None
    version: str = "2.0.0"


class MCPCapabilitiesResponse(BaseModel):
    """Response model for MCP capabilities"""
    tools: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    resource_templates: List[Dict[str, Any]]


class ErrorResponse(BaseModel):
    """Response model for errors"""
    detail: str
    type: Optional[str] = None
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Global reference to MCP client manager (will be set by main.py)
mcp_manager = None


def set_mcp_manager(manager):
    """Set the MCP client manager instance"""
    global mcp_manager
    mcp_manager = manager


# Dependency for checking MCP client connection
async def get_mcp_client():
    """
    Dependency to check if MCP client is connected
    
    Raises:
        HTTPException: If MCP client is not connected
    """
    if not mcp_manager or not mcp_manager.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP client not connected"
        )
    return mcp_manager


# Task endpoints
@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task via MCP with validation"
)
async def create_task(
    request: TaskCreateRequest,
    client: Any = Depends(get_mcp_client)
):
    """
    Create a new task via MCP with enhanced error handling
    
    This endpoint demonstrates how the host application uses the MCP client
    to execute tools on the MCP server.
    """
    try:
        # Call the create_task tool via MCP
        logger.info(f"Creating task: {request.title}")
        
        result = await client.execute_tool(
            "create_task",
            {
                "title": request.title,
                "description": request.description,
                "priority": request.priority,
                "status": request.status
            }
        )
        
        if not result:
            logger.error("Failed to create task: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task: No result from MCP server"
            )
        
        # Parse the result
        try:
            # Check if result contains a success message followed by JSON
            if "Task created successfully" in result:
                # Extract JSON part
                json_start = result.find('{')
                if json_start != -1:
                    task_json = result[json_start:]
                    task_data = json.loads(task_json)
                    return TaskResponse(**task_data)
            
            # Try parsing the entire result as JSON
            task_data = json.loads(result)
            return TaskResponse(**task_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP response: {e}")
            logger.error(f"Raw response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid response format from MCP server"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/tasks",
    response_model=TaskListResponse,
    summary="List all tasks",
    description="List all tasks with optional filtering and pagination"
)
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status (pending, in_progress, completed)"),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Items per page", ge=1, le=100),
    client: Any = Depends(get_mcp_client)
):
    """
    List all tasks via MCP with enhanced filtering and pagination
    
    Optionally filter by status and paginate results
    """
    try:
        # Validate status if provided
        if status:
            valid_statuses = ['pending', 'in_progress', 'completed']
            if status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}. Must be one of {valid_statuses}"
                )
        
        # Call the list_tasks tool via MCP
        logger.info(f"Listing tasks with filter: {status}, page: {page}, page_size: {page_size}")
        
        arguments = {}
        if status:
            arguments["status"] = status
        
        result = await client.execute_tool("list_tasks", arguments)
        
        if not result:
            logger.error("Failed to list tasks: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list tasks: No result from MCP server"
            )
        
        # Parse the result
        try:
            result_data = json.loads(result)
            
            # Check if result is already in the expected format
            if isinstance(result_data, dict) and "tasks" in result_data:
                tasks_data = result_data["tasks"]
            else:
                # Assume result is a list of tasks
                tasks_data = result_data
            
            # Apply pagination
            total_tasks = len(tasks_data)
            total_pages = (total_tasks + page_size - 1) // page_size
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_tasks)
            
            paginated_tasks = tasks_data[start_idx:end_idx]
            
            # Create response
            return TaskListResponse(
                tasks=[TaskResponse(**task) for task in paginated_tasks],
                count=len(paginated_tasks),
                filter=status,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP response: {e}")
            logger.error(f"Raw response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid response format from MCP server"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get a specific task",
    description="Get a specific task by ID"
)
async def get_task(
    task_id: str = Path(..., description="Task ID"),
    client: Any = Depends(get_mcp_client)
):
    """
    Get a specific task by ID via MCP with enhanced error handling
    """
    try:
        # Call the get_task tool via MCP
        logger.info(f"Getting task with ID: {task_id}")
        
        result = await client.execute_tool("get_task", {"task_id": task_id})
        
        if not result:
            logger.error(f"Failed to get task {task_id}: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get task {task_id}: No result from MCP server"
            )
        
        # Check for "not found" message
        if "not found" in result.lower():
            logger.warning(f"Task not found: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        # Parse the result
        try:
            task_data = json.loads(result)
            return TaskResponse(**task_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP response: {e}")
            logger.error(f"Raw response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid response format from MCP server"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update an existing task by ID"
)
async def update_task(
    task_id: str = Path(..., description="Task ID"),
    request: TaskUpdateRequest = None,
    client: Any = Depends(get_mcp_client)
):
    """
    Update a task via MCP with enhanced validation and error handling
    """
    try:
        # Build arguments for MCP tool
        logger.info(f"Updating task with ID: {task_id}")
        
        arguments = {"task_id": task_id}
        
        if request:
            if request.title is not None:
                arguments["title"] = request.title
            if request.description is not None:
                arguments["description"] = request.description
            if request.priority is not None:
                arguments["priority"] = request.priority
            if request.status is not None:
                arguments["status"] = request.status
        
        # Call the update_task tool via MCP
        result = await client.execute_tool("update_task", arguments)
        
        if not result:
            logger.error(f"Failed to update task {task_id}: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update task {task_id}: No result from MCP server"
            )
        
        # Check for "not found" message
        if "not found" in result.lower():
            logger.warning(f"Task not found: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        # Parse the result
        try:
            # Check if result contains a success message followed by JSON
            if "Task updated successfully" in result:
                # Extract JSON part
                json_start = result.find('{')
                if json_start != -1:
                    task_json = result[json_start:]
                    task_data = json.loads(task_json)
                    return TaskResponse(**task_data)
            
            # Try parsing the entire result as JSON
            task_data = json.loads(result)
            return TaskResponse(**task_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP response: {e}")
            logger.error(f"Raw response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid response format from MCP server"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a task",
    description="Delete a task by ID"
)
async def delete_task(
    task_id: str = Path(..., description="Task ID"),
    client: Any = Depends(get_mcp_client)
):
    """
    Delete a task via MCP with enhanced error handling
    """
    try:
        # Call the delete_task tool via MCP
        logger.info(f"Deleting task with ID: {task_id}")
        
        result = await client.execute_tool("delete_task", {"task_id": task_id})
        
        if not result:
            logger.error(f"Failed to delete task {task_id}: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete task {task_id}: No result from MCP server"
            )
        
        # Check for "not found" message
        if "not found" in result.lower():
            logger.warning(f"Task not found: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        return {"message": f"Task {task_id} deleted successfully"}
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# System endpoints
@router.get(
    "/system/status",
    response_model=SystemStatusResponse,
    summary="Get system status",
    description="Get the current system status with detailed information"
)
async def get_system_status():
    """
    Get the current system status with enhanced details
    
    This shows the status of MCP components and available capabilities
    """
    start_time = time.time()
    
    if not mcp_manager:
        return SystemStatusResponse(
            mcp_server="Not initialized",
            mcp_client="Not initialized",
            available_tools=0,
            available_resources=0,
            message="MCP system not initialized",
            uptime=0,
            version="2.0.0"
        )
    
    # Get connection status
    connection_status = mcp_manager.get_connection_status()
    
    if not mcp_manager.is_connected():
        return SystemStatusResponse(
            mcp_server="Disconnected",
            mcp_client="Disconnected",
            available_tools=0,
            available_resources=0,
            message="MCP client not connected to server",
            last_activity=connection_status.get("last_activity"),
            uptime=0,
            version="2.0.0"
        )
    
    # Get capabilities
    capabilities = mcp_manager.get_capabilities()
    
    return SystemStatusResponse(
        mcp_server="Connected",
        mcp_client="Connected",
        available_tools=len(capabilities["tools"]),
        available_resources=len(capabilities["resources"]),
        message="MCP system operational",
        last_activity=connection_status.get("last_activity"),
        uptime=time.time() - start_time,
        version="2.0.0"
    )


@router.get(
    "/system/capabilities",
    response_model=MCPCapabilitiesResponse,
    summary="Get MCP capabilities",
    description="Get detailed information about available MCP tools and resources"
)
async def get_mcp_capabilities(
    client: Any = Depends(get_mcp_client)
):
    """
    Get detailed MCP capabilities with enhanced error handling
    
    Returns all available tools, resources, and resource templates
    """
    try:
        capabilities = client.get_capabilities()
        return MCPCapabilitiesResponse(**capabilities)
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting capabilities: {str(e)}"
        )


@router.get(
    "/system/statistics",
    summary="Get task statistics",
    description="Get comprehensive statistics about tasks"
)
async def get_statistics(
    client: Any = Depends(get_mcp_client)
):
    """
    Get task statistics via MCP with enhanced error handling
    """
    try:
        # Call the get_statistics tool via MCP
        logger.info("Getting task statistics")
        
        result = await client.execute_tool("get_statistics", {})
        
        if not result:
            logger.error("Failed to get statistics: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get statistics: No result from MCP server"
            )
        
        # Parse the result
        try:
            stats = json.loads(result)
            
            # Add timestamp
            stats["timestamp"] = datetime.utcnow().isoformat()
            
            return stats
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP response: {e}")
            logger.error(f"Raw response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid response format from MCP server"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Resource endpoints (demonstrating MCP resource access)
@router.get(
    "/resources/tasks",
    summary="Get all tasks via resource",
    description="Get all tasks using MCP resource instead of tool"
)
async def get_all_tasks_resource(
    client: Any = Depends(get_mcp_client)
):
    """
    Get all tasks via MCP resource (not tool) with enhanced error handling
    
    This demonstrates accessing MCP resources directly
    """
    try:
        # Read the tasks://all resource
        logger.info("Fetching tasks resource")
        
        result = await client.fetch_resource("tasks://all")
        
        if not result:
            logger.error("Failed to fetch resource: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch resource: No result from MCP server"
            )
        
        # Parse the result
        try:
            tasks = json.loads(result)
            return tasks
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse resource content: {e}")
            logger.error(f"Raw response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid resource format"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error fetching resource: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/resources/task/{task_id}",
    summary="Get a task via resource",
    description="Get a specific task using MCP resource template"
)
async def get_task_resource(
    task_id: str = Path(..., description="Task ID"),
    client: Any = Depends(get_mcp_client)
):
    """
    Get a specific task via MCP resource template with enhanced error handling
    
    This demonstrates using MCP resource templates with parameters
    """
    try:
        # Read the task resource using template
        logger.info(f"Fetching task resource for ID: {task_id}")
        
        result = await client.fetch_resource(f"task://{task_id}")
        
        if not result:
            logger.error(f"Failed to fetch resource for task {task_id}: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch resource for task {task_id}: No result from MCP server"
            )
        
        # Parse the result
        try:
            task_data = json.loads(result)
            
            # Check for error
            if isinstance(task_data, dict) and "error" in task_data:
                error_msg = task_data["error"]
                if "not found" in error_msg.lower():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=error_msg
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=error_msg
                    )
            
            return task_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse resource content: {e}")
            logger.error(f"Raw response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid resource format"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error fetching resource: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/resources/tasks/status/{status}",
    summary="Get tasks by status via resource",
    description="Get tasks filtered by status using MCP resource template"
)
async def get_tasks_by_status_resource(
    status: str = Path(..., description="Task status (pending, in_progress, completed)"),
    client: Any = Depends(get_mcp_client)
):
    """
    Get tasks filtered by status via MCP resource template with enhanced error handling
    
    This demonstrates using MCP resource templates with parameters
    """
    try:
        # Validate status
        valid_statuses = ['pending', 'in_progress', 'completed']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}. Must be one of {valid_statuses}"
            )
        
        # Read the tasks by status resource using template
        logger.info(f"Fetching tasks resource for status: {status}")
        
        result = await client.fetch_resource(f"tasks://status/{status}")
        
        if not result:
            logger.error(f"Failed to fetch resource for status {status}: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch resource for status {status}: No result from MCP server"
            )
        
        # Parse the result
        try:
            tasks_data = json.loads(result)
            
            # Check for error
            if isinstance(tasks_data, dict) and "error" in tasks_data:
                error_msg = tasks_data["error"]
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )
            
            return tasks_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse resource content: {e}")
            logger.error(f"Raw response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid resource format"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error fetching resource: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/resources/tasks/priority/{priority}",
    summary="Get tasks by priority via resource",
    description="Get tasks filtered by priority using MCP resource template"
)
async def get_tasks_by_priority_resource(
    priority: str = Path(..., description="Task priority (low, medium, high)"),
    client: Any = Depends(get_mcp_client)
):
    """
    Get tasks filtered by priority via MCP resource template with enhanced error handling
    
    This demonstrates using MCP resource templates with parameters
    """
    try:
        # Validate priority
        valid_priorities = ['low', 'medium', 'high']
        if priority not in valid_priorities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority: {priority}. Must be one of {valid_priorities}"
            )
        
        # Read the tasks by priority resource using template
        logger.info(f"Fetching tasks resource for priority: {priority}")
        
        result = await client.fetch_resource(f"tasks://priority/{priority}")
        
        if not result:
            logger.error(f"Failed to fetch resource for priority {priority}: No result from MCP server")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch resource for priority {priority}: No result from MCP server"
            )
        
        # Parse the result
        try:
            tasks_data = json.loads(result)
            
            # Check for error
            if isinstance(tasks_data, dict) and "error" in tasks_data:
                error_msg = tasks_data["error"]
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )
            
            return tasks_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse resource content: {e}")
            logger.error(f"Raw response: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid resource format"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error fetching resource: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
