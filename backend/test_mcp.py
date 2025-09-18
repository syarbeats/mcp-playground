"""
Simple test script to check MCP SDK installation
"""

import sys
import importlib.util

def check_module(module_name):
    """Check if a module is installed and can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"Module {module_name} is NOT installed")
            return False
        else:
            print(f"Module {module_name} is installed")
            module = importlib.import_module(module_name)
            print(f"Version: {getattr(module, '__version__', 'unknown')}")
            print(f"Path: {module.__file__}")
            return True
    except Exception as e:
        print(f"Error checking {module_name}: {e}")
        return False

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print("\nChecking MCP SDK installation:")
    
    # Check main MCP module
    check_module("mcp")
    
    # Check specific MCP modules
    check_module("mcp.server")
    check_module("mcp.server.stdio")
    
    # Check other dependencies
    check_module("fastapi")
    check_module("uvicorn")
    check_module("asyncio")
