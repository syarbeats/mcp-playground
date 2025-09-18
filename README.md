# MCP Learning System - Enhanced Implementation

A comprehensive implementation of the Model Context Protocol (MCP) demonstrating how MCP works in AI applications. This project provides a complete, working example with an enhanced MCP server, client, host application, and user interface.

## 🎯 Purpose

This project is designed to help developers understand:
- How MCP enables communication between AI applications and external systems
- The architecture and components of an MCP system
- How to implement robust MCP servers and clients
- How to integrate MCP into web applications with best practices

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   React Frontend│ ← User Interface
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│  FastAPI Host   │ ← REST API & MCP Client Integration
└────────┬────────┘
         │ MCP Client
         ↓
┌─────────────────┐
│   MCP Server    │ ← Tools & Resources Provider
└─────────────────┘
```

### Components

1. **Enhanced MCP Server** (`backend/mcp_server/`)
   - Provides tools for task management with improved validation
   - Exposes extended resources via URI patterns
   - Communicates via STDIO transport
   - Implements JSON-RPC protocol with comprehensive error handling

2. **Enhanced MCP Client** (`backend/mcp_client/`)
   - Connects to MCP server with retry logic
   - Handles tool invocation with error recovery
   - Manages resource access with validation
   - Provides robust async communication

3. **Enhanced Host Application** (`backend/host/`)
   - FastAPI web application with improved middleware
   - Integrates MCP client with comprehensive error handling
   - Provides extended REST API endpoints with validation
   - Manages MCP lifecycle with better recovery

4. **Frontend** (`frontend/`)
   - React application updated for the enhanced backend
   - Material-UI components
   - Real-time system status
   - Educational interface

## 📋 Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mcp-learning-system
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install Node dependencies
npm install
```

## 🏃‍♂️ Running the System

### Step 1: Start the Backend (Host + MCP)

There are several ways to run the backend depending on your needs:

#### Standard Mode

```bash
# From the backend directory
cd backend

# Activate virtual environment if not already active
source venv/bin/activate  # macOS/Linux
# or
# venv\Scripts\activate  # Windows

# Run the enhanced host application
python run_host.py
```

#### Debug Mode (for detailed logging)

```bash
# Run with debug logging enabled
python run_host.py --debug
```

#### Mock Mode (for testing without a real MCP server)

```bash
# Run with mock MCP client
python run_host.py --mock
```

#### Combined Options

```bash
# Run with both debug logging and mock client
python run_host.py --mock --debug
```

The backend will start on `http://localhost:8001`

- API Documentation: `http://localhost:8001/docs`
- OpenAPI Schema: `http://localhost:8001/openapi.json`

### Running the MCP Server Standalone

If you want to run the MCP server separately (for development or testing):

```bash
# Run the MCP server standalone
python run_server.py
```

With debug logging:

```bash
# Run with debug logging enabled
python run_server.py --debug
```

### Step 2: Start the Frontend

```bash
# From the frontend directory (in a new terminal)
cd frontend

# Start the React development server
npm start
```

The frontend will start on `http://localhost:3000`

## 🎮 Using the System

### System Tab
- View MCP system status with enhanced details
- Check connection status with last activity time
- See available tools and resources
- Monitor comprehensive task statistics

### Tasks Tab
- Create new tasks with validation
- View all tasks with pagination
- Edit existing tasks
- Delete tasks
- Filter by status or priority
- Search tasks

### Learn Tab
- Understand MCP communication flow
- View example MCP messages
- Learn about the protocol
- Explore the enhanced architecture

## 🔍 Understanding MCP Flow

### Example: Creating a Task

1. **User Action**: Click "New Task" in the React frontend
2. **Frontend**: Sends HTTP POST to `/api/tasks`
3. **Host (FastAPI)**: Receives request, validates data
4. **MCP Client**: Formats JSON-RPC message for `create_task` tool
5. **MCP Server**: Executes tool with validation, creates task in storage
6. **Response Flow**: Server → Client → Host → Frontend
7. **UI Update**: New task appears in the list

### MCP Protocol Example

**Tool Call Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_task",
    "arguments": {
      "title": "Learn MCP",
      "description": "Study the protocol",
      "priority": "high",
      "status": "pending"
    }
  }
}
```

**Tool Call Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Task created successfully!\n{...task data...}"
      }
    ]
  }
}
```

## 📚 MCP Concepts Demonstrated

### Tools
Executable functions exposed by the MCP server:
- `create_task` - Create a new task with validation
- `list_tasks` - List all tasks with filtering and pagination
- `get_task` - Get a specific task by ID
- `update_task` - Update an existing task with validation
- `delete_task` - Delete a task
- `get_statistics` - Get comprehensive task statistics

### Resources
Data accessible via URI patterns:
- `tasks://all` - All tasks (static resource)
- `tasks://statistics` - Task statistics (static resource)
- `tasks://pending` - Pending tasks (static resource)
- `tasks://in_progress` - In-progress tasks (static resource)
- `tasks://completed` - Completed tasks (static resource)
- `task://{task_id}` - Individual task (resource template)
- `tasks://status/{status}` - Tasks by status (resource template)
- `tasks://priority/{priority}` - Tasks by priority (resource template)

### Transport
- **STDIO**: Communication via standard input/output
- **JSON-RPC**: Protocol for remote procedure calls

## 🛠️ Development

### Running the MCP Server Standalone

