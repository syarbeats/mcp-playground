/**
 * Main App Component
 * Root component for the MCP Learning System
 */

import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Paper,
  AppBar,
  Toolbar,
  IconButton,
  Tabs,
  Tab,
  Alert,
  Link,
  Tooltip,
} from '@mui/material';
import {
  GitHub,
  School,
  Architecture,
  Code,
  Info,
} from '@mui/icons-material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import SystemStatus from './components/SystemStatus';
import TaskList from './components/TaskList';
import { learnAPI } from './services/api';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [mcpFlow, setMcpFlow] = useState(null);
  const [mcpMessages, setMcpMessages] = useState(null);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    
    // Load educational content when switching to Learn tab
    if (newValue === 2 && !mcpFlow) {
      loadEducationalContent();
    }
  };

  const loadEducationalContent = async () => {
    try {
      const [flow, messages] = await Promise.all([
        learnAPI.getMCPFlow(),
        learnAPI.getMCPMessages(),
      ]);
      setMcpFlow(flow);
      setMcpMessages(messages);
    } catch (error) {
      console.error('Failed to load educational content:', error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        {/* App Bar */}
        <AppBar position="static">
          <Toolbar>
            <School sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              MCP Learning System
            </Typography>
            <Tooltip title="View source on GitHub">
              <IconButton
                color="inherit"
                onClick={() => window.open('https://github.com', '_blank')}
              >
                <GitHub />
              </IconButton>
            </Tooltip>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          {/* Header */}
          <Box mb={3}>
            <Typography variant="h4" gutterBottom>
              Model Context Protocol - Educational Implementation
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Learn how MCP enables communication between AI applications and external systems
            </Typography>
          </Box>

          {/* Tabs */}
          <Paper sx={{ mb: 3 }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="main tabs">
              <Tab icon={<Architecture />} label="System" />
              <Tab icon={<Code />} label="Tasks" />
              <Tab icon={<School />} label="Learn" />
            </Tabs>
          </Paper>

          {/* Tab Panels */}
          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <SystemStatus />
              </Grid>
              <Grid item xs={12}>
                <Alert severity="info">
                  <Typography variant="subtitle2" gutterBottom>
                    <strong>System Architecture Overview</strong>
                  </Typography>
                  <Typography variant="body2">
                    This system demonstrates the MCP architecture with four key components:
                  </Typography>
                  <ul style={{ marginTop: 8, marginBottom: 0 }}>
                    <li><strong>MCP Server:</strong> Provides tools and resources (Python, STDIO transport)</li>
                    <li><strong>MCP Client:</strong> Connects to server and executes operations (Python)</li>
                    <li><strong>Host Application:</strong> FastAPI backend that integrates the MCP client</li>
                    <li><strong>Frontend:</strong> React UI for user interaction (this interface)</li>
                  </ul>
                </Alert>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <TaskList />
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              {/* MCP Flow */}
              {mcpFlow && (
                <Grid item xs={12}>
                  <Paper elevation={2} sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      {mcpFlow.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {mcpFlow.description}
                    </Typography>
                    
                    <Box mt={2}>
                      {mcpFlow.steps.map((step) => (
                        <Box key={step.step} mb={2} p={2} bgcolor="grey.50" borderRadius={1}>
                          <Typography variant="subtitle2" color="primary">
                            Step {step.step}: {step.component}
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {step.action}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {step.details}
                          </Typography>
                        </Box>
                      ))}
                    </Box>

                    <Box mt={3}>
                      <Typography variant="subtitle2" gutterBottom>
                        Key Concepts:
                      </Typography>
                      {Object.entries(mcpFlow.key_concepts).map(([key, value]) => (
                        <Box key={key} mb={1}>
                          <Typography variant="body2">
                            <strong>{key}:</strong> {value}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Paper>
                </Grid>
              )}

              {/* MCP Messages */}
              {mcpMessages && (
                <Grid item xs={12}>
                  <Paper elevation={2} sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      {mcpMessages.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {mcpMessages.description}
                    </Typography>
                    
                    {mcpMessages.examples.map((example, index) => (
                      <Box key={index} mb={3}>
                        <Typography variant="subtitle2" color="primary">
                          {example.type}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {example.direction}
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: 'grey.900' }}>
                          <pre style={{ 
                            margin: 0, 
                            color: '#00ff00',
                            fontSize: '12px',
                            overflow: 'auto'
                          }}>
                            {JSON.stringify(example.message, null, 2)}
                          </pre>
                        </Paper>
                      </Box>
                    ))}
                  </Paper>
                </Grid>
              )}

              {/* Additional Resources */}
              <Grid item xs={12}>
                <Alert severity="success">
                  <Typography variant="subtitle2" gutterBottom>
                    <strong>Learning Resources</strong>
                  </Typography>
                  <Typography variant="body2" paragraph>
                    This educational implementation helps you understand:
                  </Typography>
                  <ul style={{ marginTop: 0, marginBottom: 8 }}>
                    <li>How MCP servers expose tools and resources</li>
                    <li>How MCP clients connect and communicate via STDIO</li>
                    <li>How to integrate MCP into web applications</li>
                    <li>The JSON-RPC protocol used by MCP</li>
                  </ul>
                  <Typography variant="body2">
                    Explore the source code to see the implementation details, or use the API documentation at{' '}
                    <Link href="http://localhost:8000/docs" target="_blank">
                      http://localhost:8000/docs
                    </Link>
                  </Typography>
                </Alert>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Footer */}
          <Box mt={4} py={2} borderTop={1} borderColor="divider">
            <Typography variant="caption" color="text.secondary" align="center" display="block">
              MCP Learning System - Educational Implementation of Model Context Protocol
            </Typography>
            <Typography variant="caption" color="text.secondary" align="center" display="block">
              Built with React, FastAPI, and Python MCP SDK
            </Typography>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
