# MCP Frontend

This directory contains the frontend components of the MCP Learning System, built with React and Material-UI.

## Overview

The frontend provides a user interface for interacting with the MCP system, including:

- Task management (create, view, edit, delete tasks)
- System status monitoring
- Educational content about MCP

## Components

### Main Components

- **App.js**: Main application component
- **components/**: UI components
  - **TaskList.js**: Displays and manages the list of tasks
  - **TaskForm.js**: Form for creating and editing tasks
  - **SystemStatus.js**: Displays system status information
- **services/**: Service layer
  - **api.js**: API service for communicating with the backend

## Setup and Running

### Prerequisites

- Node.js 16 or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install
```

### Running the Development Server

```bash
# Start the development server
npm start
```

The frontend will start on `http://localhost:3000`

### Building for Production

```bash
# Build the frontend for production
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Configuration

The frontend can be configured using environment variables in a `.env` file:

```
REACT_APP_API_URL=http://localhost:8001
```

## Features

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

## API Integration

The frontend communicates with the backend using the API service in `services/api.js`. This service provides methods for:

- Task management (create, list, get, update, delete)
- System information (status, capabilities, statistics)
- Educational content (MCP flow, messages, architecture)
- Resource access (tasks, task by ID, tasks by status, tasks by priority)

## Error Handling

The frontend includes comprehensive error handling for API requests, including:

- Connection errors
- Server errors
- Validation errors
- Not found errors

## Responsive Design

The frontend is designed to be responsive and work on various screen sizes, from mobile to desktop.

## Browser Support

The frontend supports modern browsers, including:

- Chrome
- Firefox
- Safari
- Edge