```bash
# Run the MCP server standalone
cd backend
python run_server.py [--debug] [--server-name NAME]
```

Options:
- `--debug`: Enable debug logging
- `--server-name`: Name of the MCP server (default: task-management-server)

### Running the Host Application with Options

```bash
# Run the host application with options
cd backend
python run_host.py [--port PORT] [--host HOST] [--reload] [--debug] [--mock] [--server-path PATH]
```

Options:
- `--port`: Port to run the host application on (default: 8001)
- `--host`: Host to bind the application to (default: 0.0.0.0)
- `--reload`: Enable auto-reload for development
- `--debug`: Enable debug logging
- `--mock`: Use mock MCP client for testing
- `--server-path`: Path to the MCP server script

### Testing MCP Client

```bash
# Run the client test
cd backend
python -m mcp_client.client
```

### API Testing

#### Using the Interactive Documentation

Use the interactive API documentation at `http://localhost:8001/docs` to test endpoints directly.

#### Using PowerShell Commands

You can also test the API using PowerShell commands:

**Create a Task:**
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @{
    "title" = "Test Task"
    "description" = "This is a test task"
    "priority" = "high"
    "status" = "pending"
} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8001/api/tasks" -Method Post -Headers $headers -Body $body
```

**List All Tasks:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8001/api/tasks" -Method Get
```

**Get a Specific Task:**
```powershell
# Replace {task_id} with the actual task ID
Invoke-WebRequest -Uri "http://localhost:8001/api/tasks/{task_id}" -Method Get
```

**Update a Task:**
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @{
    "title" = "Updated Task"
    "description" = "This task has been updated"
    "priority" = "medium"
    "status" = "in_progress"
} | ConvertTo-Json
# Replace {task_id} with the actual task ID
Invoke-WebRequest -Uri "http://localhost:8001/api/tasks/{task_id}" -Method Put -Headers $headers -Body $body
```

**Delete a Task:**
```powershell
# Replace {task_id} with the actual task ID
Invoke-WebRequest -Uri "http://localhost:8001/api/tasks/{task_id}" -Method Delete
```

## 📁 Project Structure

```
mcp-learning-system/
├── backend/
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── server.py          # Enhanced MCP Server implementation
│   │   └── task_storage.py    # Enhanced task storage with validation
│   ├── mcp_client/
│   │   ├── __init__.py
│   │   └── client.py          # Enhanced MCP Client implementation
│   ├── host/
│   │   ├── __init__.py
│   │   ├── main.py            # Enhanced FastAPI application
│   │   └── api.py             # Enhanced REST API endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── run_server.py          # MCP server entry point
│   ├── run_host.py            # Host application entry point
│   └── README.md              # Backend documentation
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── SystemStatus.js
│   │   │   ├── TaskList.js
│   │   │   └── TaskForm.js
│   │   ├── services/
│   │   │   └── api.js         # Updated API service layer
│   │   ├── App.js             # Main app component
│   │   └── index.js           # Entry point
│   └── package.json           # Node dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Backend Configuration

Environment variables:
- `HOST`: Host to bind to (default: 0.0.0.0)
- `PORT`: Port to bind to (default: 8001)
- `RELOAD`: Enable auto-reload for development (default: false)
- `MCP_USE_MOCK`: Use mock MCP client for testing (default: false)
- `MCP_SERVER_PATH`: Path to the MCP server script

### Frontend Configuration

Environment variables:
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8001)

## 🐛 Troubleshooting

### Backend Issues

1. **MCP Client not connecting**
   - Check logs in `mcp_client.log` and `host_app.log`
   - Ensure Python path is correct
   - Check that all dependencies are installed
   - Verify no other process is using port 8001

2. **Import errors**
   - Make sure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

1. **Cannot connect to backend**
   - Ensure backend is running on port 8001
   - Check CORS settings in backend
   - Verify API URL in frontend/.env

2. **Dependencies issues**
   - Clear node_modules: `rm -rf node_modules`
   - Reinstall: `npm install`

## 📖 Learning Resources

### In the Application
- **System Tab**: View real-time MCP system status
- **Learn Tab**: Interactive explanation of MCP concepts
- **API Docs**: http://localhost:8001/docs

### Code Comments
All code files include detailed comments explaining:
- MCP concepts
- Implementation decisions
- Protocol details
- Best practices
- Error handling strategies

### Key Files to Study
1. `backend/mcp_server/server.py` - Enhanced MCP server implementation
2. `backend/mcp_client/client.py` - Enhanced MCP client implementation
3. `backend/host/api.py` - Enhanced REST API integration
4. `frontend/src/services/api.js` - Updated frontend API layer

## 🤝 Contributing

Contributions that improve the system are welcome:
- Better documentation
- Additional examples
- Bug fixes
- UI improvements
- Performance optimizations

## 📄 License

This project is for educational purposes. Feel free to use and modify for learning.

## 🙏 Acknowledgments

- Built using the Model Context Protocol (MCP) specification
- FastAPI for the backend framework
- React and Material-UI for the frontend
- Python MCP SDK for protocol implementation

## 💡 Next Steps

After understanding this implementation, you can:
1. Extend the MCP server with new tools
2. Add more resource types
3. Implement different transport mechanisms
4. Create your own MCP servers for different domains
5. Integrate MCP into your own applications

---

**Happy Learning! 🚀**

For questions or issues, please refer to the code comments or explore the interactive documentation.
