'use client'

import React, { useState, useEffect, useRef } from 'react'

import MainLayout from '../components/layout/MainLayout'
import NotificationPortal from '../components/common/NotificationPortal'
import { useNotification } from '../../lib/hooks/useNotification'
import {
  Box,
  Paper,
  Typography,
  TextField,
  InputAdornment,
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
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Grid,
  Card,
  CardContent,
  Avatar,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  LinearProgress
} from '@mui/material'
import {
  Search,
  FilterList,
  MoreVert,
  GetApp,
  Delete,
  Edit,
  CloudUpload,
  Description,
  CheckCircle,
  Schedule,
  Error,
  Person,
  Business,
  DateRange,
  Storage,
  Speed,
  Fingerprint,
  Assignment,
  Assessment,
  Warning,
  DataObject,
  AccessTime,
  Description as DocumentTextIcon,
  ViewInAr as CubeIcon,
  Info as InformationCircleIcon,
  CalendarToday as CalendarIcon,
  Person as UserIcon,
  Email as EnvelopeIcon,
  Lightbulb,
  Translate,
  Insights
} from '@mui/icons-material'

export default function DocumentsPage() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [selectedDocument, setSelectedDocument] = useState<any>(null)
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [documentToDelete, setDocumentToDelete] = useState<any>(null)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [documentToEdit, setDocumentToEdit] = useState<any>(null)
  const [newDocumentName, setNewDocumentName] = useState('')
  const [lastRefreshTime, setLastRefreshTime] = useState<Date>(new Date())
  const [refreshing, setRefreshing] = useState(false)
  const documentsRef = useRef<any[]>([])

  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [deletingDocuments, setDeletingDocuments] = useState<Set<number>>(new Set());
  const [activeTab, setActiveTab] = useState("overview");
  const [expanded, setExpanded] = useState(false);

  // Notification system
  const { notification, showSuccess, showError, showWarning, showInfo, hideNotification } = useNotification()

  // Fetch documents from backend
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setLoading(true)
        const response = await fetch('http://localhost:8007/api/v1/documents')
        if (response.ok) {
          const data = await response.json()
          console.log('Fetched documents:', data)
          
          // Transform backend data to match frontend structure
          const transformedDocuments = data.documents.map((doc: any) => {
            const keyInfo = doc.ai_analysis?.key_information || null;
            const fallbackEntities = keyInfo ? {
              dates: keyInfo.dates_found || [],
              names: keyInfo.potential_names || [],
              organizations: keyInfo.organizations || [],
              medical_terms: keyInfo.medical_terms || [],
              numbers: keyInfo.numbers || [],
              emails: keyInfo.emails || [],
              phone_numbers: keyInfo.phone_numbers || [],
              entity_count: (keyInfo.dates_found?.length || 0) + (keyInfo.potential_names?.length || 0) + (keyInfo.numbers?.length || 0) + (keyInfo.emails?.length || 0) + (keyInfo.phone_numbers?.length || 0),
              success: true,
            } : {};
            const mergedEntities = (doc.extracted_entities && Object.keys(doc.extracted_entities).length > 0) ? doc.extracted_entities : fallbackEntities;
            const entitiesFoundCount = (doc.extracted_entities && Object.keys(doc.extracted_entities).length > 0)
              ? (doc.extracted_entities.entity_count || Object.values(doc.extracted_entities).reduce((acc: number, v: any) => acc + (Array.isArray(v) ? v.length : 0), 0))
              : (fallbackEntities as any).entity_count || 0;
            return ({
            id: doc.id,
            name: doc.filename,
            type: doc.document_type,
            status: doc.status,
              uploadDate: doc.upload_date,
              size: doc.file_size,
            accuracy: doc.ocr_accuracy ? parseFloat(doc.ocr_accuracy) : null,
              patientId: doc.patient_id || null,
              providerId: doc.provider_id || null,
              patientName: doc.patient_name || null,
              providerName: doc.provider_name || null,
            rawSize: doc.raw_size,
            processingTime: doc.processing_time,
              classificationConfidence: doc.confidence ? parseFloat(doc.confidence) : null,
            mimeType: doc.mime_type,
              entitiesFound: entitiesFoundCount,
              entities: mergedEntities,
              doclingResult: doc.docling_result || {},
              aiAnalysis: doc.ai_analysis || {},
              documentType: doc.document_type || 'unknown'
            })
          })
          
          setDocuments(transformedDocuments)
          documentsRef.current = transformedDocuments
          setLastRefreshTime(new Date())
          // Auto-select first document if none selected
          if (transformedDocuments.length > 0 && !selectedDocumentId) {
            setSelectedDocumentId(transformedDocuments[0].id)
            setSelectedDocument(transformedDocuments[0])
          }
        } else {
          console.error('Failed to fetch documents')
          // Fallback to empty array if API fails
          setDocuments([])
        }
      } catch (error) {
        console.error('Error fetching documents:', error)
        setDocuments([])
      } finally {
        setLoading(false)
      }
    }

    // Initial fetch
    fetchDocuments()
    
    // Only refresh if there are processing documents (every 2 minutes)
    const checkProcessingDocuments = () => {
      const hasProcessingDocs = documentsRef.current.some(doc => doc.status === 'processing')
      if (hasProcessingDocs) {
        fetchDocuments()
      }
    }
    
    // Check every 2 minutes instead of 30 seconds
    const interval = setInterval(checkProcessingDocuments, 120000)
    
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'processing': return 'warning'
      case 'failed': return 'error'
      default: return 'default'
    }
  }

  // Filter documents based on search and status
  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.type?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter
    return matchesSearch && matchesStatus
  })

  // Reset page when filtering changes
  React.useEffect(() => {
    setPage(0)
  }, [searchTerm, statusFilter])

  // Paginated documents
  const paginatedDocuments = filteredDocuments.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )



  // Debug logging
  console.log('Pagination Debug:', {
    totalDocuments: documents.length,
    filteredDocuments: filteredDocuments.length,
    page,
    rowsPerPage,
    paginatedDocuments: paginatedDocuments.length,
    startIndex: page * rowsPerPage,
    endIndex: page * rowsPerPage + rowsPerPage
  })

  // Get currently selected document
  const currentSelectedDocument = documents.find(doc => doc.id === selectedDocumentId)

  // Action handlers
  const handleDocumentSelect = (document: any) => {
    setSelectedDocumentId(document.id)
    setSelectedDocument(document)
  }

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, document: any) => {
    setAnchorEl(event.currentTarget)
    setSelectedDocument(document)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleDownloadDocument = () => {
    if (selectedDocument) {
      console.log('Downloading document:', selectedDocument)
      // Create download link
      const link = document.createElement('a')
              link.href = `http://localhost:8007/api/v1/documents/${selectedDocument.id}/download`
      link.download = selectedDocument.name
      link.click()
    }
    handleMenuClose()
  }

  const handleDeleteDocument = () => {
    if (selectedDocument) {
      setDocumentToDelete(selectedDocument)
      setDeleteModalOpen(true)
    }
    handleMenuClose()
  }

  const handleDeleteConfirm = async () => {
    if (documentToDelete) {
      try {
        const response = await fetch(`http://localhost:8007/api/v1/documents/${documentToDelete.id}`, {
          method: 'DELETE',
        })
        
        if (response.ok) {
          // Remove document from state
          setDocuments(prev => prev.filter(doc => doc.id !== documentToDelete.id))
          
          // If deleted document was selected, clear selection or select another
          if (selectedDocumentId === documentToDelete.id) {
            const remainingDocs = documents.filter(doc => doc.id !== documentToDelete.id)
            if (remainingDocs.length > 0) {
              setSelectedDocumentId(remainingDocs[0].id)
              setSelectedDocument(remainingDocs[0])
            } else {
              setSelectedDocumentId(null)
              setSelectedDocument(null)
            }
          }
          
          showSuccess('Document deleted successfully!')
        } else {
          showError('Failed to delete document')
        }
      } catch (error) {
        console.error('Error deleting document:', error)
        showError('Error deleting document')
      }
    }
    
    // Close modal
    setDeleteModalOpen(false)
    setDocumentToDelete(null)
  }

  const handleDeleteCancel = () => {
    setDeleteModalOpen(false)
    setDocumentToDelete(null)
  }



  const handleEditDocument = () => {
    if (selectedDocument) {
      setDocumentToEdit(selectedDocument)
      setNewDocumentName(selectedDocument.name)
      setEditModalOpen(true)
    }
    handleMenuClose()
  }

  const handleEditConfirm = () => {
    if (documentToEdit && newDocumentName.trim()) {
      // Update document name locally (in real app, would call API)
      setDocuments(prev => 
        prev.map(doc => 
          doc.id === documentToEdit.id 
            ? { ...doc, name: newDocumentName.trim() }
            : doc
        )
      )
      
      // Update selected document if it's the one being edited
      if (selectedDocument?.id === documentToEdit.id) {
        setSelectedDocument((prev: any) => prev ? { ...prev, name: newDocumentName.trim() } : null)
      }
      
              showSuccess('Document name updated!')
      }
      
      // Close modal
      setEditModalOpen(false)
      setDocumentToEdit(null)
      setNewDocumentName('')
    }

  const handleEditCancel = () => {
    setEditModalOpen(false)
    setDocumentToEdit(null)
    setNewDocumentName('')
  }

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(+event.target.value)
    setPage(0)
  }

  if (loading) {
    return (
      <MainLayout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <CircularProgress size={60} />
        </Box>
      </MainLayout>
    )
  }

  // Helper components and functions
  function CircularConfidence({ value }: { value: number }) {
    const radius = 48;
    const circumference = 2 * Math.PI * radius;
    const dash = (value / 100) * circumference;
    return (
      <svg viewBox="0 0 120 120" style={{ width: '112px', height: '112px' }}>
        {/* Background circle */}
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth="10"
        />
        {/* Progress circle with gradient */}
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4338CA" />
            <stop offset="100%" stopColor="#7C3AED" />
          </linearGradient>
        </defs>
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="url(#progressGradient)"
          strokeWidth="10"
          strokeDasharray={`${dash} ${circumference - dash}`}
          strokeLinecap="round"
          transform="rotate(-90 60 60)"
          style={{
            filter: 'drop-shadow(0 2px 4px rgba(67, 56, 202, 0.3))'
          }}
        />
        {/* Center text */}
        <text
          x="60"
          y="60"
          dominantBaseline="middle"
          textAnchor="middle"
          style={{
            fontSize: '24px',
            fontWeight: '600',
            fill: '#111827',
            fontFamily: 'system-ui, -apple-system, sans-serif'
          }}
        >
          {value}%
        </text>
      </svg>
    );
  }

  function InfoRow({ k, v, style }: { k: string; v: string; style?: React.CSSProperties }) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', ...style }}>
        <span style={{ color: '#6B7280' }}>{k}</span>
        <span style={{ fontWeight: '500', color: '#111827' }}>{v}</span>
      </div>
    );
  }

  function Th({ children }: { children: React.ReactNode }) {
    return <th className="px-3 py-2 text-xs font-semibold uppercase tracking-wide text-gray-600">{children}</th>;
  }

  function Td({ children, className = "", style }: { children: React.ReactNode; className?: string; style?: React.CSSProperties }) {
    return <td className={`px-3 py-2 ${className}`} style={style}>{children}</td>;
  }

  function QualityCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="text-xs font-semibold uppercase tracking-wide text-gray-500">{label}</div>
        <div className="mt-1 text-2xl font-semibold text-gray-900">{value}</div>
        {hint && <div className="mt-2 text-xs text-gray-500">{hint}</div>}
      </div>
    );
  }

  function capitalize(s: string) {
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  function getFlag(term: string, value: string | number) {
    if (typeof value === 'string') return undefined;
    if (value > 200) return "High";
    if (value < 70) return "Low";
    return "Normal";
  }

  return (
    <MainLayout>
      <Box sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
          <Box>
            <Typography variant="h4" gutterBottom fontWeight="bold">
              All Documents
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Manage and search through {documents.length} documents
              {filteredDocuments.length !== documents.length && ` (${filteredDocuments.length} filtered)`}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
              Last updated: {lastRefreshTime.toLocaleTimeString()} • Auto-refresh: {documents.some(doc => doc.status === 'processing') ? 'Every 2 min' : 'Disabled'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', minWidth: '600px' }}>
            {/* Search and Filter Controls */}
            <TextField
              size="small"
              variant="outlined"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: '200px' }}
            />
            <FormControl size="small" sx={{ minWidth: '120px' }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                label="Status"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="processing">Processing</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </Select>
            </FormControl>
            {/* Action Buttons */}
            <Button 
              variant="outlined" 
              startIcon={refreshing ? <CircularProgress size={16} /> : <Speed />}
              disabled={refreshing}
              onClick={() => {
                if (refreshing) return
                setRefreshing(true)
                fetch('http://localhost:8007/api/v1/documents')
                  .then(response => response.json())
                  .then(data => {
                    const transformedDocuments = data.documents.map((doc: any) => {
                      const keyInfo = doc.ai_analysis?.key_information || null;
                      const fallbackEntities = keyInfo ? {
                        dates: keyInfo.dates_found || [],
                        names: keyInfo.potential_names || [],
                        organizations: keyInfo.organizations || [],
                        medical_terms: keyInfo.medical_terms || [],
                        numbers: keyInfo.numbers || [],
                        emails: keyInfo.emails || [],
                        phone_numbers: keyInfo.phone_numbers || [],
                        entity_count: (keyInfo.dates_found?.length || 0) + (keyInfo.potential_names?.length || 0) + (keyInfo.numbers?.length || 0) + (keyInfo.emails?.length || 0) + (keyInfo.phone_numbers?.length || 0),
                        success: true,
                      } : {};
                      const mergedEntities = (doc.extracted_entities && Object.keys(doc.extracted_entities).length > 0) ? doc.extracted_entities : fallbackEntities;
                      const entitiesFoundCount = (doc.extracted_entities && Object.keys(doc.extracted_entities).length > 0)
                        ? (doc.extracted_entities.entity_count || Object.values(doc.extracted_entities).reduce((acc: number, v: any) => acc + (Array.isArray(v) ? v.length : 0), 0))
                        : (fallbackEntities as any).entity_count || 0;
                      return ({
                      id: doc.id,
                      name: doc.filename,
                      type: doc.document_type,
                      status: doc.status,
                        uploadDate: doc.upload_date,
                        size: doc.file_size,
                      accuracy: doc.ocr_accuracy ? parseFloat(doc.ocr_accuracy) : null,
                        patientId: doc.patient_id || null,
                        providerId: doc.provider_id || null,
                        patientName: doc.patient_name || null,
                        providerName: doc.provider_name || null,
                      rawSize: doc.raw_size,
                      processingTime: doc.processing_time,
                        classificationConfidence: doc.confidence ? parseFloat(doc.confidence) : null,
                      mimeType: doc.mime_type,
                        entitiesFound: entitiesFoundCount,
                        entities: mergedEntities,
                        doclingResult: doc.docling_result || {},
                        aiAnalysis: doc.ai_analysis || {},
                        documentType: doc.document_type || 'unknown'
                      })
                    })
                    setDocuments(transformedDocuments)
                    documentsRef.current = transformedDocuments
                    setLastRefreshTime(new Date())
                    setPage(0) // Reset to first page when refreshing
                    setRefreshing(false)
                    showSuccess('Documents refreshed successfully!')
                  })
                  .catch(error => {
                    console.error('Error refreshing documents:', error)
                    setRefreshing(false)
                    showError('Failed to refresh documents')
                  })
              }}
            >
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Button 
              variant="contained" 
              startIcon={<CloudUpload />}
              href="/documents/upload"
            >
              Upload Document
            </Button>
          </Box>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: '#1976d2', mr: 2 }}>
                    <Description />
                  </Avatar>
                  <Box>
                    <Typography variant="h5" fontWeight="bold">
                      {documents.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Documents
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: '#16a34a', mr: 2 }}>
                    <CheckCircle />
                  </Avatar>
                  <Box>
                    <Typography variant="h5" fontWeight="bold">
                      {documents.filter(doc => doc.status === 'completed').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Completed
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: '#f59e0b', mr: 2 }}>
                    <Schedule />
                  </Avatar>
                  <Box>
                    <Typography variant="h5" fontWeight="bold">
                      {documents.filter(doc => doc.status === 'processing').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Processing
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: '#dc2626', mr: 2 }}>
                    <Error />
                  </Avatar>
                  <Box>
                    <Typography variant="h5" fontWeight="bold">
                      {documents.filter(doc => doc.status === 'failed').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Failed
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>



        {/* Main Content Layout */}
        <Box sx={{ 
          display: 'flex', 
          gap: 3, 
          height: 'calc(100vh - 400px)', 
          minHeight: '500px',
          mt: 2
        }}>
          {/* Left Panel - Document List */}
          <Box sx={{ 
            width: '35%', 
            minWidth: '350px',
            display: 'flex', 
            flexDirection: 'column',
            border: '1px solid #e0e0e0',
            borderRadius: 1,
            backgroundColor: 'white'
          }}>
            {/* Document List Header */}
            <Box sx={{ 
              p: 2, 
              borderBottom: '1px solid #e0e0e0', 
              backgroundColor: '#f8f9fa',
              borderTopLeftRadius: 4,
              borderTopRightRadius: 4
            }}>
              <Typography variant="h6" fontWeight="bold">
                Documents ({filteredDocuments.length})
              </Typography>
              {filteredDocuments.length > 0 && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                  Showing {paginatedDocuments.length} of {filteredDocuments.length} documents
                  {page > 0 && ` (Page ${page + 1})`}
                </Typography>
              )}
            </Box>
            
            {/* Document List - Scrollable */}
            <Box sx={{ 
              flexGrow: 1, 
              overflowY: 'auto',
              overflowX: 'hidden',
              borderRight: '1px solid #e0e0e0',
              '&::-webkit-scrollbar': {
                width: '12px',
              },
              '&::-webkit-scrollbar-track': {
                backgroundColor: '#f1f1f1',
                borderRadius: '6px',
              },
              '&::-webkit-scrollbar-thumb': {
                backgroundColor: '#c1c1c1',
                borderRadius: '6px',
                border: '2px solid #f1f1f1',
                '&:hover': {
                  backgroundColor: '#a8a8a8',
                },
              },
              '&::-webkit-scrollbar-corner': {
                backgroundColor: '#f1f1f1',
              },
            }}>
              {filteredDocuments.length === 0 ? (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="body1" color="text.secondary">
                    {documents.length === 0 ? 'No documents found' : 'No documents match your search criteria'}
                  </Typography>
                </Box>
              ) : (
                <List disablePadding>
                  {paginatedDocuments.map((doc) => (
                    <ListItem
                      key={doc.id}
                      button
                      onClick={() => handleDocumentSelect(doc)}
                      selected={doc.id === selectedDocumentId}
                      sx={{
                        borderBottom: '1px solid #f0f0f0',
                        '&.Mui-selected': {
                          backgroundColor: '#e3f2fd',
                          borderLeft: '4px solid #1976d2',
                          '&:hover': {
                            backgroundColor: '#e3f2fd',
                          }
                        },
                        '&:hover': {
                          backgroundColor: '#f5f5f5'
                        }
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: '#1976d2' }}>
                          <Description fontSize="small" />
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="subtitle2" sx={{ fontWeight: doc.id === selectedDocumentId ? 'bold' : 'normal' }}>
                            {doc.name}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" color="text.secondary" display="block">
                              {doc.type || 'Unknown Document'}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                              <Chip
                                label={doc.status.toUpperCase()}
                                color={getStatusColor(doc.status) as any}
                                size="small"
                                sx={{ height: 20, fontSize: '0.75rem' }}
                              />
                              <Typography variant="caption" color="text.secondary">
                                {doc.size}
                              </Typography>
                            </Box>
                          </Box>
                        }
                      />
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleMenuClick(e, doc)
                        }}
                        sx={{ ml: 1 }}
                      >
                        <MoreVert fontSize="small" />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
            
            {/* Pagination Footer */}
            {filteredDocuments.length > 0 && (
              <Box sx={{ 
                borderTop: '1px solid #e0e0e0', 
                backgroundColor: '#f8f9fa',
                borderBottomLeftRadius: 4,
                borderBottomRightRadius: 4
              }}>
                <TablePagination
                  rowsPerPageOptions={[5, 10, 25, 50]}
                  component="div"
                  count={filteredDocuments.length}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={handleChangePage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                  sx={{ 
                    '.MuiTablePagination-toolbar': { minHeight: 48 },
                    '.MuiTablePagination-selectLabel, .MuiTablePagination-displayedRows': {
                      fontSize: '0.875rem'
                    }
                  }}
                />
              </Box>
            )}
          </Box>

          {/* Right Panel - Document Details */}
          <Box sx={{ 
            flexGrow: 1,
            display: 'flex', 
            flexDirection: 'column',
            border: '1px solid #e0e0e0',
            borderRadius: 1,
            backgroundColor: 'white'
          }}>
            {currentSelectedDocument ? (
              <>
                {/* Content Body - Scrollable */}
                <Box sx={{ 
                  flexGrow: 1, 
                  overflowY: 'auto',
                  overflowX: 'hidden',
                  p: 3,
                  maxHeight: 'calc(100vh - 300px)',
                  backgroundColor: '#F9FAFB',
                  '&::-webkit-scrollbar': {
                    width: '12px',
                  },
                  '&::-webkit-scrollbar-track': {
                    backgroundColor: '#f1f1f1',
                    borderRadius: '6px',
                  },
                  '&::-webkit-scrollbar-thumb': {
                    backgroundColor: '#c1c1c1',
                    borderRadius: '6px',
                    border: '2px solid #f1f1f1',
                    '&:hover': {
                      backgroundColor: '#a8a8a8',
                    },
                  },
                  '&::-webkit-scrollbar-corner': {
                    backgroundColor: '#f1f1f1',
                  },
                }}>
                  
                  {/* Main Container */}
                  <div style={{ 
                    maxWidth: '1200px', 
                    margin: '0 auto', 
                    backgroundColor: 'white', 
                    borderRadius: '16px',
                    padding: '32px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                    minHeight: 'calc(100vh - 400px)',
                    border: '1px solid #F3F4F6'
                  }}>
                    
                    {/* Header */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
                      <div>
                        <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', margin: 0, lineHeight: '1.2' }}>Document Analysis</h1>
                        <p style={{ color: '#6B7280', marginTop: '8px', margin: 0, fontSize: '16px' }}>AI-powered insights and extracted information</p>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <span style={{ 
                          display: 'inline-flex', 
                          alignItems: 'center', 
                          gap: '8px', 
                          padding: '6px 16px', 
                          fontSize: '14px', 
                          backgroundColor: '#D1FAE5', 
                          color: '#047857', 
                          borderRadius: '9999px',
                          border: '1px solid #A7F3D0',
                          fontWeight: '500'
                        }}>
                          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'currentColor' }}></span>
                          {currentSelectedDocument?.status === 'completed' ? 'processed' : currentSelectedDocument?.status || 'unknown'}
                        </span>
                        <span style={{ 
                          display: 'inline-flex', 
                          alignItems: 'center', 
                          gap: '8px', 
                          padding: '6px 16px', 
                          fontSize: '14px', 
                          backgroundColor: '#F3F4F6', 
                          color: '#374151', 
                          borderRadius: '9999px',
                          border: '1px solid #E5E7EB',
                          fontWeight: '500'
                        }}>
                          Type: <span style={{ fontWeight: '600', textTransform: 'uppercase' }}>{currentSelectedDocument?.documentType || 'unknown'}</span>
                        </span>
                      </div>
                    </div>

                    {/* Top summary cards - 4 columns in 1 row */}
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(4, 1fr)', 
                      gap: '20px', 
                      marginBottom: '32px' 
                    }}>
                      {/* AI Confidence Card */}
                      <div style={{ 
                        borderRadius: '16px', 
                        border: '1px solid #E5E7EB', 
                        backgroundColor: 'white', 
                        padding: '20px', 
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)'
                      }}>
                        <div style={{ 
                          marginBottom: '12px', 
                          fontSize: '12px', 
                          fontWeight: '700', 
                          textTransform: 'uppercase', 
                          letterSpacing: '0.05em', 
                          color: '#6B7280' 
                        }}>AI CONFIDENCE</div>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
                          <CircularConfidence value={currentSelectedDocument?.classificationConfidence || 0} />
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                              <span style={{ fontSize: '14px', color: '#6B7280' }}>Model certainty</span>
                              <div style={{ 
                                display: 'inline-flex', 
                                padding: '4px 12px', 
                                fontSize: '12px', 
                                fontWeight: '600', 
                                backgroundColor: currentSelectedDocument?.classificationConfidence && currentSelectedDocument.classificationConfidence > 70 ? '#EEF2FF' : currentSelectedDocument?.classificationConfidence && currentSelectedDocument.classificationConfidence > 40 ? '#FEF3C7' : '#FEE2E2', 
                                color: currentSelectedDocument?.classificationConfidence && currentSelectedDocument.classificationConfidence > 70 ? '#4338CA' : currentSelectedDocument?.classificationConfidence && currentSelectedDocument.classificationConfidence > 40 ? '#D97706' : '#DC2626', 
                                borderRadius: '6px',
                                border: `1px solid ${currentSelectedDocument?.classificationConfidence && currentSelectedDocument.classificationConfidence > 70 ? '#C7D2FE' : currentSelectedDocument?.classificationConfidence && currentSelectedDocument.classificationConfidence > 40 ? '#FCD34D' : '#FECACA'}`
                              }}>
                                {currentSelectedDocument?.classificationConfidence && currentSelectedDocument.classificationConfidence > 70 ? 'High' : currentSelectedDocument?.classificationConfidence && currentSelectedDocument.classificationConfidence > 40 ? 'Medium' : 'Low'}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Document Overview Card */}
                      <div style={{ 
                        borderRadius: '16px', 
                        border: '1px solid #E5E7EB', 
                        backgroundColor: 'white', 
                        padding: '20px', 
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)'
                      }}>
                        <div style={{ 
                          marginBottom: '12px', 
                          fontSize: '12px', 
                          fontWeight: '700', 
                          textTransform: 'uppercase', 
                          letterSpacing: '0.05em', 
                          color: '#6B7280' 
                        }}>DOCUMENT OVERVIEW</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '14px' }}>
                          <InfoRow k="Language" v={currentSelectedDocument?.aiAnalysis?.language || 'EN'} />
                          <InfoRow k="Words" v={currentSelectedDocument?.aiAnalysis?.word_count || '0'} />
                          <InfoRow k="Entities" v={currentSelectedDocument?.entitiesFound?.toString() || '0'} />
                          <InfoRow k="Size" v={currentSelectedDocument?.size || '0 KB'} />
                        </div>
                      </div>

                      {/* Patient Card */}
                      <div style={{ 
                        borderRadius: '16px', 
                        border: '1px solid #E5E7EB', 
                        backgroundColor: 'white', 
                        padding: '20px', 
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)'
                      }}>
                        <div style={{ 
                          marginBottom: '12px', 
                          fontSize: '12px', 
                          fontWeight: '700', 
                          textTransform: 'uppercase', 
                          letterSpacing: '0.05em', 
                          color: '#6B7280' 
                        }}>PATIENT</div>
                        <div style={{ fontSize: '14px' }}>
                          <div style={{ fontWeight: '600', color: '#111827', marginBottom: '8px' }}>
                            {currentSelectedDocument?.patientName || 'Not Found'}
                          </div>
                          <div style={{ color: '#6B7280', marginBottom: '4px' }}>
                            DOB: {currentSelectedDocument?.aiAnalysis?.key_information?.dates_found?.[0] || 'Not Found'}
                          </div>
                          <div style={{ color: '#6B7280' }}>
                            MRN: {currentSelectedDocument?.patientId || 'Not Found'}
                          </div>
                        </div>
                      </div>

                      {/* Report Card */}
                      <div style={{ 
                        borderRadius: '16px', 
                        border: '1px solid #E5E7EB', 
                        backgroundColor: 'white', 
                        padding: '20px', 
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)'
                      }}>
                        <div style={{ 
                          marginBottom: '12px', 
                          fontSize: '12px', 
                          fontWeight: '700', 
                          textTransform: 'uppercase', 
                          letterSpacing: '0.05em', 
                          color: '#6B7280' 
                        }}>REPORT</div>
                        <div style={{ fontSize: '14px' }}>
                          <InfoRow k="Provider" v={currentSelectedDocument?.providerName || 'Not Found'} />
                          <InfoRow k="Report Date" v={currentSelectedDocument?.aiAnalysis?.key_information?.dates_found?.[0] || 'Not Found'} />
                        </div>
                      </div>
                    </div>

                    {/* Tabs */}
                    <div>
                      <div style={{ display: 'flex', gap: '0px', borderBottom: '1px solid #E5E7EB' }}>
                        {[
                          { id: "overview", name: "Overview" },
                          { id: "tests", name: "Test Results" },
                          { id: "entities", name: "Entities" },
                          { id: "preview", name: "Content Preview" },
                          { id: "quality", name: "Quality" },
                        ].map((t) => (
                          <button
                            key={t.id}
                            onClick={() => setActiveTab(t.id)}
                            style={{
                              marginBottom: '-1px',
                              padding: '12px 24px',
                              fontSize: '14px',
                              fontWeight: '500',
                              cursor: 'pointer',
                              border: 'none',
                              backgroundColor: 'transparent',
                              color: activeTab === t.id ? '#7C3AED' : '#6B7280',
                              borderBottom: activeTab === t.id ? '2px solid #7C3AED' : 'none',
                              transition: 'all 0.2s ease'
                            }}
                            onMouseEnter={(e) => {
                              if (activeTab !== t.id) e.currentTarget.style.color = '#111827';
                            }}
                            onMouseLeave={(e) => {
                              if (activeTab !== t.id) e.currentTarget.style.color = '#6B7280';
                            }}
                          >
                            {t.name}
                          </button>
                        ))}
                      </div>

                      {/* Tab panels */}
                      <div style={{ 
                        borderBottomLeftRadius: '12px', 
                        borderBottomRightRadius: '12px', 
                        borderTopRightRadius: '12px',
                        border: '1px solid #E5E7EB', 
                        backgroundColor: 'white', 
                        padding: '24px', 
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        minHeight: '400px'
                      }}>
                        {activeTab === "overview" && (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: 0 }}>What This Document Tells Us</h3>
                            <p style={{ color: '#374151', fontSize: '15px', lineHeight: '1.6', margin: 0 }}>
                              {currentSelectedDocument?.aiAnalysis?.summary || 
                               `This is a ${currentSelectedDocument?.documentType || 'document'} for ${currentSelectedDocument?.patientName || 'the patient'} with ${currentSelectedDocument?.entitiesFound || 0} extracted entities.`}
                            </p>

                            {currentSelectedDocument?.aiAnalysis?.key_information?.medical_terms?.some((term: string) => 
                              term.toLowerCase().includes('cholesterol') || term.toLowerCase().includes('glucose') || term.toLowerCase().includes('blood')
                            ) && (
                              <div style={{ marginTop: '8px', display: 'grid', gridTemplateColumns: '1fr', gap: '16px' }}>
                                <div style={{ 
                                  borderRadius: '12px', 
                                  border: '1px solid #FCD34D', 
                                  backgroundColor: 'rgba(254, 243, 199, 0.8)', 
                                  padding: '16px', 
                                  fontSize: '14px', 
                                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)' 
                                }}>
                                  <div style={{ marginBottom: '8px', fontWeight: '600', color: '#92400E' }}>Potential Flag</div>
                                  <div style={{ color: '#92400E', lineHeight: '1.5' }}>
                                    {currentSelectedDocument?.aiAnalysis?.alerts?.[0] || 'Medical values detected. Please review clinical context.'}
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {activeTab === "tests" && (
                          <div style={{ overflowX: 'auto' }}>
                            {currentSelectedDocument?.aiAnalysis?.test_results && currentSelectedDocument.aiAnalysis.test_results.length > 0 ? (
                              <table style={{ minWidth: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                                <thead>
                                  <tr style={{ backgroundColor: '#F9FAFB' }}>
                                    <Th>Name</Th>
                                    <Th>Value</Th>
                                    <Th>Unit</Th>
                                    <Th>Reference</Th>
                                    <Th>Flag</Th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {currentSelectedDocument.aiAnalysis.test_results.map((test: any, index: number) => (
                                    <tr key={index} style={{ borderBottom: '1px solid #F3F4F6' }}>
                                      <Td style={{ fontWeight: '500', color: '#111827' }}>{test.name || 'Unknown'}</Td>
                                      <Td>{test.value || 'N/A'}</Td>
                                      <Td>{test.unit || 'N/A'}</Td>
                                      <Td style={{ color: '#6B7280' }}>{test.reference || 'N/A'}</Td>
                                      <Td>
                                        <span style={{
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          gap: '8px',
                                          padding: '2px 10px',
                                          fontSize: '12px',
                                          fontWeight: '500',
                                          borderRadius: '9999px',
                                          backgroundColor: test.flag === 'High' || test.flag === 'Low' ? '#FEF2F2' : '#F0FDF4',
                                          color: test.flag === 'High' || test.flag === 'Low' ? '#DC2626' : '#16A34A',
                                          border: `1px solid ${test.flag === 'High' || test.flag === 'Low' ? '#FECACA' : '#BBF7D0'}`
                                        }}>
                                          {test.flag || 'Normal'}
                                        </span>
                                      </Td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            ) : (
                              <div style={{ textAlign: 'center', padding: '40px', color: '#6B7280' }}>
                                <Typography variant="body1">No test results found in this document</Typography>
                                <Typography variant="body2" sx={{ mt: 1 }}>
                                  Test results will appear here if they are extracted during document processing
                                </Typography>
                              </div>
                            )}
                          </div>
                        )}

                        {activeTab === "entities" && (
                          <div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                              {currentSelectedDocument?.entities && Object.keys(currentSelectedDocument.entities).length > 0 ? (
                                <>
                                  {/* Display extracted entities dynamically */}
                                  {currentSelectedDocument.entities.names && currentSelectedDocument.entities.names.map((name: string, index: number) => (
                                    <span key={`name-${index}`} style={{
                                      borderRadius: '9999px',
                                      backgroundColor: '#F3F4F6',
                                      padding: '4px 12px',
                                      fontSize: '14px',
                                      color: '#374151',
                                      border: '1px solid #E5E7EB'
                                    }}>
                                      {name}
                                    </span>
                                  ))}
                                  
                                  {currentSelectedDocument.entities.dates && currentSelectedDocument.entities.dates.map((date: string, index: number) => (
                                    <span key={`date-${index}`} style={{
                                      borderRadius: '9999px',
                                      backgroundColor: '#F3F4F6',
                                      padding: '4px 12px',
                                      fontSize: '14px',
                                      color: '#374151',
                                      border: '1px solid #E5E7EB'
                                    }}>
                                      Date: {date}
                                    </span>
                                  ))}
                                  
                                  {currentSelectedDocument.entities.organizations && currentSelectedDocument.entities.organizations.map((org: string, index: number) => (
                                    <span key={`org-${index}`} style={{
                                      borderRadius: '9999px',
                                      backgroundColor: '#F3F4F6',
                                      padding: '4px 12px',
                                      fontSize: '14px',
                                      color: '#374151',
                                      border: '1px solid #E5E7EB'
                                    }}>
                                      {org}
                                    </span>
                                  ))}
                                  
                                  {currentSelectedDocument.entities.medical_terms && currentSelectedDocument.entities.medical_terms.map((term: string, index: number) => (
                                    <span key={`term-${index}`} style={{
                                      borderRadius: '9999px',
                                      backgroundColor: '#F3F4F6',
                                      padding: '4px 12px',
                                      fontSize: '14px',
                                      color: '#374151',
                                      border: '1px solid #E5E7EB'
                                    }}>
                                      {term}
                                    </span>
                                  ))}
                                  
                                  {currentSelectedDocument.entities.numbers && currentSelectedDocument.entities.numbers.map((num: string, index: number) => (
                                    <span key={`num-${index}`} style={{
                                      borderRadius: '9999px',
                                      backgroundColor: '#F3F4F6',
                                      padding: '4px 12px',
                                      fontSize: '14px',
                                      color: '#374151',
                                      border: '1px solid #E5E7EB'
                                    }}>
                                      {num}
                                    </span>
                                  ))}
                                  
                                  {currentSelectedDocument.entities.emails && currentSelectedDocument.entities.emails.map((email: string, index: number) => (
                                    <span key={`email-${index}`} style={{
                                      borderRadius: '9999px',
                                      backgroundColor: '#F3F4F6',
                                      padding: '4px 12px',
                                      fontSize: '14px',
                                      color: '#374151',
                                      border: '1px solid #E5E7EB'
                                    }}>
                                      {email}
                                    </span>
                                  ))}
                                  
                                  {currentSelectedDocument.entities.phone_numbers && currentSelectedDocument.entities.phone_numbers.map((phone: string, index: number) => (
                                    <span key={`phone-${index}`} style={{
                                      borderRadius: '9999px',
                                      backgroundColor: '#F3F4F6',
                                      padding: '4px 12px',
                                      fontSize: '14px',
                                      color: '#374151',
                                      border: '1px solid #E5E7EB'
                                    }}>
                                      {phone}
                                    </span>
                                  ))}
                                </>
                              ) : (
                                <div style={{ textAlign: 'center', padding: '20px', color: '#6B7280' }}>
                                  <Typography variant="body1">No entities extracted from this document</Typography>
                                  <Typography variant="body2" sx={{ mt: 1 }}>
                                    Entities will appear here after document processing is complete
                                  </Typography>
                                </div>
                              )}
                            </div>
                            <p style={{ marginTop: '12px', fontSize: '12px', color: '#6B7280' }}>
                              Total entities: {currentSelectedDocument?.entitiesFound || 0}. (Auto-extracted; may include duplicates or partial phrases.)
                            </p>
                          </div>
                        )}

                        {activeTab === "preview" && (
                          <div>
                            <pre style={{
                              whiteSpace: 'pre-wrap',
                              borderRadius: '8px',
                              backgroundColor: '#F9FAFB',
                              padding: '12px',
                              fontSize: '14px',
                              color: '#1F2937',
                              border: '1px solid #E5E7EB',
                              fontFamily: 'monospace',
                              lineHeight: '1.5',
                              maxHeight: expanded ? 'none' : '300px',
                              overflow: expanded ? 'visible' : 'auto'
                            }}>
                              {currentSelectedDocument?.aiAnalysis?.extracted_text || 
                               currentSelectedDocument?.aiAnalysis?.summary ||
                               `Document: ${currentSelectedDocument?.name || 'Unknown'}
Type: ${currentSelectedDocument?.documentType || 'Unknown'}
Status: ${currentSelectedDocument?.status || 'Unknown'}
Upload Date: ${currentSelectedDocument?.uploadDate || 'Unknown'}
Size: ${currentSelectedDocument?.size || 'Unknown'}

No content preview available. The document may still be processing or content extraction failed.`}
                            </pre>
                            <button
                              onClick={() => setExpanded((v) => !v)}
                              style={{
                                marginTop: '12px',
                                padding: '6px 12px',
                                fontSize: '14px',
                                fontWeight: '500',
                                backgroundColor: 'white',
                                border: '1px solid #E5E7EB',
                                borderRadius: '8px',
                                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                                cursor: 'pointer'
                              }}
                              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F9FAFB'}
                              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                            >
                              {expanded ? "Show less" : "Expand"}
                            </button>
                          </div>
                        )}

                        {activeTab === "quality" && (
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                            <QualityCard 
                              label="AI Confidence" 
                              value={`${currentSelectedDocument?.classificationConfidence || 0}%`}
                              hint="Overall certainty in extraction/classification." 
                            />
                            <QualityCard 
                              label="Processing Status" 
                              value={currentSelectedDocument?.status || 'Unknown'} 
                              hint="Pipeline state at last run." 
                            />
                            <QualityCard 
                              label="Word Count" 
                              value={currentSelectedDocument?.aiAnalysis?.word_count || '0'} 
                              hint="Words identified in this document." 
                            />
                            <QualityCard 
                              label="OCR Accuracy" 
                              value={currentSelectedDocument?.accuracy ? `${currentSelectedDocument.accuracy}%` : 'N/A'} 
                              hint="Optical character recognition accuracy." 
                            />
                            <QualityCard 
                              label="Processing Time" 
                              value={currentSelectedDocument?.processingTime ? `${currentSelectedDocument.processingTime}s` : 'N/A'} 
                              hint="Time taken to process document." 
                            />
                            <QualityCard 
                              label="File Size" 
                              value={currentSelectedDocument?.size || 'Unknown'} 
                              hint="Original document file size." 
                            />
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Footer meta */}
                    <div style={{ 
                      marginTop: '24px', 
                      display: 'flex', 
                      flexWrap: 'wrap', 
                      alignItems: 'center', 
                      justifyContent: 'space-between', 
                      gap: '12px', 
                      fontSize: '12px', 
                      color: '#6B7280' 
                    }}>
                      <div>
                        Designed for: <span style={{ fontWeight: '500' }}>Detail View</span> • Language: {currentSelectedDocument?.aiAnalysis?.language || 'EN'} • Type: {currentSelectedDocument?.documentType || 'unknown'}
                      </div>
                      <div>
                        Last updated from source: {currentSelectedDocument?.uploadDate ? new Date(currentSelectedDocument.uploadDate).toLocaleDateString() : 'Unknown'} • Provider: {currentSelectedDocument?.providerName || 'Unknown'}
                      </div>
                    </div>
                  </div>
                </Box>

                {/* Action Buttons Footer */}
                <Box sx={{ 
                  p: 3, 
                  borderTop: '1px solid #e0e0e0', 
                  backgroundColor: '#f8f9fa',
                  borderBottomLeftRadius: 4,
                  borderBottomRightRadius: 4
                }}>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Button
                      variant="contained"
                      startIcon={<GetApp />}
                      onClick={handleDownloadDocument}
                    >
                      Download
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Edit />}
                      onClick={handleEditDocument}
                    >
                      Edit Name
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<Delete />}
                      onClick={handleDeleteDocument}
                    >
                      Delete
                    </Button>
                  </Box>
                </Box>
              </>
            ) : (
              <Box sx={{ 
                height: '100%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                flexDirection: 'column',
                color: 'text.secondary'
              }}>
                <Description sx={{ fontSize: 64, mb: 2, color: 'text.disabled' }} />
                <Typography variant="h6" gutterBottom>
                  Select a document to view details
                </Typography>
                <Typography variant="body2">
                  Choose a document from the list on the left to see its information
                </Typography>
              </Box>
            )}
          </Box>
        </Box>

        {/* Action Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem onClick={handleDownloadDocument}>
            <GetApp sx={{ mr: 1 }} fontSize="small" />
            Download
          </MenuItem>
          <MenuItem onClick={handleEditDocument}>
            <Edit sx={{ mr: 1 }} fontSize="small" />
            Edit Name
          </MenuItem>
          <MenuItem onClick={handleDeleteDocument} sx={{ color: 'error.main' }}>
            <Delete sx={{ mr: 1 }} fontSize="small" />
            Delete
          </MenuItem>
                </Menu>

        {/* Delete Confirmation Modal */}
        <Dialog
          open={deleteModalOpen}
          onClose={handleDeleteCancel}
          maxWidth="xs"
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: 2,
              bgcolor: '#2a2a2a',
              color: 'white'
            }
          }}
        >
          <DialogTitle sx={{ pb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Warning sx={{ color: '#f44336' }} />
              <Typography variant="h6" component="span">
                localhost:3006 says
              </Typography>
            </Box>
          </DialogTitle>
          <DialogContent sx={{ pb: 2 }}>
            <Typography>
              Are you sure you want to delete "{documentToDelete?.name}"?
            </Typography>
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
            <Button
              onClick={handleDeleteCancel}
              variant="outlined"
              sx={{
                color: 'white',
                borderColor: 'rgba(255, 255, 255, 0.3)',
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)'
                }
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleDeleteConfirm}
              variant="contained"
              color="error"
              sx={{
                bgcolor: '#f44336',
                '&:hover': {
                  bgcolor: '#d32f2f'
                }
              }}
            >
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        {/* Edit Document Modal */}
        <Dialog
          open={editModalOpen}
          onClose={handleEditCancel}
          maxWidth="sm"
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: 2,
              bgcolor: '#2a2a2a',
              color: 'white'
            }
          }}
        >
          <DialogTitle sx={{ pb: 2 }}>
            <Typography variant="h6">
              localhost:3006 says
            </Typography>
          </DialogTitle>
          <DialogContent sx={{ pb: 2 }}>
            <Typography sx={{ mb: 2 }}>
              Enter new document name:
            </Typography>
            <TextField
              fullWidth
              value={newDocumentName}
              onChange={(e) => setNewDocumentName(e.target.value)}
              variant="outlined"
              autoFocus
              sx={{
                '& .MuiOutlinedInput-root': {
                  color: 'white',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '& fieldset': {
                    borderColor: 'rgba(255, 255, 255, 0.3)',
                  },
                  '&:hover fieldset': {
                    borderColor: 'rgba(255, 255, 255, 0.5)',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#1976d2',
                  },
                },
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleEditConfirm()
                }
              }}
            />
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
            <Button
              onClick={handleEditCancel}
              variant="outlined"
              sx={{
                color: 'white',
                borderColor: 'rgba(255, 255, 255, 0.3)',
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                  backgroundColor: 'rgba(255, 255, 255, 0.1)'
                }
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleEditConfirm}
              variant="contained"
              disabled={!newDocumentName.trim()}
              sx={{
                bgcolor: '#1976d2',
                '&:hover': {
                  bgcolor: '#1565c0'
                },
                '&:disabled': {
                  bgcolor: 'rgba(255, 255, 255, 0.1)',
                  color: 'rgba(255, 255, 255, 0.3)'
                }
              }}
            >
              OK
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