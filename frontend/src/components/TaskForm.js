/**
 * Task Form Component
 * Form for creating and editing tasks
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Alert,
  CircularProgress,
  Typography,
  Chip,
} from '@mui/material';
import { Save, Cancel, Add } from '@mui/icons-material';

const TaskForm = ({ open, onClose, onSubmit, task = null, loading = false, error = null }) => {
  const [formData, setFormData] = useState({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || 'medium',
    status: task?.status || 'pending',
  });

  const [validationErrors, setValidationErrors] = useState({});

  const isEditMode = !!task;

  // Handle input changes
  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors({
        ...validationErrors,
        [field]: null,
      });
    }
  };

  // Validate form
  const validateForm = () => {
    const errors = {};
    
    if (!formData.title.trim()) {
      errors.title = 'Title is required';
    } else if (formData.title.length > 100) {
      errors.title = 'Title must be less than 100 characters';
    }
    
    if (!formData.description.trim()) {
      errors.description = 'Description is required';
    } else if (formData.description.length > 500) {
      errors.description = 'Description must be less than 500 characters';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    // Only send changed fields for updates
    if (isEditMode) {
      const updates = {};
      if (formData.title !== task.title) updates.title = formData.title;
      if (formData.description !== task.description) updates.description = formData.description;
      if (formData.priority !== task.priority) updates.priority = formData.priority;
      if (formData.status !== task.status) updates.status = formData.status;
      
      // Only submit if there are changes
      if (Object.keys(updates).length > 0) {
        await onSubmit(updates);
      } else {
        onClose();
      }
    } else {
      await onSubmit(formData);
    }
  };

  // Reset form when dialog opens/closes
  React.useEffect(() => {
    if (open) {
      setFormData({
        title: task?.title || '',
        description: task?.description || '',
        priority: task?.priority || 'medium',
        status: task?.status || 'pending',
      });
      setValidationErrors({});
    }
  }, [open, task]);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'info';
      case 'pending':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            {isEditMode ? 'Edit Task' : 'Create New Task'}
          </Typography>
          {isEditMode && (
            <Typography variant="caption" color="text.secondary">
              ID: {task.id.substring(0, 8)}...
            </Typography>
          )}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <TextField
            fullWidth
            label="Title"
            value={formData.title}
            onChange={handleChange('title')}
            error={!!validationErrors.title}
            helperText={validationErrors.title || `${formData.title.length}/100 characters`}
            disabled={loading}
            margin="normal"
            required
            autoFocus
          />

          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={handleChange('description')}
            error={!!validationErrors.description}
            helperText={validationErrors.description || `${formData.description.length}/500 characters`}
            disabled={loading}
            margin="normal"
            required
            multiline
            rows={3}
          />

          <Box display="flex" gap={2} mt={2}>
            <FormControl fullWidth margin="normal">
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.priority}
                onChange={handleChange('priority')}
                label="Priority"
                disabled={loading}
              >
                <MenuItem value="low">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip label="Low" size="small" color="success" />
                  </Box>
                </MenuItem>
                <MenuItem value="medium">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip label="Medium" size="small" color="warning" />
                  </Box>
                </MenuItem>
                <MenuItem value="high">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip label="High" size="small" color="error" />
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth margin="normal">
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                onChange={handleChange('status')}
                label="Status"
                disabled={loading}
              >
                <MenuItem value="pending">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip label="Pending" size="small" />
                  </Box>
                </MenuItem>
                <MenuItem value="in_progress">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip label="In Progress" size="small" color="info" />
                  </Box>
                </MenuItem>
                <MenuItem value="completed">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip label="Completed" size="small" color="success" />
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Educational note about MCP */}
          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="caption">
              <strong>MCP Note:</strong> When you submit this form, the data flows through:
              <br />
              1. React → 2. FastAPI Host → 3. MCP Client → 4. MCP Server (via STDIO)
              <br />
              The MCP server executes the {isEditMode ? 'update_task' : 'create_task'} tool and returns the result.
            </Typography>
          </Alert>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button
          onClick={onClose}
          disabled={loading}
          startIcon={<Cancel />}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={loading}
          variant="contained"
          startIcon={loading ? <CircularProgress size={20} /> : (isEditMode ? <Save /> : <Add />)}
        >
          {loading ? 'Processing...' : (isEditMode ? 'Update' : 'Create')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TaskForm;
