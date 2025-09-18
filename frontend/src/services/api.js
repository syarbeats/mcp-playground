/**
 * API Service
 * Handles all communication with the backend host application
 */

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging (educational purposes)
api.interceptors.request.use(
  (config) => {
    console.log('🚀 MCP Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
api.interceptors.response.use(
  (response) => {
    console.log('✅ MCP Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.status, error.config?.url);
    return Promise.reject(error);
  }
);

/**
 * Task Management API
 */
export const taskAPI = {
  // Create a new task
  create: async (taskData) => {
    const response = await api.post('/api/tasks', taskData);
    return response.data;
  },

  // List all tasks with pagination and filtering
  list: async (status = null, page = 1, pageSize = 10) => {
    const params = { page, page_size: pageSize };
    if (status) params.status = status;
    const response = await api.get('/api/tasks', { params });
    return response.data;
  },

  // Get a specific task
  get: async (taskId) => {
    const response = await api.get(`/api/tasks/${taskId}`);
    return response.data;
  },

  // Update a task
  update: async (taskId, updates) => {
    const response = await api.put(`/api/tasks/${taskId}`, updates);
    return response.data;
  },

  // Delete a task
  delete: async (taskId) => {
    const response = await api.delete(`/api/tasks/${taskId}`);
    return response.data;
  },
};

/**
 * System API
 */
export const systemAPI = {
  // Get system status
  getStatus: async () => {
    const response = await api.get('/api/system/status');
    return response.data;
  },

  // Get MCP capabilities
  getCapabilities: async () => {
    const response = await api.get('/api/system/capabilities');
    return response.data;
  },

  // Get task statistics
  getStatistics: async () => {
    const response = await api.get('/api/system/statistics');
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

/**
 * Resource API (demonstrating MCP resources)
 */
export const resourceAPI = {
  // Get all tasks via resource
  getAllTasksResource: async () => {
    const response = await api.get('/api/resources/tasks');
    return response.data;
  },

  // Get specific task via resource template
  getTaskResource: async (taskId) => {
    const response = await api.get(`/api/resources/task/${taskId}`);
    return response.data;
  },
  
  // Get tasks by status via resource
  getTasksByStatus: async (status) => {
    const response = await api.get(`/api/resources/tasks/status/${status}`);
    return response.data;
  },
  
  // Get tasks by priority via resource
  getTasksByPriority: async (priority) => {
    const response = await api.get(`/api/resources/tasks/priority/${priority}`);
    return response.data;
  },
};

/**
 * Educational API
 */
export const learnAPI = {
  // Get MCP flow explanation
  getMCPFlow: async () => {
    const response = await api.get('/api/learn/mcp-flow');
    return response.data;
  },

  // Get MCP message examples
  getMCPMessages: async () => {
    const response = await api.get('/api/learn/mcp-messages');
    return response.data;
  },
  
  // Get architecture explanation
  getArchitecture: async () => {
    const response = await api.get('/api/learn/architecture');
    return response.data;
  },
};

// Error handler helper
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error
    const message = error.response.data?.detail || error.response.data?.message || 'Server error occurred';
    const status = error.response.status;
    
    if (status === 503) {
      return 'MCP system is not connected. Please ensure the backend is running.';
    } else if (status === 404) {
      return 'Resource not found';
    } else if (status === 400) {
      return `Invalid request: ${message}`;
    } else if (status === 500) {
      return `Server error: ${message}`;
    }
    
    return message;
  } else if (error.request) {
    // Request made but no response
    return 'Cannot connect to server. Please ensure the backend is running on port 8001.';
  } else {
    // Error in request setup
    return error.message || 'An unexpected error occurred';
  }
};

export default api;
