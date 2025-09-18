/**
 * Task List Component
 * Displays and manages the list of tasks
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Box,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Tooltip,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
  FormControl,
  Select,
  InputLabel,
} from '@mui/material';
import {
  Edit,
  Delete,
  MoreVert,
  Add,
  Refresh,
  Search,
  FilterList,
  CheckCircle,
  Schedule,
  PlayArrow,
} from '@mui/icons-material';
import { taskAPI, handleAPIError } from '../services/api';
import TaskForm from './TaskForm';

const TaskList = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formOpen, setFormOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [menuTask, setMenuTask] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTasks, setTotalTasks] = useState(0);

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      setError(null);
      setLoading(true);
      const filter = statusFilter === 'all' ? null : statusFilter;
      const data = await taskAPI.list(filter, page, pageSize);
      
      // Handle the new response format with pagination
      if (data.tasks) {
        setTasks(data.tasks);
        setTotalPages(data.total_pages || 1);
        setTotalTasks(data.count || data.tasks.length);
      } else {
        // Fallback for backward compatibility
        setTasks(data);
        setTotalTasks(data.length);
      }
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [statusFilter, page, pageSize]);

  // Create task
  const handleCreateTask = async (taskData) => {
    try {
      setFormLoading(true);
      setFormError(null);
      const newTask = await taskAPI.create(taskData);
      setTasks([newTask, ...tasks]);
      setFormOpen(false);
      setSelectedTask(null);
    } catch (err) {
      setFormError(handleAPIError(err));
    } finally {
      setFormLoading(false);
    }
  };

  // Update task
  const handleUpdateTask = async (updates) => {
    try {
      setFormLoading(true);
      setFormError(null);
      const updatedTask = await taskAPI.update(selectedTask.id, updates);
      setTasks(tasks.map(t => t.id === updatedTask.id ? updatedTask : t));
      setFormOpen(false);
      setSelectedTask(null);
    } catch (err) {
      setFormError(handleAPIError(err));
    } finally {
      setFormLoading(false);
    }
  };

  // Delete task
  const handleDeleteTask = async (taskId) => {
    try {
      await taskAPI.delete(taskId);
      setTasks(tasks.filter(t => t.id !== taskId));
      handleCloseMenu();
    } catch (err) {
      setError(handleAPIError(err));
    }
  };

  // Quick status update
  const handleQuickStatusUpdate = async (taskId, newStatus) => {
    try {
      const updatedTask = await taskAPI.update(taskId, { status: newStatus });
      setTasks(tasks.map(t => t.id === updatedTask.id ? updatedTask : t));
      handleCloseMenu();
    } catch (err) {
      setError(handleAPIError(err));
    }
  };

  // Menu handlers
  const handleOpenMenu = (event, task) => {
    setAnchorEl(event.currentTarget);
    setMenuTask(task);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
    setMenuTask(null);
  };

  // Edit task
  const handleEditTask = (task) => {
    setSelectedTask(task);
    setFormOpen(true);
    handleCloseMenu();
  };

  // Filter tasks by search term
  const filteredTasks = tasks.filter(task => 
    task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    task.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  // Get status color and icon
  const getStatusInfo = (status) => {
    switch (status) {
      case 'completed':
        return { color: 'success', icon: <CheckCircle fontSize="small" /> };
      case 'in_progress':
        return { color: 'info', icon: <PlayArrow fontSize="small" /> };
      case 'pending':
        return { color: 'default', icon: <Schedule fontSize="small" /> };
      default:
        return { color: 'default', icon: null };
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading && tasks.length === 0) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" p={2}>
            <CircularProgress size={24} />
            <Typography ml={2}>Loading tasks via MCP...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card elevation={3}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6" component="div">
              Task Management
            </Typography>
            <Box display="flex" gap={1}>
              <Tooltip title="Refresh tasks">
                <IconButton onClick={fetchTasks} disabled={loading}>
                  <Refresh />
                </IconButton>
              </Tooltip>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => {
                  setSelectedTask(null);
                  setFormOpen(true);
                }}
              >
                New Task
              </Button>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Search and Filter */}
          <Box display="flex" gap={2} mb={2}>
            <TextField
              size="small"
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ flexGrow: 1 }}
            />
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Status Filter</InputLabel>
              <Select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1); // Reset to first page when filter changes
                }}
                label="Status Filter"
                startAdornment={<FilterList />}
              >
                <MenuItem value="all">All Tasks</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Priority Filter</InputLabel>
              <Select
                value={priorityFilter}
                onChange={(e) => {
                  setPriorityFilter(e.target.value);
                  setPage(1); // Reset to first page when filter changes
                }}
                label="Priority Filter"
              >
                <MenuItem value="all">All Priorities</MenuItem>
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Divider />

          {/* Task List */}
          {filteredTasks.length === 0 ? (
            <Box p={4} textAlign="center">
              <Typography color="text.secondary">
                {searchTerm || statusFilter !== 'all' 
                  ? 'No tasks found matching your criteria'
                  : 'No tasks yet. Create your first task!'}
              </Typography>
            </Box>
          ) : (
            <List>
              {filteredTasks.map((task, index) => {
                const statusInfo = getStatusInfo(task.status);
                return (
                  <React.Fragment key={task.id}>
                    {index > 0 && <Divider />}
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle1">
                              {task.title}
                            </Typography>
                            <Chip
                              label={task.priority}
                              size="small"
                              color={getPriorityColor(task.priority)}
                              variant="outlined"
                            />
                            <Chip
                              label={task.status.replace('_', ' ')}
                              size="small"
                              color={statusInfo.color}
                              icon={statusInfo.icon}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {task.description}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Created: {formatDate(task.created_at)}
                              {task.updated_at !== task.created_at && 
                                ` • Updated: ${formatDate(task.updated_at)}`}
                            </Typography>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={(e) => handleOpenMenu(e, task)}
                        >
                          <MoreVert />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  </React.Fragment>
                );
              })}
            </List>
          )}

          {/* Pagination and Task count */}
          <Box mt={2} display="flex" justifyContent="space-between" alignItems="center">
            <Button 
              disabled={page <= 1} 
              onClick={() => setPage(prev => Math.max(1, prev - 1))}
              size="small"
            >
              Previous
            </Button>
            
            <Typography variant="caption" color="text.secondary">
              Page {page} of {totalPages} • Showing {filteredTasks.length} of {totalTasks} tasks
            </Typography>
            
            <Button 
              disabled={page >= totalPages} 
              onClick={() => setPage(prev => prev + 1)}
              size="small"
            >
              Next
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Task Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleCloseMenu}
      >
        <MenuItem onClick={() => handleEditTask(menuTask)}>
          <Edit fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <Divider />
        <MenuItem 
          onClick={() => handleQuickStatusUpdate(menuTask?.id, 'pending')}
          disabled={menuTask?.status === 'pending'}
        >
          <Schedule fontSize="small" sx={{ mr: 1 }} />
          Mark as Pending
        </MenuItem>
        <MenuItem 
          onClick={() => handleQuickStatusUpdate(menuTask?.id, 'in_progress')}
          disabled={menuTask?.status === 'in_progress'}
        >
          <PlayArrow fontSize="small" sx={{ mr: 1 }} />
          Mark as In Progress
        </MenuItem>
        <MenuItem 
          onClick={() => handleQuickStatusUpdate(menuTask?.id, 'completed')}
          disabled={menuTask?.status === 'completed'}
        >
          <CheckCircle fontSize="small" sx={{ mr: 1 }} />
          Mark as Completed
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => handleDeleteTask(menuTask?.id)}>
          <Delete fontSize="small" sx={{ mr: 1 }} color="error" />
          <Typography color="error">Delete</Typography>
        </MenuItem>
      </Menu>

      {/* Task Form Dialog */}
      <TaskForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setSelectedTask(null);
          setFormError(null);
        }}
        onSubmit={selectedTask ? handleUpdateTask : handleCreateTask}
        task={selectedTask}
        loading={formLoading}
        error={formError}
      />
    </>
  );
};

export default TaskList;
