#!/usr/bin/env python3
"""
Test script to verify the MCP Learning System components
Run this to check if all components are working correctly
"""

import sys
import os
import asyncio
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from mcp_server.task_storage import TaskStorage, Task
        print("✓ Task storage module imported")
        
        from mcp_server.server import TaskManagementServer
        print("✓ MCP server module imported")
        
        from mcp_client.client import MCPClient, MCPClientManager
        print("✓ MCP client module imported")
        
        from host.api import router
        print("✓ API module imported")
        
        from host.main import app
        print("✓ Main host module imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_task_storage():
    """Test task storage functionality"""
    print("\nTesting task storage...")
    try:
        from mcp_server.task_storage import TaskStorage
        
        storage = TaskStorage()
        
        # Test create
        task = storage.create_task(
            title="Test Task",
            description="Test Description",
            priority="high",
            status="pending"
        )
        print(f"✓ Created task: {task.id}")
        
        # Test get
        retrieved = storage.get_task(task.id)
        assert retrieved.title == "Test Task"
        print("✓ Retrieved task successfully")
        
        # Test update
        updated = storage.update_task(task.id, status="completed")
        assert updated.status == "completed"
        print("✓ Updated task successfully")
        
        # Test list
        tasks = storage.list_tasks()
        assert len(tasks) > 0
        print(f"✓ Listed {len(tasks)} tasks")
        
        # Test delete
        success = storage.delete_task(task.id)
        assert success == True
        print("✓ Deleted task successfully")
        
        return True
    except Exception as e:
        print(f"✗ Task storage error: {e}")
        return False

async def test_mcp_communication():
    """Test MCP client-server communication"""
    print("\nTesting MCP communication...")
    try:
        from mcp_client.client import MCPClientManager
        
        # Create client manager
        manager = MCPClientManager()
        
        # Get server path
        server_path = os.path.join(
            os.path.dirname(__file__),
            "backend",
            "run_server.py"
        )
        
        # Start client (which starts server)
        print("Starting MCP client and server...")
        success = await manager.start_client(server_path)
        
        if not success:
            print("✗ Failed to start MCP client/server")
            return False
        
        print("✓ MCP client connected to server")
        
        # Get capabilities
        capabilities = manager.get_capabilities()
        print(f"✓ Found {len(capabilities['tools'])} tools")
        print(f"✓ Found {len(capabilities['resources'])} resources")
        
        # Test tool execution
        result = await manager.execute_tool(
            "create_task",
            {
                "title": "MCP Test Task",
                "description": "Created via MCP test",
                "priority": "medium"
            }
        )
        
        if result:
            print("✓ Successfully executed create_task tool")
        else:
            print("✗ Failed to execute tool")
            
        # Test resource access
        resource = await manager.fetch_resource("tasks://all")
        if resource:
            tasks = json.loads(resource)
            print(f"✓ Successfully fetched resource: {len(tasks)} tasks")
        else:
            print("✗ Failed to fetch resource")
        
        # Stop client
        await manager.stop_client()
        print("✓ MCP client stopped")
        
        return True
        
    except Exception as e:
        print(f"✗ MCP communication error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")
    
    required_packages = {
        'mcp': 'MCP SDK',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic'
    }
    
    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} not installed")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install -r backend/requirements.txt")
        return False
    
    return True

def check_frontend():
    """Check if frontend dependencies are installed"""
    print("\nChecking frontend...")
    
    node_modules = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "node_modules"
    )
    
    if os.path.exists(node_modules):
        print("✓ Frontend dependencies installed")
        return True
    else:
        print("✗ Frontend dependencies not installed")
        print("Install with: cd frontend && npm install")
        return False

async def main():
    """Run all tests"""
    print("=" * 50)
    print("MCP Learning System - Component Test")
    print("=" * 50)
    
    all_passed = True
    
    # Check dependencies
    if not check_dependencies():
        all_passed = False
        print("\n⚠️  Please install Python dependencies first")
        return
    
    # Test imports
    if not test_imports():
        all_passed = False
        print("\n⚠️  Import tests failed")
        return
    
    # Test task storage
    if not test_task_storage():
        all_passed = False
    
    # Test MCP communication
    if not await test_mcp_communication():
        all_passed = False
    
    # Check frontend
    if not check_frontend():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! System is ready to use.")
        print("\nTo run the system:")
        print("1. Backend: cd backend && python host/main.py")
        print("2. Frontend: cd frontend && npm start")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
