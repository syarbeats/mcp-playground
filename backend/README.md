# MCP Backend Components

This directory contains the backend components of the MCP Learning System, including the MCP server, client, and host application.

## Components

### 1. MCP Server (`mcp_server/`)

The MCP Server provides tools and resources for task management with improved validation and error handling.

- **server.py**: Main server implementation with JSON-RPC protocol support
- **task_storage.py**: Task storage with validation and comprehensive error handling

### 2. MCP Client (`mcp_client/`)

The MCP Client connects to the MCP server and handles communication with robust error recovery.

- **client.py**: Main client implementation with retry logic and error handling
- **mock_client.py**: Mock implementation for testing without a real server

### 3. Host Application (`host/`)

The Host Application is a FastAPI web application that provides REST API endpoints and integrates with the MCP client.

- **main.py**: FastAPI application with improved middleware and error handling
- **api.py**: REST API endpoints with validation and comprehensive error handling

## Running the Backend

### Running the Host Application

```bash
python run_host.py [--port PORT] [--host HOST] [--reload] [--debug] [--mock] [--server-path PATH]
```

Options:
- `--port`: Port to run the host application on (default: 8001)
- `--host`: Host to bind the application to (default: 0.0.0.0)
- `--reload`: Enable auto-reload for development
- `--debug`: Enable debug logging
- `--mock`: Use mock MCP client for testing
- `--server-path`: Path to the MCP server script

### Running the MCP Server Standalone

```bash
python run_server.py [--debug] [--server-name NAME]
```

Options:
- `--debug`: Enable debug logging
- `--server-name`: Name of the MCP server (default: task-management-server)

## API Documentation

When the host application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI Schema: http://localhost:8001/openapi.json

## Testing

### Testing the MCP Client

```bash
python -m mcp_client.client
```

### Testing with Mock Client

For testing without a real MCP server, you can use the mock client:

```bash
python run_host.py --mock
```

## API Endpoints

### Task Management

- `GET /api/tasks`: List all tasks with filtering and pagination
- `POST /api/tasks`: Create a new task
- `GET /api/tasks/{task_id}`: Get a specific task
- `PUT /api/tasks/{task_id}`: Update a task
- `DELETE /api/tasks/{task_id}`: Delete a task

### System Information

- `GET /api/system/status`: Get system status
- `GET /api/system/capabilities`: Get MCP capabilities
- `GET /api/system/statistics`: Get task statistics

### Educational Endpoints

- `GET /api/learn/mcp-flow`: Get MCP communication flow explanation
- `GET /api/learn/mcp-messages`: Get MCP message examples
- `GET /api/learn/architecture`: Get architecture explanation

### Resource Endpoints

- `GET /api/resources/tasks`: Get all tasks via resource
- `GET /api/resources/task/{task_id}`: Get a specific task via resource
- `GET /api/resources/tasks/status/{status}`: Get tasks by status
- `GET /api/resources/tasks/priority/{priority}`: Get tasks by priority

## Environment Variables

- `HOST`: Host to bind to (default: 0.0.0.0)
- `PORT`: Port to bind to (default: 8001)
- `RELOAD`: Enable auto-reload for development (default: false)
- `MCP_USE_MOCK`: Use mock MCP client for testing (default: false)
- `MCP_SERVER_PATH`: Path to the MCP server script
