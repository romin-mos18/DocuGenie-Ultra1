'use client'

import React, { useState, useEffect } from 'react'
import MainLayout from '../components/layout/MainLayout'
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Grid,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert
} from '@mui/material'
import {
  Assignment,
  CheckCircle,
  Cancel,
  Schedule,
  Person,
  Comment,
  Add,
  Visibility,
  Edit,
  History
} from '@mui/icons-material'

interface Workflow {
  id: string
  document_id: string
  document_name: string
  workflow_type: string
  status: string
  assignee_id: string
  priority: string
  deadline?: string
  notes?: string
  created_at: string
  created_by: string
  history: any[]
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false)
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null)
  const [newWorkflow, setNewWorkflow] = useState({
    document_id: '',
    workflow_type: 'review',
    assignee_id: '',
    priority: 'medium',
    deadline: '',
    notes: ''
  })
  const [reviewAction, setReviewAction] = useState({
    action: 'approve',
    comments: ''
  })

  useEffect(() => {
    fetchWorkflows()
  }, [])

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('http://localhost:8007/api/workflows')
      const data = await response.json()
      setWorkflows(data.workflows || [])
    } catch (error) {
      console.error('Failed to fetch workflows:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateWorkflow = async () => {
    try {
      const response = await fetch('http://localhost:8007/api/workflows/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newWorkflow)
      })
      
      if (response.ok) {
        setCreateDialogOpen(false)
        setNewWorkflow({
          document_id: '',
          workflow_type: 'review',
          assignee_id: '',
          priority: 'medium',
          deadline: '',
          notes: ''
        })
        fetchWorkflows()
      }
    } catch (error) {
      console.error('Failed to create workflow:', error)
    }
  }

  const handleSubmitReview = async () => {
    if (!selectedWorkflow) return

    try {
      const response = await fetch('http://localhost:8007/api/workflows/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: selectedWorkflow.id,
          action: reviewAction.action,
          comments: reviewAction.comments,
          reviewer_id: 'current_user'
        })
      })
      
      if (response.ok) {
        setReviewDialogOpen(false)
        setReviewAction({ action: 'approve', comments: '' })
        setSelectedWorkflow(null)
        fetchWorkflows()
      }
    } catch (error) {
      console.error('Failed to submit review:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success'
      case 'rejected': return 'error'
      case 'pending': return 'warning'
      case 'changes_requested': return 'info'
      default: return 'default'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error'
      case 'medium': return 'warning'
      case 'low': return 'success'
      default: return 'default'
    }
  }

  return (
    <MainLayout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              Document Workflows
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Manage document approval, review, and validation workflows
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Workflow
          </Button>
        </Box>

        {/* Workflow Stats */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="warning.main">
                  {workflows.filter(w => w.status === 'pending').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending Reviews
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="success.main">
                  {workflows.filter(w => w.status === 'approved').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Approved
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="error.main">
                  {workflows.filter(w => w.status === 'rejected').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Rejected
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="info.main">
                  {workflows.filter(w => w.status === 'changes_requested').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Changes Requested
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Workflows List */}
        <Grid container spacing={3}>
          {workflows.map((workflow) => (
            <Grid item xs={12} md={6} lg={4} key={workflow.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                      {workflow.document_name}
                    </Typography>
                    <Chip
                      label={workflow.status}
                      color={getStatusColor(workflow.status) as any}
                      size="small"
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={workflow.workflow_type} 
                      variant="outlined" 
                      size="small" 
                      sx={{ mr: 1, mb: 1 }} 
                    />
                    <Chip 
                      label={workflow.priority} 
                      color={getPriorityColor(workflow.priority) as any}
                      variant="outlined" 
                      size="small"
                      sx={{ mb: 1 }} 
                    />
                  </Box>

                  <List dense>
                    <ListItem>
                      <ListItemIcon><Person /></ListItemIcon>
                      <ListItemText 
                        primary="Assignee" 
                        secondary={workflow.assignee_id} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><Schedule /></ListItemIcon>
                      <ListItemText 
                        primary="Created" 
                        secondary={new Date(workflow.created_at).toLocaleDateString()} 
                      />
                    </ListItem>
                    {workflow.deadline && (
                      <ListItem>
                        <ListItemIcon><Schedule /></ListItemIcon>
                        <ListItemText 
                          primary="Deadline" 
                          secondary={new Date(workflow.deadline).toLocaleDateString()} 
                        />
                      </ListItem>
                    )}
                  </List>

                  {workflow.notes && (
                    <Alert severity="info" sx={{ mt: 1 }}>
                      {workflow.notes}
                    </Alert>
                  )}
                </CardContent>

                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={<Visibility />}
                    onClick={() => setSelectedWorkflow(workflow)}
                  >
                    View Details
                  </Button>
                  {workflow.status === 'pending' && (
                    <Button 
                      size="small" 
                      startIcon={<Edit />}
                      onClick={() => {
                        setSelectedWorkflow(workflow)
                        setReviewDialogOpen(true)
                      }}
                    >
                      Review
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>

        {workflows.length === 0 && !isLoading && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Assignment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No workflows found
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Create your first workflow to start managing document approvals
            </Typography>
            <Button 
              variant="contained" 
              startIcon={<Add />}
              onClick={() => setCreateDialogOpen(true)}
              sx={{ mt: 2 }}
            >
              Create Workflow
            </Button>
          </Paper>
        )}

        {/* Create Workflow Dialog */}
        <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Create New Workflow</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Document ID"
                  value={newWorkflow.document_id}
                  onChange={(e) => setNewWorkflow({...newWorkflow, document_id: e.target.value})}
                  placeholder="Enter document ID"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Workflow Type</InputLabel>
                  <Select
                    value={newWorkflow.workflow_type}
                    onChange={(e) => setNewWorkflow({...newWorkflow, workflow_type: e.target.value})}
                  >
                    <MenuItem value="approval">Approval</MenuItem>
                    <MenuItem value="review">Review</MenuItem>
                    <MenuItem value="validation">Validation</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={newWorkflow.priority}
                    onChange={(e) => setNewWorkflow({...newWorkflow, priority: e.target.value})}
                  >
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Assignee ID"
                  value={newWorkflow.assignee_id}
                  onChange={(e) => setNewWorkflow({...newWorkflow, assignee_id: e.target.value})}
                  placeholder="Enter assignee user ID"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Deadline"
                  type="date"
                  value={newWorkflow.deadline}
                  onChange={(e) => setNewWorkflow({...newWorkflow, deadline: e.target.value})}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Notes"
                  value={newWorkflow.notes}
                  onChange={(e) => setNewWorkflow({...newWorkflow, notes: e.target.value})}
                  placeholder="Add any additional notes or instructions"
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleCreateWorkflow} 
              variant="contained"
              disabled={!newWorkflow.document_id || !newWorkflow.assignee_id}
            >
              Create Workflow
            </Button>
          </DialogActions>
        </Dialog>

        {/* Review Dialog */}
        <Dialog open={reviewDialogOpen} onClose={() => setReviewDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Submit Review</DialogTitle>
          <DialogContent>
            {selectedWorkflow && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Document: {selectedWorkflow.document_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Workflow Type: {selectedWorkflow.workflow_type}
                </Typography>
                
                <FormControl fullWidth sx={{ mt: 2, mb: 2 }}>
                  <InputLabel>Action</InputLabel>
                  <Select
                    value={reviewAction.action}
                    onChange={(e) => setReviewAction({...reviewAction, action: e.target.value})}
                  >
                    <MenuItem value="approve">Approve</MenuItem>
                    <MenuItem value="reject">Reject</MenuItem>
                    <MenuItem value="request_changes">Request Changes</MenuItem>
                  </Select>
                </FormControl>

                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Comments"
                  value={reviewAction.comments}
                  onChange={(e) => setReviewAction({...reviewAction, comments: e.target.value})}
                  placeholder="Enter your review comments..."
                  required
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setReviewDialogOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleSubmitReview} 
              variant="contained"
              disabled={!reviewAction.comments.trim()}
            >
              Submit Review
            </Button>
          </DialogActions>
        </Dialog>
              </Box>


      </MainLayout>
    )
  }
