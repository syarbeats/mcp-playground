/**
 * Application Entry Point
 * Renders the React app to the DOM
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Create root element
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render app
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Log MCP system information to console (educational)
console.log('%c🚀 MCP Learning System Started', 'color: #1976d2; font-size: 16px; font-weight: bold;');
console.log('%cModel Context Protocol Educational Implementation', 'color: #666; font-size: 12px;');
console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ccc;');
console.log('%cArchitecture:', 'color: #1976d2; font-weight: bold;');
console.log('  1. Frontend (React) → You are here!');
console.log('  2. Host (FastAPI) → http://localhost:8000');
console.log('  3. MCP Client (Python) → Connects to MCP Server');
console.log('  4. MCP Server (Python) → Provides tools & resources');
console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ccc;');
console.log('%cOpen the Network tab to see MCP communication flow', 'color: #666; font-style: italic;');
console.log('%cAPI Documentation: http://localhost:8000/docs', 'color: #666; font-style: italic;');
