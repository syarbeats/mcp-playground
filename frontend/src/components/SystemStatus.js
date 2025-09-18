/**
 * System Status Component
 * Displays the current status of the MCP system
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Grid,
  CircularProgress,
  Alert,
  Tooltip,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Info,
  ExpandMore,
  ExpandLess,
  Memory,
  Storage,
  Api,
} from '@mui/icons-material';
import { systemAPI, handleAPIError } from '../services/api';

const SystemStatus = () => {
  const [status, setStatus] = useState(null);
  const [capabilities, setCapabilities] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);

  // Fetch system status
  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all system information
      const [statusData, capData, statsData] = await Promise.all([
        systemAPI.getStatus(),
        systemAPI.getCapabilities().catch(() => null),
        systemAPI.getStatistics().catch(() => null),
      ]);

      setStatus(statusData);
      setCapabilities(capData);
      setStatistics(statsData);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Refresh status every 10 seconds
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !status) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" p={2}>
            <CircularProgress size={24} />
            <Typography ml={2}>Checking MCP system status...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const isConnected = status?.mcp_server === 'Connected';

  return (
    <Card elevation={3}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" component="div">
            MCP System Status
          </Typography>
          <Tooltip title={isConnected ? 'System Operational' : 'System Disconnected'}>
            {isConnected ? (
              <CheckCircle color="success" />
            ) : (
              <Error color="error" />
            )}
          </Tooltip>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" mb={1}>
              <Memory sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="body2" color="text.secondary">
                MCP Server
              </Typography>
            </Box>
            <Chip
              label={status?.mcp_server || 'Unknown'}
              color={isConnected ? 'success' : 'error'}
              size="small"
              variant="outlined"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" mb={1}>
              <Api sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="body2" color="text.secondary">
                MCP Client
              </Typography>
            </Box>
            <Chip
              label={status?.mcp_client || 'Unknown'}
              color={isConnected ? 'success' : 'error'}
              size="small"
              variant="outlined"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" mb={1}>
              <Storage sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="body2" color="text.secondary">
                Available Tools
              </Typography>
            </Box>
            <Typography variant="h6" color="primary">
              {status?.available_tools || 0}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" mb={1}>
              <Storage sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="body2" color="text.secondary">
                Available Resources
              </Typography>
            </Box>
            <Typography variant="h6" color="primary">
              {status?.available_resources || 0}
            </Typography>
          </Grid>
          
          {status?.last_activity && (
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" mb={1}>
                <Info sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Last Activity
                </Typography>
              </Box>
              <Typography variant="body2">
                {status.last_activity}
              </Typography>
            </Grid>
          )}
          
          {status?.uptime !== undefined && (
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" mb={1}>
                <Info sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Uptime
                </Typography>
              </Box>
              <Typography variant="body2">
                {status.uptime.toFixed(2)} seconds
              </Typography>
            </Grid>
          )}
          
          {status?.version && (
            <Grid item xs={12} sm={6}>
              <Box display="flex" alignItems="center" mb={1}>
                <Info sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Version
                </Typography>
              </Box>
              <Typography variant="body2">
                {status.version}
              </Typography>
            </Grid>
          )}
        </Grid>

        {statistics && (
          <Box mt={3}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" gutterBottom>
              Task Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography variant="body2" color="text.secondary">
                  Total Tasks
                </Typography>
                <Typography variant="h6">{statistics.total}</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="body2" color="text.secondary">
                  Pending
                </Typography>
                <Typography variant="h6" color="warning.main">
                  {statistics.by_status?.pending || 0}
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="body2" color="text.secondary">
                  Completed
                </Typography>
                <Typography variant="h6" color="success.main">
                  {statistics.by_status?.completed || 0}
                </Typography>
              </Grid>
              
              {statistics.completion_rate !== undefined && (
                <Grid item xs={12}>
                  <Box mt={1}>
                    <Typography variant="body2" color="text.secondary">
                      Completion Rate
                    </Typography>
                    <Box display="flex" alignItems="center">
                      <Box
                        sx={{
                          width: '100%',
                          bgcolor: 'background.paper',
                          borderRadius: 1,
                          mr: 1,
                          border: '1px solid',
                          borderColor: 'divider',
                        }}
                      >
                        <Box
                          sx={{
                            width: `${statistics.completion_rate}%`,
                            bgcolor: 'success.main',
                            height: 10,
                            borderRadius: 1,
                          }}
                        />
                      </Box>
                      <Typography variant="body2">
                        {statistics.completion_rate}%
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              )}
              
              {statistics.by_priority && (
                <>
                  <Grid item xs={4}>
                    <Typography variant="body2" color="text.secondary">
                      High Priority
                    </Typography>
                    <Typography variant="body1" color="error.main">
                      {statistics.by_priority.high || 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2" color="text.secondary">
                      Medium Priority
                    </Typography>
                    <Typography variant="body1" color="warning.main">
                      {statistics.by_priority.medium || 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2" color="text.secondary">
                      Low Priority
                    </Typography>
                    <Typography variant="body1" color="success.main">
                      {statistics.by_priority.low || 0}
                    </Typography>
                  </Grid>
                </>
              )}
            </Grid>
          </Box>
        )}

        {capabilities && (
          <Box mt={2}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="subtitle2">
                MCP Capabilities
              </Typography>
              <IconButton size="small" onClick={() => setExpanded(!expanded)}>
                {expanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Box>
            
            <Collapse in={expanded}>
              <Box mt={2}>
                {capabilities.tools?.length > 0 && (
                  <>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Available Tools ({capabilities.tools.length})
                    </Typography>
                    <List dense>
                      {capabilities.tools.map((tool, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={tool.name}
                            secondary={tool.description}
                            primaryTypographyProps={{ variant: 'body2' }}
                            secondaryTypographyProps={{ variant: 'caption' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}

                {capabilities.resources?.length > 0 && (
                  <>
                    <Typography variant="body2" color="text.secondary" gutterBottom mt={2}>
                      Available Resources ({capabilities.resources.length})
                    </Typography>
                    <List dense>
                      {capabilities.resources.map((resource, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={resource.name}
                            secondary={resource.uri}
                            primaryTypographyProps={{ variant: 'body2' }}
                            secondaryTypographyProps={{ variant: 'caption' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}

                {capabilities.resource_templates?.length > 0 && (
                  <>
                    <Typography variant="body2" color="text.secondary" gutterBottom mt={2}>
                      Resource Templates ({capabilities.resource_templates.length})
                    </Typography>
                    <List dense>
                      {capabilities.resource_templates.map((template, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={template.name}
                            secondary={template.uriTemplate}
                            primaryTypographyProps={{ variant: 'body2' }}
                            secondaryTypographyProps={{ variant: 'caption' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}
              </Box>
            </Collapse>
          </Box>
        )}

        <Box mt={2} display="flex" alignItems="center">
          <Info fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
          <Typography variant="caption" color="text.secondary">
            {status?.message || 'System status unknown'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SystemStatus;
