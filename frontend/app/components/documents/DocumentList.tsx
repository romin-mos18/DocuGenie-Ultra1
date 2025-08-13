'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Typography,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Tooltip,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Visibility,
  Delete,
  Search,
  Refresh,
  Download,
  PlayArrow,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useAppSelector, useAppDispatch } from '@/store/store';
import { setDocuments, setFilters, setPagination } from '@/store/slices/documentSlice';
import { format } from 'date-fns';

export default function DocumentList() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const documents = useAppSelector((state) => state.documents.documents);
  const filters = useAppSelector((state) => state.documents.filters);
  const pagination = useAppSelector((state) => state.documents.pagination);

  const [searchTerm, setSearchTerm] = useState(filters.searchTerm || '');
  const [selectedStatus, setSelectedStatus] = useState(filters.status || 'all');
  const [selectedType, setSelectedType] = useState(filters.documentType || 'all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingDocuments, setDeletingDocuments] = useState<Set<number>>(new Set());
  const [notification, setNotification] = useState<{
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
    show: boolean;
  } | null>(null);

  // Show notification helper
  const showNotification = (type: 'success' | 'error' | 'info' | 'warning', message: string) => {
    setNotification({ type, message, show: true });
    // Auto-hide after 5 seconds
    setTimeout(() => setNotification(null), 5000);
  };

  // Fetch documents from backend
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch('http://localhost:8007/documents');
        if (response.ok) {
          const data = await response.json();
          console.log('Fetched documents:', data);
          
          // Transform backend data to match frontend structure
          const transformedDocuments = data.documents.map((doc: any) => ({
            id: parseInt(doc.id) || Math.random(),
            title: doc.filename || 'Untitled Document',
            filename: doc.filename || 'document',
            fileType: doc.file_type || 'unknown',
            fileSize: doc.file_size || 0,
            status: doc.status || 'uploaded',
            documentType: doc.document_type || 'unknown',
            createdAt: doc.upload_date || new Date().toISOString(),
            updatedAt: doc.upload_date || new Date().toISOString(),
            // Add AI analysis data if available
            ai_analysis: doc.ai_analysis || null
          }));
          
          dispatch(setDocuments(transformedDocuments));
          dispatch(setPagination({ total: transformedDocuments.length }));
        } else {
          console.error('Failed to fetch documents:', response.statusText);
          setError('Failed to fetch documents from server');
        }
      } catch (error) {
        console.error('Error fetching documents:', error);
        setError('Error connecting to server. Please check if the backend is running.');
        
        // Provide demo data for testing when backend is not available
        const demoDocuments = [
          {
            id: 1,
            title: 'Sample Medical Report',
            filename: 'medical_report.pdf',
            fileType: 'pdf',
            fileSize: 1024000,
            status: 'processed' as const,
            documentType: 'medical_report',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            ai_analysis: {
              document_type: 'medical_report',
              confidence: 0.95,
              entities_extracted: 15
            }
          },
          {
            id: 2,
            title: 'Lab Results',
            filename: 'lab_results.pdf',
            fileType: 'pdf',
            fileSize: 512000,
            status: 'processed' as const,
            documentType: 'lab_result',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            ai_analysis: {
              document_type: 'lab_result',
              confidence: 0.92,
              entities_extracted: 12
            }
          }
        ];
        
        dispatch(setDocuments(demoDocuments));
        dispatch(setPagination({ total: demoDocuments.length }));
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [dispatch]);

  const handleChangePage = (event: unknown, newPage: number) => {
    dispatch(setPagination({ page: newPage }));
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(
      setPagination({
        limit: parseInt(event.target.value, 10),
        page: 0,
      })
    );
  };

  const handleSearch = () => {
    dispatch(
      setFilters({
        searchTerm,
        status: selectedStatus === 'all' ? undefined : selectedStatus,
        documentType: selectedType === 'all' ? undefined : selectedType,
      })
    );
  };

  const handleViewDocument = (documentId: number) => {
    router.push(`/documents/${documentId}`);
  };

  const handleProcessDocument = async (documentId: number) => {
    try {
      // TODO: Replace with actual API call
      await fetch(`/api/documents/${documentId}/process`, {
        method: 'POST',
      });
    } catch (error) {
      console.error('Failed to process document:', error);
    }
  };

  // Backend health check
  const checkBackendHealth = async (): Promise<boolean> => {
    try {
      const response = await fetch('http://localhost:8007/health', { 
        method: 'GET',
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });
      return response.ok;
    } catch (error) {
      console.log('🌐 Backend health check failed:', error);
      return false;
    }
  };

  // Enhanced delete with health check
  const handleDeleteDocument = async (documentId: number, retryCount = 0) => {
    // Show confirmation dialog first
    if (!window.confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      return;
    }

    // Set loading state
    setDeletingDocuments(prev => new Set(prev).add(documentId));

    try {
      console.log(`🗑️ Attempting to delete document: ${documentId} (attempt ${retryCount + 1})`);
      
      // Check backend health first
      const backendHealthy = await checkBackendHealth();
      if (!backendHealthy) {
        showNotification('warning', 'Backend not available. Removing document from local state.');
        // Remove from local state for demo purposes
        const updatedDocuments = documents.filter(doc => doc.id !== documentId);
        dispatch(setDocuments(updatedDocuments));
        
        // Update pagination
        const newTotal = Math.max(0, pagination.total - 1);
        dispatch(setPagination({ ...pagination, total: newTotal }));
        return;
      }
      
      // Try to delete from backend
      const response = await fetch(`http://localhost:8007/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Document deleted successfully:', result);
        
        // Remove from local state immediately for better UX
        const updatedDocuments = documents.filter(doc => doc.id !== documentId);
        dispatch(setDocuments(updatedDocuments));
        
        // Update pagination
        const newTotal = Math.max(0, pagination.total - 1);
        dispatch(setPagination({ ...pagination, total: newTotal }));
        
        // Show success message
        showNotification('success', 'Document deleted successfully!');
        
        // Optional: Show a toast notification instead of alert
        console.log('🎉 Document deletion completed successfully');
        
      } else {
        // Handle different HTTP error codes
        let errorMessage = 'Failed to delete document';
        
        if (response.status === 404) {
          errorMessage = 'Document not found. It may have already been deleted.';
        } else if (response.status === 400) {
          errorMessage = 'Invalid request. Please check the document ID.';
        } else if (response.status === 500) {
          errorMessage = 'Server error. Please try again later.';
        } else {
          errorMessage = `Delete failed with status: ${response.status}`;
        }
        
        console.error('❌ Delete failed:', response.status, errorMessage);
        
        // Offer retry for certain errors
        if ((response.status === 500 || response.status >= 500) && retryCount < 2) {
          const shouldRetry = window.confirm(
            `${errorMessage}\n\nWould you like to retry? (${2 - retryCount} attempts remaining)`
          );
          if (shouldRetry) {
            showNotification('warning', `Retrying delete operation... (attempt ${retryCount + 2})`);
            setTimeout(() => handleDeleteDocument(documentId, retryCount + 1), 1000);
            return;
          }
        }
        
        showNotification('error', errorMessage);
      }
      
    } catch (error) {
      console.error('❌ Error during document deletion:', error);
      
      // Handle different types of errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        // Network error - backend not available
        console.log('🌐 Backend not available, removing from local state');
        
        // Remove from local state for demo purposes
        const updatedDocuments = documents.filter(doc => doc.id !== documentId);
        dispatch(setDocuments(updatedDocuments));
        
        // Update pagination
        const newTotal = Math.max(0, pagination.total - 1);
        dispatch(setPagination({ ...pagination, total: newTotal }));
        
        showNotification('info', 'Document removed from local state (backend not available)');
        
      } else if (error instanceof Error) {
        // Other JavaScript errors
        showNotification('error', `Error: ${error.message}`);
      } else {
        // Unknown error
        showNotification('error', 'An unexpected error occurred. Please try again.');
      }
      
    } finally {
      // Clear loading state
      setDeletingDocuments(prev => {
        const newSet = new Set(prev);
        newSet.delete(documentId);
        return newSet;
      });
    }
  };

  const handleDownloadDocument = async (documentId: number) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/documents/${documentId}/download`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'document';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download document:', error);
    }
  };

  const handleRefresh = () => {
    // Trigger a refresh by re-fetching documents
    window.location.reload();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'uploaded':
        return 'info';
      case 'processing':
        return 'warning';
      case 'processed':
        return 'success';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Notification System */}
      {notification && (
        <Alert 
          severity={notification.type} 
          sx={{ mb: 2 }}
          onClose={() => setNotification(null)}
        >
          {notification.message}
        </Alert>
      )}
      
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            label="Search"
            variant="outlined"
            size="small"
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

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={selectedStatus}
              label="Status"
              onChange={(e) => setSelectedStatus(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="uploaded">Uploaded</MenuItem>
              <MenuItem value="processing">Processing</MenuItem>
              <MenuItem value="processed">Processed</MenuItem>
              <MenuItem value="error">Error</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={selectedType}
              label="Type"
              onChange={(e) => setSelectedType(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="medical_report">Medical Report</MenuItem>
              <MenuItem value="lab_result">Lab Result</MenuItem>
              <MenuItem value="prescription">Prescription</MenuItem>
              <MenuItem value="consent_form">Consent Form</MenuItem>
              <MenuItem value="insurance">Insurance</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            onClick={handleSearch}
            startIcon={<Search />}
          >
            Search
          </Button>

          <Button
            variant="outlined"
            onClick={() => {
              setSearchTerm('');
              setSelectedStatus('all');
              setSelectedType('all');
              dispatch(setFilters({}));
            }}
            startIcon={<Refresh />}
          >
            Reset
          </Button>

          <Button
            variant="outlined"
            onClick={handleRefresh}
            startIcon={<Refresh />}
          >
            Refresh
          </Button>
        </Box>
      </Paper>

      {/* Document Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Uploaded</TableCell>
              <TableCell>Size</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : error ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Alert severity="error">{error}</Alert>
                </TableCell>
              </TableRow>
            ) : documents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No documents found.
                </TableCell>
              </TableRow>
            ) : (
              documents.map((document) => (
                <TableRow key={document.id}>
                  <TableCell>
                    <Typography variant="body2" noWrap>
                      {document.title}
                    </Typography>
                    <Typography variant="caption" color="textSecondary" noWrap>
                      {document.filename}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={document.documentType || 'Unknown'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={document.status}
                      size="small"
                      color={getStatusColor(document.status)}
                    />
                  </TableCell>
                  <TableCell>
                    {format(new Date(document.createdAt), 'MMM d, yyyy')}
                  </TableCell>
                  <TableCell>
                    {document.fileSize ? `${(document.fileSize / 1024 / 1024).toFixed(2)} MB` : 'Unknown'}
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="View">
                      <IconButton
                        size="small"
                        onClick={() => handleViewDocument(document.id)}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Process">
                      <IconButton
                        size="small"
                        onClick={() => handleProcessDocument(document.id)}
                        disabled={
                          document.status === 'processing' ||
                          document.status === 'processed'
                        }
                      >
                        <PlayArrow />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Download">
                      <IconButton
                        size="small"
                        onClick={() => handleDownloadDocument(document.id)}
                      >
                        <Download />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteDocument(document.id)}
                        data-document-id={document.id}
                        disabled={deletingDocuments.has(document.id)}
                      >
                        {deletingDocuments.has(document.id) ? (
                          <CircularProgress size={20} />
                        ) : (
                          <Delete />
                        )}
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={pagination.total}
          rowsPerPage={pagination.limit}
          page={pagination.page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  );
}
