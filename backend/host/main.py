"""
Enhanced Host Application
FastAPI application that integrates MCP client and provides REST API with improved error handling and performance
"""

import asyncio
import os
import sys
import logging
import time
import traceback
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client.client import MCPClientManager
from mcp_client.mock_client import MockMCPClientManager
from host.api import router, set_mcp_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler("host_app.log")
    ]
)
logger = logging.getLogger(__name__)

# Global MCP client manager
mcp_manager = MCPClientManager(max_retries=3, retry_delay=1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle with improved error handling
    Start MCP client on startup, stop on shutdown
    """
    logger.info("Starting enhanced host application...")
    
    # Get server path from environment or use default
    server_path = os.getenv("MCP_SERVER_PATH", os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "run_server.py"
    ))
    
    try:
        # Initialize MCP client
        logger.info(f"Initializing MCP client with server at: {server_path}")
        
        # Check if we should use a real client or mock for testing
        use_mock = os.getenv("MCP_USE_MOCK", "false").lower() == "true"
        
        if use_mock:
            logger.info("Using mock MCP client for testing")
            # Replace the manager with a mock implementation
            global mcp_manager
            mcp_manager = MockMCPClientManager()
        else:
            # Start the client
            success = await mcp_manager.start_client(server_path)
            
            if not success:
                logger.warning("Failed to initialize MCP client, will operate in degraded mode")
        
        # Set the manager in the API module
        set_mcp_manager(mcp_manager)
        
        # Continue with application startup
        logger.info("Host application started successfully")
        
        yield
        
        # Cleanup on shutdown
        logger.info("Shutting down host application...")
        
        if not use_mock:
            await mcp_manager.stop_client()
            
        logger.info("Host application stopped")
        
    except Exception as e:
        logger.error(f"Error during application lifecycle: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Still need to yield to allow FastAPI to continue
        yield
        
        logger.info("Host application stopped after error")


# Create FastAPI application with improved configuration
app = FastAPI(
    title="Enhanced MCP Learning System - Host Application",
    description="""
    Enhanced educational implementation of Model Context Protocol (MCP) Host Application.
    
    This host application demonstrates:
    - Robust integration with MCP client
    - Comprehensive REST API endpoints for task management
    - Efficient MCP tools and resources usage
    - Detailed system status monitoring
    - Improved error handling and recovery
    
    ## Architecture
    
    The system consists of:
    1. **MCP Server**: Provides tools and resources for task management
    2. **MCP Client**: Connects to and communicates with the MCP server
    3. **Host Application**: This FastAPI app that provides REST API
    4. **Frontend**: React application for user interaction
    
    ## MCP Concepts Demonstrated
    
    - **Tools**: Executable functions (create_task, update_task, etc.)
    - **Resources**: Data access via URIs (tasks://all, task://{id})
    - **Resource Templates**: Dynamic resources with parameters
    - **STDIO Transport**: Communication via standard input/output
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS for frontend access with improved security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Alternative dev port
        "http://localhost:8080",  # Production build
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Add GZip compression for better performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routes
app.include_router(router)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information"""
    start_time = time.time()
    
    # Generate request ID
    request_id = f"{int(start_time * 1000)}"
    
    # Log request
    logger.info(f"Request {request_id} started: {request.method} {request.url.path}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Request {request_id} completed: {response.status_code} ({process_time:.4f}s)")
        
        # Add timing header
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        return response
    except Exception as e:
        # Log error
        logger.error(f"Request {request_id} failed: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": str(e)
            }
        )


@app.get("/")
async def root():
    """
    Root endpoint - provides system information
    """
    return {
        "application": "Enhanced MCP Learning System - Host",
        "version": "2.0.0",
        "description": "Educational MCP implementation with improved features",
        "endpoints": {
            "api_docs": "/docs",
            "openapi_spec": "/openapi.json",
            "system_status": "/api/system/status",
            "tasks": "/api/tasks",
            "capabilities": "/api/system/capabilities"
        },
        "mcp_info": {
            "protocol": "Model Context Protocol",
            "transport": "STDIO",
            "architecture": "Client-Server with Host intermediary"
        },
        "features": {
            "error_handling": "Comprehensive error handling and recovery",
            "performance": "Optimized for better performance",
            "logging": "Detailed logging for debugging and monitoring",
            "security": "Improved security with CORS configuration"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint with detailed status
    """
    if not mcp_manager:
        return {
            "status": "degraded",
            "mcp_client": "not_initialized",
            "message": "MCP client manager not initialized"
        }
    
    # Get connection status
    connection_status = mcp_manager.get_connection_status()
    
    # Determine overall status
    if connection_status["connected"]:
        status = "healthy"
        message = "System fully operational"
    else:
        status = "degraded"
        message = connection_status["message"]
    
    return {
        "status": status,
        "mcp_client": "connected" if connection_status["connected"] else "disconnected",
        "message": message,
        "details": connection_status
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors with improved logging
    """
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred",
            "type": type(exc).__name__,
            "message": str(exc)
        }
    )


# Educational endpoints for learning
@app.get("/api/learn/mcp-flow")
async def explain_mcp_flow():
    """
    Educational endpoint explaining the MCP flow
    """
    return {
        "title": "MCP Communication Flow",
        "description": "How data flows through the MCP system",
        "steps": [
            {
                "step": 1,
                "component": "Frontend (React)",
                "action": "User clicks 'Create Task' button",
                "details": "React app sends HTTP POST to /api/tasks"
            },
            {
                "step": 2,
                "component": "Host (FastAPI)",
                "action": "Receives HTTP request",
                "details": "Validates request and prepares MCP tool call"
            },
            {
                "step": 3,
                "component": "MCP Client",
                "action": "Sends tool call message",
                "details": "Formats JSON-RPC message and sends via STDIO"
            },
            {
                "step": 4,
                "component": "MCP Server",
                "action": "Executes tool",
                "details": "Processes create_task tool and returns result"
            },
            {
                "step": 5,
                "component": "MCP Client",
                "action": "Receives response",
                "details": "Parses JSON-RPC response from server"
            },
            {
                "step": 6,
                "component": "Host (FastAPI)",
                "action": "Processes MCP response",
                "details": "Formats response for REST API"
            },
            {
                "step": 7,
                "component": "Frontend (React)",
                "action": "Updates UI",
                "details": "Displays new task to user"
            }
        ],
        "key_concepts": {
            "JSON-RPC": "Protocol for remote procedure calls using JSON",
            "STDIO Transport": "Communication via standard input/output streams",
            "Tools": "Executable functions exposed by MCP server",
            "Resources": "Data accessible via URI patterns"
        },
        "error_handling": {
            "retry_logic": "Client implements retry logic for failed operations",
            "validation": "Comprehensive validation at all levels",
            "logging": "Detailed logging for debugging and monitoring"
        }
    }


@app.get("/api/learn/mcp-messages")
async def show_mcp_messages():
    """
    Educational endpoint showing example MCP messages
    """
    return {
        "title": "MCP Message Examples",
        "description": "Examples of actual MCP protocol messages",
        "examples": [
            {
                "type": "Tool Discovery",
                "direction": "Client -> Server",
                "message": {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
            },
            {
                "type": "Tool Discovery Response",
                "direction": "Server -> Client",
                "message": {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "tools": [
                            {
                                "name": "create_task",
                                "description": "Create a new task",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "description": {"type": "string"}
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "type": "Tool Call",
                "direction": "Client -> Server",
                "message": {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "create_task",
                        "arguments": {
                            "title": "Learn MCP",
                            "description": "Study the protocol"
                        }
                    }
                }
            },
            {
                "type": "Tool Call Error",
                "direction": "Server -> Client",
                "message": {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "error": {
                        "code": 400,
                        "message": "Validation error: Title cannot be empty"
                    }
                }
            },
            {
                "type": "Resource Read",
                "direction": "Client -> Server",
                "message": {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "resources/read",
                    "params": {
                        "uri": "tasks://all"
                    }
                }
            }
        ]
    }


@app.get("/api/learn/architecture")
async def explain_architecture():
    """
    Educational endpoint explaining the system architecture
    """
    return {
        "title": "MCP System Architecture",
        "description": "Overview of the MCP system components and their interactions",
        "components": [
            {
                "name": "MCP Server",
                "role": "Provides tools and resources",
                "features": [
                    "Task management tools",
                    "Data resources",
                    "Resource templates",
                    "Validation",
                    "Error handling"
                ],
                "implementation": "Python with MCP SDK"
            },
            {
                "name": "MCP Client",
                "role": "Communicates with MCP server",
                "features": [
                    "Connection management",
                    "Message formatting",
                    "Tool invocation",
                    "Resource access",
                    "Retry logic",
                    "Error handling"
                ],
                "implementation": "Python with asyncio"
            },
            {
                "name": "Host Application",
                "role": "Provides REST API for frontend",
                "features": [
                    "API endpoints",
                    "Request validation",
                    "Response formatting",
                    "Error handling",
                    "Logging",
                    "Performance optimization"
                ],
                "implementation": "Python with FastAPI"
            },
            {
                "name": "Frontend",
                "role": "User interface",
                "features": [
                    "Task management UI",
                    "System status display",
                    "Error handling",
                    "User feedback"
                ],
                "implementation": "React with Material-UI"
            }
        ],
        "communication": [
            {
                "from": "Frontend",
                "to": "Host Application",
                "protocol": "HTTP/REST",
                "format": "JSON"
            },
            {
                "from": "Host Application",
                "to": "MCP Client",
                "protocol": "Direct function calls",
                "format": "Native objects"
            },
            {
                "from": "MCP Client",
                "to": "MCP Server",
                "protocol": "JSON-RPC over STDIO",
                "format": "JSON"
            }
        ]
    }


def main():
    """
    Main entry point for running the host application
    """
    # Get configuration from environment variables
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting FastAPI host on {host}:{port} (reload={reload})")
    logger.info("API documentation available at http://localhost:8001/docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=reload
    )


if __name__ == "__main__":
    main()
