"""
Task Storage Module
Enhanced implementation of in-memory task storage with improved validation and error handling
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception raised for validation errors in task operations"""
    pass


@dataclass
class Task:
    """
    Enhanced Task data model
    Represents a single task in the system with improved validation
    """
    id: str
    title: str
    description: str
    status: str  # 'pending', 'in_progress', 'completed'
    created_at: str
    updated_at: str
    priority: str  # 'low', 'medium', 'high'
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary with validation"""
        # Validate required fields
        required_fields = ['id', 'title', 'description', 'status', 'created_at', 'updated_at', 'priority']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate status
        valid_statuses = ['pending', 'in_progress', 'completed']
        if data['status'] not in valid_statuses:
            raise ValidationError(f"Invalid status: {data['status']}. Must be one of {valid_statuses}")
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high']
        if data['priority'] not in valid_priorities:
            raise ValidationError(f"Invalid priority: {data['priority']}. Must be one of {valid_priorities}")
        
        return cls(**data)


class TaskStorage:
    """
    Enhanced in-memory task storage
    This class manages all task CRUD operations with improved validation and error handling
    """
    
    def __init__(self):
        """Initialize empty task storage"""
        self.tasks: Dict[str, Task] = {}
        self._initialize_sample_tasks()
        logger.info("Task storage initialized with sample tasks")
    
    def _initialize_sample_tasks(self):
        """Add some sample tasks for demonstration"""
        sample_tasks = [
            {
                "title": "Learn MCP Protocol",
                "description": "Understand how Model Context Protocol works and its key concepts",
                "status": "in_progress",
                "priority": "high"
            },
            {
                "title": "Build MCP Server",
                "description": "Implement a functional MCP server with tools and resources",
                "status": "completed",
                "priority": "high"
            },
            {
                "title": "Test Integration",
                "description": "Test the complete MCP system integration with all components",
                "status": "pending",
                "priority": "medium"
            },
            {
                "title": "Write Documentation",
                "description": "Create comprehensive documentation for the MCP system",
                "status": "pending",
                "priority": "medium"
            },
            {
                "title": "Performance Optimization",
                "description": "Optimize the MCP system for better performance",
                "status": "pending",
                "priority": "low"
            }
        ]
        
        for task_data in sample_tasks:
            self.create_task(
                title=task_data["title"],
                description=task_data["description"],
                status=task_data["status"],
                priority=task_data["priority"]
            )
    
    def _validate_status(self, status: str) -> None:
        """Validate task status"""
        valid_statuses = ['pending', 'in_progress', 'completed']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status: {status}. Must be one of {valid_statuses}")
    
    def _validate_priority(self, priority: str) -> None:
        """Validate task priority"""
        valid_priorities = ['low', 'medium', 'high']
        if priority not in valid_priorities:
            raise ValidationError(f"Invalid priority: {priority}. Must be one of {valid_priorities}")
    
    def _validate_task_id(self, task_id: str) -> None:
        """Validate task ID exists"""
        if task_id not in self.tasks:
            raise ValidationError(f"Task not found with ID: {task_id}")
    
    def create_task(self, title: str, description: str, 
                   status: str = "pending", priority: str = "medium") -> Task:
        """
        Create a new task with validation
        
        Args:
            title: Task title
            description: Task description
            status: Task status (pending, in_progress, completed)
            priority: Task priority (low, medium, high)
        
        Returns:
            Created task object
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate inputs
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")
        
        if not description or not description.strip():
            raise ValidationError("Description cannot be empty")
        
        self._validate_status(status)
        self._validate_priority(priority)
        
        # Create task
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        task = Task(
            id=task_id,
            title=title.strip(),
            description=description.strip(),
            status=status,
            created_at=now,
            updated_at=now,
            priority=priority
        )
        
        self.tasks[task_id] = task
        logger.info(f"Created task with ID: {task_id}")
        return task
    
    def get_task(self, task_id: str) -> Task:
        """
        Get a task by ID
        
        Args:
            task_id: Task ID
        
        Returns:
            Task object
            
        Raises:
            ValidationError: If task not found
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValidationError(f"Task not found with ID: {task_id}")
        
        return task
    
    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        """
        List all tasks, optionally filtered by status
        
        Args:
            status: Optional status filter
        
        Returns:
            List of tasks
            
        Raises:
            ValidationError: If status is invalid
        """
        if status:
            self._validate_status(status)
            tasks = [t for t in self.tasks.values() if t.status == status]
        else:
            tasks = list(self.tasks.values())
        
        # Sort by created_at (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks
    
    def update_task(self, task_id: str, **updates) -> Task:
        """
        Update a task with validation
        
        Args:
            task_id: Task ID
            **updates: Fields to update
        
        Returns:
            Updated task
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate task exists
        self._validate_task_id(task_id)
        task = self.tasks[task_id]
        
        # Validate updates
        allowed_fields = {'title', 'description', 'status', 'priority'}
        for field, value in updates.items():
            if field not in allowed_fields:
                raise ValidationError(f"Cannot update field: {field}")
            
            if field == 'status':
                self._validate_status(value)
            elif field == 'priority':
                self._validate_priority(value)
            elif field in ['title', 'description'] and (not value or not value.strip()):
                raise ValidationError(f"{field.capitalize()} cannot be empty")
        
        # Apply updates
        for field, value in updates.items():
            if field in ['title', 'description']:
                setattr(task, field, value.strip())
            else:
                setattr(task, field, value)
        
        # Update timestamp
        task.updated_at = datetime.utcnow().isoformat()
        logger.info(f"Updated task with ID: {task_id}")
        
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task
        
        Args:
            task_id: Task ID
        
        Returns:
            True if deleted
            
        Raises:
            ValidationError: If task not found
        """
        # Validate task exists
        self._validate_task_id(task_id)
        
        # Delete task
        del self.tasks[task_id]
        logger.info(f"Deleted task with ID: {task_id}")
        return True
    
    def get_all_tasks_json(self) -> str:
        """
        Get all tasks as JSON string
        
        Returns:
            JSON string of all tasks
        """
        tasks_list = [task.to_dict() for task in self.tasks.values()]
        # Sort by created_at (newest first)
        tasks_list.sort(key=lambda t: t['created_at'], reverse=True)
        return json.dumps(tasks_list, indent=2)
    
    def get_task_json(self, task_id: str) -> Optional[str]:
        """
        Get a single task as JSON string
        
        Args:
            task_id: Task ID
        
        Returns:
            JSON string of task if found, None otherwise
        """
        try:
            task = self.get_task(task_id)
            return json.dumps(task.to_dict(), indent=2)
        except ValidationError:
            return None
    
    def get_tasks_by_status_json(self, status: str) -> str:
        """
        Get tasks filtered by status as JSON string
        
        Args:
            status: Status to filter by
        
        Returns:
            JSON string of filtered tasks
            
        Raises:
            ValidationError: If status is invalid
        """
        try:
            tasks = self.list_tasks(status=status)
            tasks_list = [task.to_dict() for task in tasks]
            return json.dumps(tasks_list, indent=2)
        except ValidationError as e:
            return json.dumps({"error": str(e)})
    
    def get_statistics(self) -> dict:
        """
        Get task statistics
        
        Returns:
            Dictionary with task statistics
        """
        tasks = list(self.tasks.values())
        
        # Count tasks by status
        status_counts = {
            "pending": len([t for t in tasks if t.status == "pending"]),
            "in_progress": len([t for t in tasks if t.status == "in_progress"]),
            "completed": len([t for t in tasks if t.status == "completed"])
        }
        
        # Count tasks by priority
        priority_counts = {
            "low": len([t for t in tasks if t.priority == "low"]),
            "medium": len([t for t in tasks if t.priority == "medium"]),
            "high": len([t for t in tasks if t.priority == "high"])
        }
        
        # Calculate completion rate
        completion_rate = 0
        if tasks:
            completion_rate = (status_counts["completed"] / len(tasks)) * 100
        
        # Get most recent tasks
        recent_tasks = sorted(tasks, key=lambda t: t.created_at, reverse=True)[:5]
        recent_task_ids = [t.id for t in recent_tasks]
        
        stats = {
            "total": len(tasks),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "completion_rate": round(completion_rate, 2),
            "recent_task_ids": recent_task_ids
        }
        
        return stats


# Global storage instance (singleton pattern)
_storage_instance = None

def get_storage() -> TaskStorage:
    """
    Get the global task storage instance
    
    Returns:
        TaskStorage instance
    """
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = TaskStorage()
    return _storage_instance
