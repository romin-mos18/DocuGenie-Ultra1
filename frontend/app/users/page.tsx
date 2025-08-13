'use client'

import React, { useState } from 'react'
import MainLayout from '../components/layout/MainLayout'
import NotificationPortal from '../components/common/NotificationPortal'
import { useNotification } from '../../lib/hooks/useNotification'
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Grid,
  Card,
  CardContent,
  Snackbar,
  Alert
} from '@mui/material'
import {
  PersonAdd,
  MoreVert,
  Edit,
  Delete,
  Block,
  Security,
  Email,
  Phone,
  AdminPanelSettings,
  MedicalServices,
  Business,
  CheckCircle,
  Search,
  FilterList,
  Visibility
} from '@mui/icons-material'

interface User {
  id: number | string
  name: string
  email: string
  role: 'admin' | 'doctor' | 'nurse' | 'researcher' | 'viewer'
  status: 'active' | 'inactive' | 'suspended'
  lastLogin: string
  documentsAccessed: number
  avatar?: string
  phone?: string
}

export default function UsersPage() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [addUserOpen, setAddUserOpen] = useState(false)
  const [userList, setUserList] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  // New user form state
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'viewer' as const,
    phone: ''
  })
  
  // Notification system
  const { notification, showSuccess, showError, showWarning, showInfo, hideNotification } = useNotification()
  
  // Edit user state
  const [editUserOpen, setEditUserOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [editUserData, setEditUserData] = useState({
    name: '',
    email: '',
    role: 'viewer' as 'admin' | 'doctor' | 'nurse' | 'researcher' | 'viewer',
    phone: ''
  })
  
  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  // Initialize with mock data
  React.useEffect(() => {
    setUserList([
      {
        id: 1,
        name: 'Dr. Sarah Johnson',
        email: 'sarah.johnson@hospital.com',
        role: 'doctor',
        status: 'active',
        lastLogin: '2024-01-15 09:30',
        documentsAccessed: 342
      },
      {
        id: 2,
        name: 'Mike Chen',
        email: 'mike.chen@research.org',
        role: 'researcher',
        status: 'active',
        lastLogin: '2024-01-15 08:45',
        documentsAccessed: 156
      },
      {
        id: 3,
        name: 'Admin User',
        email: 'admin@docugenie.com',
        role: 'admin',
        status: 'active',
        lastLogin: '2024-01-15 10:15',
        documentsAccessed: 1247
      },
      {
        id: 4,
        name: 'Nurse Williams',
        email: 'nurse.williams@hospital.com',
        role: 'nurse',
        status: 'inactive',
        lastLogin: '2024-01-10 16:20',
        documentsAccessed: 89
      }
    ])
  }, [])

  const getRoleColor = (role: string) => {
    // Minimal color scheme - all use same neutral color
    return '#6b7280'
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return <AdminPanelSettings />
      case 'doctor': return <MedicalServices />
      case 'researcher': return <Business />
      default: return <Security />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#3b82f6'
      case 'inactive': return '#6b7280'
      case 'suspended': return '#6b7280'
      default: return '#6b7280'
    }
  }

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, user: User) => {
    setAnchorEl(event.currentTarget)
    setSelectedUser(user)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
    setSelectedUser(null)
  }

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleEditUser = (user: User) => {
    setEditingUser(user)
    setEditUserData({
      name: user.name,
      email: user.email,
      role: user.role,
      phone: user.phone || ''
    })
    setEditUserOpen(true)
    handleMenuClose()
  }

  const handleUpdateUser = async () => {
    if (!editingUser || !editUserData.name || !editUserData.email) {
      showWarning('Please fill in all required fields')
      return
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(editUserData.email)) {
      showError('Please enter a valid email address')
      return
    }

    setIsLoading(true)
    
    try {
      // Simulate API call to update user
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Update user in local state
      const updatedUsers = userList.map(user => 
        user.id === editingUser.id 
          ? { ...user, ...editUserData }
          : user
      )
      setUserList(updatedUsers)
      
      // Reset form and close dialog
      setEditUserData({ name: '', email: '', role: 'viewer', phone: '' })
      setEditingUser(null)
      setEditUserOpen(false)
      
      showSuccess(`🎉 User "${editUserData.name}" updated successfully!`)
    } catch (error) {
      console.error('Failed to update user:', error)
      showError('🔌 Failed to update user. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteUser = (user: User) => {
    setUserList(userList.filter(u => u.id !== user.id))
    showSuccess(`🗑️ User "${user.name}" has been deleted`)
    handleMenuClose()
  }

  const handleSuspendUser = (user: User) => {
    const updatedUsers = userList.map(u => 
      u.id === user.id 
        ? { ...u, status: (u.status === 'active' ? 'inactive' : 'active') as 'active' | 'inactive' | 'suspended' } as User
        : u
    )
    setUserList(updatedUsers)
    const action = user.status === 'active' ? 'suspended' : 'reactivated'
    showWarning(`⚠️ User "${user.name}" has been ${action}`)
    handleMenuClose()
  }

  const handleSendEmail = (user: User) => {
    showSuccess(`📧 Email sent to ${user.email}`)
    handleMenuClose()
  }

  const handleToggleStatus = (user: User) => {
    const updatedUsers = userList.map(u => 
      u.id === user.id 
        ? { ...u, status: (u.status === 'active' ? 'inactive' : 'active') as 'active' | 'inactive' | 'suspended' } as User
        : u
    )
    setUserList(updatedUsers)
    const newStatus = user.status === 'active' ? 'inactive' : 'active'
    showInfo(`🔄 User "${user.name}" status changed to ${newStatus}`)
  }

  // Filter and search logic
  const filteredUsers = userList.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRole = roleFilter === 'all' || user.role === roleFilter
    const matchesStatus = statusFilter === 'all' || user.status === statusFilter
    
    return matchesSearch && matchesRole && matchesStatus
  })

  const handleAddUser = async () => {
    if (!newUser.name || !newUser.email) {
      showWarning('Please fill in all required fields')
      return
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(newUser.email)) {
      showError('Please enter a valid email address')
      return
    }

    setIsLoading(true)
    
    try {
      const response = await fetch('http://localhost:8007/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newUser.name,
          email: newUser.email,
          password: "defaultpassword", // Default password for user management
          role: newUser.role,
          phone: newUser.phone
        }),
      })

      if (response.ok) {
        const result = await response.json()
        
        // Add user to local state using backend response
        const newUserData: User = {
          id: result.user?.id || userList.length + 1,
          name: newUser.name,
          email: newUser.email,
          role: newUser.role,
          status: 'active',
          lastLogin: 'Never',
          documentsAccessed: 0,
          phone: newUser.phone
        }
        
        setUserList([...userList, newUserData])
        
        // Reset form
        setNewUser({ name: '', email: '', role: 'viewer', phone: '' })
        setAddUserOpen(false)
        
        showSuccess(`🎉 User "${newUser.name}" added successfully!`)
      } else {
        let errorMessage = 'Failed to add user'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || `Error ${response.status}: ${response.statusText}`
        } catch (parseError) {
          errorMessage = `Error ${response.status}: ${response.statusText}`
        }
        showError(`❌ ${errorMessage}`)
      }
    } catch (error) {
      console.error('Failed to add user:', error)
      let errorMessage = 'Network error. Please check your connection and try again.'
      if (error instanceof Error) {
        if (error.message.includes('fetch')) {
          errorMessage = 'Backend server is not running. Please start the backend server.'
        } else {
          errorMessage = error.message
        }
      } else if (typeof error === 'string') {
        errorMessage = error
      }
      showError(`🔌 ${errorMessage}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <MainLayout>
      <Box sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 4,
          p: 3,
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}>
          <Box>
            <Typography variant="h4" gutterBottom fontWeight="600" sx={{ color: '#1f2937' }}>
              User Management
            </Typography>
            <Typography variant="subtitle1" sx={{ color: '#6b7280' }}>
              Manage system users and their permissions
            </Typography>
          </Box>
          <Button 
            variant="contained" 
            startIcon={<PersonAdd />}
            onClick={() => setAddUserOpen(true)}
            sx={{
              backgroundColor: '#3b82f6',
              color: 'white',
              borderRadius: '8px',
              fontWeight: 500,
              textTransform: 'none',
              boxShadow: 'none',
              '&:hover': {
                backgroundColor: '#2563eb',
                boxShadow: 'none'
              }
            }}
          >
            Add User
          </Button>
        </Box>

        {/* Comprehensive Role Summary Cards */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={2.4}>
            <Card sx={{ 
              backgroundColor: '#ffffff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: 'none',
              '&:hover': { boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' }
            }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ 
                    p: 1.5, 
                    borderRadius: '6px', 
                    backgroundColor: '#dbeafe', 
                    mr: 2 
                  }}>
                    <Security sx={{ color: '#3b82f6', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="h6" fontWeight="600" sx={{ color: '#1f2937' }}>
                      {userList.length}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      Total Users
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2.4}>
            <Card sx={{ 
              backgroundColor: '#ffffff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: 'none',
              '&:hover': { boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' }
            }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ 
                    p: 1.5, 
                    borderRadius: '6px', 
                    backgroundColor: '#d1fae5', 
                    mr: 2 
                  }}>
                    <CheckCircle sx={{ color: '#10b981', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="h6" fontWeight="600" sx={{ color: '#1f2937' }}>
                      {userList.filter(u => u.status === 'active').length}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      Active Users
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={2.4}>
            <Card sx={{ 
              backgroundColor: '#ffffff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: 'none',
              '&:hover': { boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' }
            }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ 
                    p: 1.5, 
                    borderRadius: '6px', 
                    backgroundColor: '#fef3c7', 
                    mr: 2 
                  }}>
                    <AdminPanelSettings sx={{ color: '#f59e0b', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="h6" fontWeight="600" sx={{ color: '#1f2937' }}>
                      {userList.filter(u => u.role === 'admin').length}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      Administrators
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={2.4}>
            <Card sx={{ 
              backgroundColor: '#ffffff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: 'none',
              '&:hover': { boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' }
            }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ 
                    p: 1.5, 
                    borderRadius: '6px', 
                    backgroundColor: '#e0e7ff', 
                    mr: 2 
                  }}>
                    <MedicalServices sx={{ color: '#6366f1', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="h6" fontWeight="600" sx={{ color: '#1f2937' }}>
                      {userList.filter(u => ['doctor', 'nurse'].includes(u.role)).length}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      Medical Staff
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={2.4}>
            <Card sx={{ 
              backgroundColor: '#ffffff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: 'none',
              '&:hover': { boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' }
            }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box sx={{ 
                    p: 1.5, 
                    borderRadius: '6px', 
                    backgroundColor: '#f3e8ff', 
                    mr: 2 
                  }}>
                    <Visibility sx={{ color: '#8b5cf6', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="h6" fontWeight="600" sx={{ color: '#1f2937' }}>
                      {userList.filter(u => u.role === 'viewer').length}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6b7280' }}>
                      Viewers
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Search and Filter Bar */}
        <Paper sx={{ p: 3, mb: 3, backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: 'none' }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search users by name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <Box sx={{ mr: 1 }}>
                      <Search sx={{ color: '#6b7280' }} />
                    </Box>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px',
                    '& fieldset': { borderColor: '#e5e7eb' },
                    '&:hover fieldset': { borderColor: '#3b82f6' },
                    '&.Mui-focused fieldset': { borderColor: '#3b82f6' }
                  }
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Filter by Role</InputLabel>
                <Select
                  value={roleFilter}
                  label="Filter by Role"
                  onChange={(e) => setRoleFilter(e.target.value)}
                  sx={{
                    borderRadius: '8px',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: '#e5e7eb' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#3b82f6' },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#3b82f6' }
                  }}
                >
                  <MenuItem value="all">All Roles</MenuItem>
                  <MenuItem value="admin">Administrator</MenuItem>
                  <MenuItem value="doctor">Doctor</MenuItem>
                  <MenuItem value="nurse">Nurse</MenuItem>
                  <MenuItem value="researcher">Researcher</MenuItem>
                  <MenuItem value="viewer">Viewer</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Filter by Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                  sx={{
                    borderRadius: '8px',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: '#e5e7eb' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#3b82f6' },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#3b82f6' }
                  }}
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Typography variant="body2" sx={{ color: '#6b7280', textAlign: 'center' }}>
                {filteredUsers.length} of {userList.length} users
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        {/* Users Table */}
        <Paper sx={{ 
          width: '100%', 
          overflow: 'hidden',
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '12px',
          boxShadow: 'none'
        }}>
          <TableContainer>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>User</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Last Login</TableCell>
                  <TableCell>Documents Accessed</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                              {filteredUsers
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((user) => (
                    <TableRow key={user.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ 
                            mr: 2, 
                            bgcolor: '#f3f4f6',
                            color: '#6b7280',
                            fontWeight: 600
                          }}>
                            {user.name.split(' ').map(n => n[0]).join('')}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle2" fontWeight="600" sx={{ color: '#1f2937' }}>
                              {user.name}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#6b7280' }}>
                              {user.email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          px: 2,
                          py: 0.5,
                          borderRadius: '6px',
                          backgroundColor: '#f3f4f6',
                          gap: 0.5
                        }}>
                          {getRoleIcon(user.role)}
                          <Typography variant="caption" fontWeight="500" sx={{ color: '#6b7280' }}>
                            {user.role.toUpperCase()}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box 
                          sx={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            px: 2,
                            py: 0.5,
                            borderRadius: '6px',
                            backgroundColor: user.status === 'active' ? '#eff6ff' : '#f3f4f6',
                            border: user.status === 'active' ? '1px solid #dbeafe' : '1px solid #e5e7eb',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              transform: 'scale(1.05)',
                              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
                            }
                          }}
                          onClick={() => handleToggleStatus(user)}
                          title={`Click to ${user.status === 'active' ? 'deactivate' : 'activate'} user`}
                        >
                          <Typography 
                            variant="caption" 
                            fontWeight="500" 
                            sx={{ color: user.status === 'active' ? '#3b82f6' : '#6b7280' }}
                          >
                            {user.status.toUpperCase()}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{user.lastLogin}</TableCell>
                      <TableCell>{user.documentsAccessed}</TableCell>
                      <TableCell>
                        <IconButton
                          onClick={(e) => handleMenuClick(e, user)}
                        >
                          <MoreVert />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={filteredUsers.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>

        {/* Action Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => selectedUser && handleEditUser(selectedUser)}>
            <Edit sx={{ mr: 1 }} />
            Edit User
          </MenuItem>
          <MenuItem onClick={() => selectedUser && handleSendEmail(selectedUser)}>
            <Email sx={{ mr: 1 }} />
            Send Email
          </MenuItem>
          <MenuItem onClick={() => selectedUser && handleSuspendUser(selectedUser)}>
            <Block sx={{ mr: 1 }} />
            {selectedUser?.status === 'active' ? 'Suspend User' : 'Reactivate User'}
          </MenuItem>
          <MenuItem 
            onClick={() => selectedUser && handleDeleteUser(selectedUser)} 
            sx={{ color: 'error.main' }}
          >
            <Delete sx={{ mr: 1 }} />
            Delete User
          </MenuItem>
        </Menu>

        {/* Add User Dialog */}
        <Dialog
          open={addUserOpen}
          onClose={() => setAddUserOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Add New User</DialogTitle>
          <DialogContent>
            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Full Name"
                  variant="outlined"
                  value={newUser.name}
                  onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email Address"
                  variant="outlined"
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Role</InputLabel>
                  <Select 
                    label="Role" 
                    value={newUser.role}
                    onChange={(e) => setNewUser({...newUser, role: e.target.value as any})}
                  >
                    <MenuItem value="viewer">Viewer</MenuItem>
                    <MenuItem value="nurse">Nurse</MenuItem>
                    <MenuItem value="doctor">Doctor</MenuItem>
                    <MenuItem value="researcher">Researcher</MenuItem>
                    <MenuItem value="admin">Administrator</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Phone Number"
                  variant="outlined"
                  value={newUser.phone}
                  onChange={(e) => setNewUser({...newUser, phone: e.target.value})}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAddUserOpen(false)} disabled={isLoading}>Cancel</Button>
            <Button 
              variant="contained" 
              onClick={handleAddUser}
              disabled={isLoading}
            >
              {isLoading ? 'Adding...' : 'Add User'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Edit User Dialog */}
        <Dialog
          open={editUserOpen}
          onClose={() => setEditUserOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Edit User</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Full Name *"
              fullWidth
              variant="outlined"
              value={editUserData.name}
              onChange={(e) => setEditUserData({ ...editUserData, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Email Address *"
              type="email"
              fullWidth
              variant="outlined"
              value={editUserData.email}
              onChange={(e) => setEditUserData({ ...editUserData, email: e.target.value })}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Role</InputLabel>
              <Select
                value={editUserData.role}
                label="Role"
                onChange={(e) => setEditUserData({ ...editUserData, role: e.target.value as 'admin' | 'doctor' | 'nurse' | 'viewer' })}
              >
                <MenuItem value="admin">Administrator</MenuItem>
                <MenuItem value="doctor">Doctor</MenuItem>
                <MenuItem value="nurse">Nurse</MenuItem>
                <MenuItem value="viewer">Viewer</MenuItem>
              </Select>
            </FormControl>
            <TextField
              margin="dense"
              label="Phone Number"
              fullWidth
              variant="outlined"
              value={editUserData.phone}
              onChange={(e) => setEditUserData({ ...editUserData, phone: e.target.value })}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditUserOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleUpdateUser}
              variant="contained"
              disabled={isLoading}
            >
              {isLoading ? 'Updating...' : 'Update User'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Portal Notification System */}
        <NotificationPortal 
          notification={notification} 
          onClose={hideNotification} 
        />
      </Box>
    </MainLayout>
  )
}