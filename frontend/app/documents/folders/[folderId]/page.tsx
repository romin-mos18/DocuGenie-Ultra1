'use client'

import React, { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import MainLayout from '../../../components/layout/MainLayout'
import NotificationPortal from '../../../components/common/NotificationPortal'
import { useNotification } from '../../../../lib/hooks/useNotification'
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  Button,
  Grid,
  Card,
  CardContent,
  Avatar,
  CircularProgress,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material'
import {
  Search,
  Folder,
  Description,
  TableChart,
  TextSnippet,
  DataObject,
  Image,
  ArrowBack,
  CloudUpload,
  Visibility,
  Download,
  Delete,
  Refresh,
  FilterList,
  Sort,
  CalendarToday,
  Storage,
  AccessTime,
  CheckCircle,
  Warning,
  Error
} from '@mui/icons-material'

interface Document {
  id: string
  filename: string
  document_type: string
  file_size: number
  upload_date: string
  status: string
  processing_status?: string
  ai_confidence?: number
  extracted_text?: string
  ai_analysis?: {
    classification?: {
      document_type?: string
      confidence?: number
    }
    entities?: any
    language?: any
    processing_timestamp?: string
    text_preview?: string
    word_count?: number
    key_information?: any
  }
}

interface FolderInfo {
  id: string
  name: string
  icon: React.ReactNode
  color: string
  description: string
  extensions: string[]
}

export default function FolderViewPage() {
  const router = useRouter()
  const params = useParams()
  const folderId = params.folderId as string
  
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)
  const [documents, setDocuments] = useState<Document[]>([])
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([])
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list')
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'size'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Folder information mapping
  const folderInfo: Record<string, FolderInfo> = {
    pdf: {
      id: 'pdf',
      name: 'PDF Documents',
      icon: <Description />,
      color: '#DC2626',
      description: 'Portable Document Format files',
      extensions: ['.pdf']
    },
    docs: {
      id: 'docs',
      name: 'Word Documents',
      icon: <Description />,
      color: '#2563EB',
      description: 'Microsoft Word and text documents',
      extensions: ['.doc', '.docx', '.txt', '.rtf']
    },
    xls: {
      id: 'xls',
      name: 'Spreadsheets',
      icon: <TableChart />,
      color: '#16A34A',
      description: 'Excel and spreadsheet files',
      extensions: ['.xls', '.xlsx', '.csv']
    },
    csv: {
      id: 'csv',
      name: 'CSV Files',
      icon: <TableChart />,
      color: '#059669',
      description: 'Comma-separated values',
      extensions: ['.csv']
    },
    txt: {
      id: 'txt',
      name: 'Text Files',
      icon: <TextSnippet />,
      color: '#7C3AED',
      description: 'Plain text documents',
      extensions: ['.txt', '.md', '.log']
    },
    json: {
      id: 'json',
      name: 'JSON Files',
      icon: <DataObject />,
      color: '#EA580C',
      description: 'JavaScript Object Notation',
      extensions: ['.json']
    },
    image: {
      id: 'image',
      name: 'Images',
      icon: <Image />,
      color: '#DB2777',
      description: 'Image and media files',
      extensions: ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
    }
  }

  const currentFolder = folderInfo[folderId]

  // Notification system
  const { notification, showSuccess, showError, showWarning, showInfo, hideNotification } = useNotification()

  // Fetch documents for the specific folder
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setLoading(true)
        const response = await fetch('http://localhost:8007/api/v1/documents')
        if (response.ok) {
          const data = await response.json()
          const allDocuments = data.documents || []
          
          // Filter documents by folder type
          let folderDocuments: Document[] = []
          
          if (folderId === 'pdf') {
            folderDocuments = allDocuments.filter((doc: Document) => 
              doc.document_type?.toLowerCase() === 'pdf' || 
              doc.filename?.toLowerCase().endsWith('.pdf')
            )
          } else if (folderId === 'docs') {
            folderDocuments = allDocuments.filter((doc: Document) => 
              ['doc', 'docx', 'txt', 'rtf'].includes(doc.document_type?.toLowerCase()) ||
              ['.doc', '.docx', '.txt', '.rtf'].some(ext => 
                doc.filename?.toLowerCase().endsWith(ext)
              )
            )
          } else if (folderId === 'xls') {
            folderDocuments = allDocuments.filter((doc: Document) => 
              ['xls', 'xlsx'].includes(doc.document_type?.toLowerCase()) ||
              ['.xls', '.xlsx'].some(ext => 
                doc.filename?.toLowerCase().endsWith(ext)
              )
            )
          } else if (folderId === 'csv') {
            folderDocuments = allDocuments.filter((doc: Document) => 
              doc.document_type?.toLowerCase() === 'csv' ||
              doc.filename?.toLowerCase().endsWith('.csv')
            )
          } else if (folderId === 'txt') {
            folderDocuments = allDocuments.filter((doc: Document) => 
              ['txt', 'md', 'log'].includes(doc.document_type?.toLowerCase()) ||
              ['.txt', '.md', '.log'].some(ext => 
                doc.filename?.toLowerCase().endsWith(ext)
              )
            )
          } else if (folderId === 'json') {
            folderDocuments = allDocuments.filter((doc: Document) => 
              doc.document_type?.toLowerCase() === 'json' ||
              doc.filename?.toLowerCase().endsWith('.json')
            )
          } else if (folderId === 'image') {
            folderDocuments = allDocuments.filter((doc: Document) => 
              ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'].includes(doc.document_type?.toLowerCase()) ||
              ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'].some(ext => 
                doc.filename?.toLowerCase().endsWith(ext)
              )
            )
          }
          
          setDocuments(folderDocuments)
          setFilteredDocuments(folderDocuments)
        }
      } catch (error) {
        console.error('Error fetching documents:', error)
        showError('Failed to load documents')
      } finally {
        setLoading(false)
      }
    }

    if (folderId) {
      fetchDocuments()
    }
  }, [folderId])

  // Filter and sort documents
  useEffect(() => {
         let filtered = documents.filter(doc =>
       (doc.filename || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
       getDocumentType(doc.filename, doc.document_type, doc.ai_analysis).toLowerCase().includes(searchTerm.toLowerCase())
     )

    // Sort documents
    filtered.sort((a, b) => {
      let aValue: any, bValue: any
      
             if (sortBy === 'date') {
         aValue = new Date(a.upload_date || new Date()).getTime()
         bValue = new Date(b.upload_date || new Date()).getTime()
       } else if (sortBy === 'name') {
         aValue = (a.filename || '').toLowerCase()
         bValue = (b.filename || '').toLowerCase()
       } else if (sortBy === 'size') {
         aValue = a.file_size || 0
         bValue = b.file_size || 0
       }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    setFilteredDocuments(filtered)
  }, [documents, searchTerm, sortBy, sortOrder])

  const handleBackToFolders = () => {
    router.push('/documents/folders')
  }

  const handleUploadDocument = () => {
    router.push('/documents/upload')
  }

  const handleDocumentClick = (document: Document) => {
    setSelectedDocument(document)
  }

  const handleCloseDetails = () => {
    setSelectedDocument(null)
  }

  const getFileIcon = (filename: string) => {
    if (!filename) return <Description />
    
    const ext = filename.split('.').pop()?.toLowerCase()
    if (['pdf'].includes(ext || '')) return <Description />
    if (['doc', 'docx', 'txt', 'rtf', 'md'].includes(ext || '')) return <TextSnippet />
    if (['xls', 'xlsx', 'csv'].includes(ext || '')) return <TableChart />
    if (['json', 'xml'].includes(ext || '')) return <DataObject />
    if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'].includes(ext || '')) return <Image />
    return <Description />
  }

  const formatDocumentType = (docType: string) => {
    // Convert backend document types to user-friendly names
    const typeMapping: Record<string, string> = {
      // Medical/Healthcare
      'medical_report': 'Medical Report',
      'lab_result': 'Lab Result',
      'prescription': 'Prescription',
      'clinical_trial': 'Clinical Trial',
      'consent_form': 'Consent Form',
      
      // Financial/Business
      'billing': 'Billing',
      'insurance': 'Insurance',
      'administrative': 'Administrative',
      
      // Default formatting
      'other': 'Document',
      'unknown': 'Document'
    }
    
    // If we have a mapping, use it
    if (typeMapping[docType]) {
      return typeMapping[docType]
    }
    
    // Otherwise, format the type nicely (e.g., "medical_report" -> "Medical Report")
    return docType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const getDocumentType = (filename: string, documentType?: string, aiAnalysis?: any) => {
    if (!filename) return 'Document'
    
    // Priority 1: Use AI-classified document type from backend (most accurate)
    // Check multiple possible locations for AI classification
    const aiDocType = aiAnalysis?.classification?.document_type || 
                     aiAnalysis?.document_type || 
                     documentType;
    
    if (aiDocType && aiDocType !== 'unknown' && aiDocType !== 'other' && aiDocType !== 'Unknown') {
      console.log(`🤖 Folder view using AI classification: ${aiDocType} for ${filename}`);
      return formatDocumentType(aiDocType);
    }
    
    // Priority 2: Try to use any available classification data
    if (documentType && documentType !== 'Unknown' && documentType !== 'unknown' && documentType !== 'other') {
      return formatDocumentType(documentType);
    }
    
    // Log when no AI classification is available
    console.warn(`⚠️ Folder view: No AI classification available for ${filename}`);
    console.log('AI Analysis:', aiAnalysis);
    console.log('Document Type:', documentType);
    
    // Priority 3: Return generic type - ALL classification should come from AI content analysis
    return 'Document - Needs AI Analysis'
  }

  const getStatusIcon = (status: string) => {
    if (!status) return <Warning sx={{ color: '#F59E0B' }} />
    
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle sx={{ color: '#16A340' }} />
      case 'processing':
        return <CircularProgress size={16} />
      case 'pending':
        return <Warning sx={{ color: '#F59E0B' }} />
      case 'error':
        return <Error sx={{ color: '#DC2626' }} />
      default:
        return <Warning sx={{ color: '#F59E0B' }} />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (!bytes || bytes === 0) return 'Small'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Recent'
    
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (error) {
      return 'Recent'
    }
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

  if (!currentFolder) {
    return (
      <MainLayout>
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="error">
            Folder not found
          </Typography>
          <Button onClick={handleBackToFolders} sx={{ mt: 2 }}>
            Back to Folders
          </Button>
        </Box>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <Box sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar 
              sx={{ 
                bgcolor: currentFolder.color, 
                width: 56, 
                height: 56,
                boxShadow: `0 4px 12px ${currentFolder.color}40`
              }}
            >
              {currentFolder.icon}
            </Avatar>
            <Box>
              <Typography variant="h4" gutterBottom fontWeight="bold">
                {currentFolder.name}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                {currentFolder.description}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                {filteredDocuments.length} documents • {currentFolder.extensions.join(', ')}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button 
              variant="outlined" 
              startIcon={<ArrowBack />}
              onClick={handleBackToFolders}
            >
              Back to Folders
            </Button>
            <Button 
              variant="contained" 
              startIcon={<CloudUpload />}
              onClick={handleUploadDocument}
            >
              Upload Document
            </Button>
          </Box>
        </Box>

        {/* Search and Controls */}
        <Paper sx={{ p: 3, mb: 3, borderRadius: '16px' }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="medium"
                variant="outlined"
                placeholder={`Search in ${currentFolder.name.toLowerCase()}...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
                sx={{ 
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '12px',
                    backgroundColor: 'white'
                  }
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant={viewMode === 'list' ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => setViewMode('list')}
                  startIcon={<FilterList />}
                >
                  List
                </Button>
                <Button
                  variant={viewMode === 'grid' ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => setViewMode('grid')}
                  startIcon={<Sort />}
                >
                  Grid
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  startIcon={<Sort />}
                >
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setSortBy(sortBy === 'date' ? 'name' : sortBy === 'name' ? 'size' : 'date')}
                >
                  {sortBy === 'date' ? 'Date' : sortBy === 'name' ? 'Name' : 'Size'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Documents List/Grid */}
        {viewMode === 'list' ? (
          <Paper sx={{ borderRadius: '16px', overflow: 'hidden' }}>
            <List>
              {filteredDocuments.map((doc, index) => (
                <React.Fragment key={doc.id}>
                  <ListItem 
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': { backgroundColor: '#f8fafc' },
                      py: 2
                    }}
                    onClick={() => handleDocumentClick(doc)}
                  >
                    <ListItemIcon>
                                           <Avatar sx={{ bgcolor: currentFolder.color, width: 40, height: 40 }}>
                       {getFileIcon(doc.filename || 'unknown')}
                     </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                     <Typography variant="subtitle1" fontWeight="600">
                             {doc.filename || 'Document'}
                           </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip 
                              label={getDocumentType(doc.filename, doc.document_type, doc.ai_analysis).toUpperCase()} 
                              size="small" 
                              sx={{ 
                                backgroundColor: `${currentFolder.color}15`,
                                color: currentFolder.color,
                                fontWeight: '600'
                              }}
                            />
                            {doc.ai_analysis?.classification?.confidence && (
                              <Chip 
                                label={`${(doc.ai_analysis.classification.confidence * 100).toFixed(2)}%`}
                                size="small"
                                sx={{ 
                                  backgroundColor: '#f3f4f6',
                                  color: '#6b7280',
                                  fontSize: '0.7rem',
                                  height: '20px'
                                }}
                              />
                            )}
                          </Box>
                        </Box>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 0.5 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <Storage sx={{ fontSize: 16, color: 'text.secondary' }} />
                                                         <Typography variant="caption" color="text.secondary">
                               {formatFileSize(doc.file_size || 0)}
                             </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <CalendarToday sx={{ fontSize: 16, color: 'text.secondary' }} />
                                                         <Typography variant="caption" color="text.secondary">
                               {formatDate(doc.upload_date || new Date().toISOString())}
                             </Typography>
                          </Box>
                                                     <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                             {getStatusIcon(doc.status || 'unknown')}
                             <Typography variant="caption" color="text.secondary">
                               {doc.status || 'Pending'}
                             </Typography>
                           </Box>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => handleDocumentClick(doc)}>
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download">
                          <IconButton size="small">
                            <Download />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton size="small" color="error">
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < filteredDocuments.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {filteredDocuments.map((doc) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={doc.id}>
                <Card
                  sx={{
                    height: '280px',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    border: '1px solid #e0e0e0',
                    borderRadius: '16px',
                    backgroundColor: 'white',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                      borderColor: currentFolder.color
                    }
                  }}
                  onClick={() => handleDocumentClick(doc)}
                >
                  <CardContent sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column', 
                    justifyContent: 'space-between',
                    p: 3
                  }}>
                    {/* Document Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                                             <Avatar 
                         sx={{ 
                           bgcolor: currentFolder.color, 
                           width: 48, 
                           height: 48
                         }}
                       >
                         {getFileIcon(doc.filename || 'unknown')}
                       </Avatar>
                      <Box sx={{ flex: 1 }}>
                                                 <Typography variant="h6" fontWeight="bold" noWrap>
                           {doc.filename || 'Document'}
                         </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip 
                            label={getDocumentType(doc.filename, doc.document_type, doc.ai_analysis).toUpperCase()} 
                            size="small" 
                            sx={{ 
                              backgroundColor: `${currentFolder.color}15`,
                              color: currentFolder.color,
                              fontWeight: '600'
                            }}
                          />
                          {doc.ai_analysis?.classification?.confidence && (
                            <Chip 
                              label={`${(doc.ai_analysis.classification.confidence * 100).toFixed(2)}%`}
                              size="small"
                              sx={{ 
                                backgroundColor: '#f3f4f6',
                                color: '#6b7280',
                                fontSize: '0.7rem',
                                height: '20px'
                              }}
                            />
                          )}
                        </Box>
                      </Box>
                    </Box>

                    {/* Document Info */}
                    <Box sx={{ flexGrow: 1 }}>
                      <Stack spacing={1}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Storage sx={{ fontSize: 16, color: 'text.secondary' }} />
                                                     <Typography variant="body2" color="text.secondary">
                             {formatFileSize(doc.file_size || 0)}
                           </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CalendarToday sx={{ fontSize: 16, color: 'text.secondary' }} />
                                                     <Typography variant="body2" color="text.secondary">
                             {formatDate(doc.upload_date || new Date().toISOString())}
                           </Typography>
                        </Box>
                                                 <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                           {getStatusIcon(doc.status || 'unknown')}
                           <Typography variant="body2" color="text.secondary">
                             {doc.status || 'Pending'}
                           </Typography>
                         </Box>
                      </Stack>
                    </Box>

                    {/* Document Actions */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        Click to view
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton size="small">
                          <Visibility />
                        </IconButton>
                        <IconButton size="small">
                          <Download />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Empty State */}
        {filteredDocuments.length === 0 && (
          <Box sx={{ 
            textAlign: 'center', 
            py: 8, 
            color: 'text.secondary' 
          }}>
            <Folder sx={{ fontSize: 64, mb: 2, color: 'text.disabled' }} />
            <Typography variant="h6" gutterBottom>
              No documents found
            </Typography>
            <Typography variant="body2">
              {searchTerm ? 'Try adjusting your search terms' : 'This folder is empty. Upload some documents to get started!'}
            </Typography>
            {!searchTerm && (
              <Button 
                variant="contained" 
                startIcon={<CloudUpload />}
                onClick={handleUploadDocument}
                sx={{ mt: 2 }}
              >
                Upload Document
              </Button>
            )}
          </Box>
        )}

        {/* Document Details Dialog */}
        {selectedDocument && (
          <Paper
            sx={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '90%',
              maxWidth: '800px',
              maxHeight: '90vh',
              overflow: 'auto',
              zIndex: 1300,
              p: 3,
              borderRadius: '16px',
              boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" fontWeight="bold">
                Document Details
              </Typography>
              <IconButton onClick={handleCloseDetails}>
                <ArrowBack />
              </IconButton>
            </Box>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                                     <Avatar 
                     sx={{ 
                       bgcolor: currentFolder.color, 
                       width: 64, 
                       height: 64
                     }}
                   >
                     {getFileIcon(selectedDocument.filename || 'unknown')}
                   </Avatar>
                  <Box>
                                         <Typography variant="h6" fontWeight="bold">
                       {selectedDocument.filename || 'Document'}
                     </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip 
                        label={getDocumentType(selectedDocument.filename, selectedDocument.document_type, selectedDocument.ai_analysis).toUpperCase()} 
                        sx={{ 
                          backgroundColor: `${currentFolder.color}15`,
                          color: currentFolder.color,
                          fontWeight: '600'
                        }}
                      />
                      {selectedDocument.ai_analysis?.classification?.confidence && (
                        <Chip 
                          label={`${(selectedDocument.ai_analysis.classification.confidence * 100).toFixed(2)}%`}
                          size="small"
                          sx={{ 
                            backgroundColor: '#f3f4f6',
                            color: '#6b7280',
                            fontSize: '0.7rem',
                            height: '20px'
                          }}
                        />
                      )}
                    </Box>
                  </Box>
                </Box>
                
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      File Size
                    </Typography>
                                         <Typography variant="body1">
                       {formatFileSize(selectedDocument.file_size || 0)}
                     </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Upload Date
                    </Typography>
                                         <Typography variant="body1">
                       {formatDate(selectedDocument.upload_date || new Date().toISOString())}
                     </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Status
                    </Typography>
                                         <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                       {getStatusIcon(selectedDocument.status || 'unknown')}
                       <Typography variant="body1">
                         {selectedDocument.status || 'Pending'}
                       </Typography>
                     </Box>
                  </Box>
                </Stack>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Actions
                </Typography>
                <Stack spacing={2}>
                  <Button
                    variant="contained"
                    startIcon={<Download />}
                    fullWidth
                  >
                    Download Document
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Visibility />}
                    fullWidth
                  >
                    View Full Text
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<Delete />}
                    fullWidth
                  >
                    Delete Document
                  </Button>
                </Stack>
                
                                 {selectedDocument.extracted_text && selectedDocument.extracted_text.length > 0 && (
                   <Box sx={{ mt: 3 }}>
                     <Typography variant="h6" gutterBottom>
                       Extracted Text Preview
                     </Typography>
                     <Paper sx={{ p: 2, backgroundColor: '#f8fafc', maxHeight: '200px', overflow: 'auto' }}>
                       <Typography variant="body2">
                         {selectedDocument.extracted_text.substring(0, 300)}...
                       </Typography>
                     </Paper>
                   </Box>
                 )}
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* Portal Notification System */}
        <NotificationPortal 
          notification={notification} 
          onClose={hideNotification} 
        />
      </Box>
    </MainLayout>
  )
}
