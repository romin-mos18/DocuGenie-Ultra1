'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import MainLayout from '../../components/layout/MainLayout'
import NotificationPortal from '../../components/common/NotificationPortal'
import DocumentSearchResults from '../../components/folders/DocumentSearchResults'
import { useNotification } from '../../../lib/hooks/useNotification'
import { documentsApi } from '../../../lib/api/documents'
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
  Stack
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
  CloudUpload
} from '@mui/icons-material'

interface FolderType {
  id: string
  name: string
  icon: React.ReactNode
  color: string
  count: number
  description: string
  extensions: string[]
}

interface Document {
  id: string
  filename: string
  document_type: string
  file_size: number
  upload_date: string
  status: string
  ai_analysis?: {
    classification?: {
      document_type?: string
      confidence?: number
    }
    entity_count?: number
    document_type?: string
    confidence?: number
    processing_method?: string
    extraction_successful?: boolean
    analysis_successful?: boolean
    word_count?: number
    processing_time?: number
  }
  folder?: {
    id: string
    name: string
    color: string
    icon: React.ReactNode
  }
}

export default function FoldersPage() {
  const router = useRouter()
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)
  const [searchResults, setSearchResults] = useState<Document[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [folders, setFolders] = useState<FolderType[]>([
    {
      id: 'pdf',
      name: 'PDF Documents',
      icon: <Description />,
      color: '#DC2626',
      count: 0,
      description: 'Portable Document Format files',
      extensions: ['.pdf']
    },
    {
      id: 'docs',
      name: 'Word Documents',
      icon: <Description />,
      color: '#2563EB',
      count: 0,
      description: 'Microsoft Word and text documents',
      extensions: ['.doc', '.docx', '.txt', '.rtf']
    },
    {
      id: 'xls',
      name: 'Spreadsheets',
      icon: <TableChart />,
      color: '#16A34A',
      count: 0,
      description: 'Excel and spreadsheet files',
      extensions: ['.xls', '.xlsx', '.csv']
    },
    {
      id: 'csv',
      name: 'CSV Files',
      icon: <TableChart />,
      color: '#059669',
      count: 0,
      description: 'Comma-separated values',
      extensions: ['.csv']
    },
    {
      id: 'txt',
      name: 'Text Files',
      icon: <TextSnippet />,
      color: '#7C3AED',
      count: 0,
      description: 'Plain text documents',
      extensions: ['.txt', '.md', '.log']
    },
    {
      id: 'json',
      name: 'JSON Files',
      icon: <DataObject />,
      color: '#EA580C',
      count: 0,
      description: 'JavaScript Object Notation',
      extensions: ['.json']
    },
    {
      id: 'image',
      name: 'Images',
      icon: <Image />,
      color: '#DB2777',
      count: 0,
      description: 'Image and media files',
      extensions: ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
    }
  ])

  // Notification system
  const { notification, showSuccess, showError, showWarning, showInfo, hideNotification } = useNotification()

  // Function to determine which folder a document belongs to
  const getDocumentFolder = (filename: string): FolderType => {
    if (!filename) return folders.find(f => f.id === 'other') || folders[0]
    
    const ext = '.' + filename.split('.').pop()?.toLowerCase()
    
    for (const folder of folders) {
      if (folder.extensions.some(folderExt => folderExt === ext)) {
        return folder
      }
    }
    
    // Default to first folder if no match
    return folders[0]
  }

  // Function to search across all documents
  const searchAllDocuments = async (term: string) => {
    if (!term.trim()) {
      setSearchResults([])
      setIsSearching(false)
      return
    }

    setIsSearching(true)
    setLoading(true)

    try {
      // Fetch all documents from backend
      const response = await documentsApi.getDocuments()
      const allDocuments = response.documents

      // Filter documents based on search term and add folder information
      const filtered = allDocuments
        .filter(doc => 
          (doc.filename || '').toLowerCase().includes(term.toLowerCase()) ||
          (doc.document_type || '').toLowerCase().includes(term.toLowerCase()) ||
          (doc.ai_analysis?.document_type || '').toLowerCase().includes(term.toLowerCase()) ||
          ((doc.ai_analysis as any)?.classification?.document_type || '').toLowerCase().includes(term.toLowerCase())
        )
        .map(doc => {
          const folder = getDocumentFolder(doc.filename)
          return {
            ...doc,
            folder: {
              id: folder.id,
              name: folder.name,
              color: folder.color,
              icon: folder.icon
            }
          } as Document
        })

      setSearchResults(filtered)
    } catch (error) {
      console.error('Error searching documents:', error)
      showError('Failed to search documents')
      setSearchResults([])
    } finally {
      setLoading(false)
    }
  }

  // Debounced search effect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchAllDocuments(searchTerm)
    }, 300) // 300ms debounce

    return () => clearTimeout(timeoutId)
  }, [searchTerm])

  // Fetch document counts for each folder type
  useEffect(() => {
    const fetchDocumentCounts = async () => {
      try {
        setLoading(true)
        const response = await fetch('http://localhost:8007/api/v1/documents')
        if (response.ok) {
          const data = await response.json()
          const documents = data.documents || []
          
          // Count documents by type
          const updatedFolders = folders.map(folder => {
            let count = 0
            if (folder.id === 'pdf') {
              count = documents.filter((doc: any) => 
                doc.document_type?.toLowerCase() === 'pdf' || 
                doc.filename?.toLowerCase().endsWith('.pdf')
              ).length
            } else if (folder.id === 'docs') {
              count = documents.filter((doc: any) => 
                ['doc', 'docx', 'txt', 'rtf'].includes(doc.document_type?.toLowerCase()) ||
                ['.doc', '.docx', '.txt', '.rtf'].some(ext => 
                  doc.filename?.toLowerCase().endsWith(ext)
                )
              ).length
            } else if (folder.id === 'xls') {
              count = documents.filter((doc: any) => 
                ['xls', 'xlsx'].includes(doc.document_type?.toLowerCase()) ||
                ['.xls', '.xlsx'].some(ext => 
                  doc.filename?.toLowerCase().endsWith(ext)
                )
              ).length
            } else if (folder.id === 'csv') {
              count = documents.filter((doc: any) => 
                doc.document_type?.toLowerCase() === 'csv' ||
                doc.filename?.toLowerCase().endsWith('.csv')
              ).length
            } else if (folder.id === 'txt') {
              count = documents.filter((doc: any) => 
                ['txt', 'md', 'log'].includes(doc.document_type?.toLowerCase()) ||
                ['.txt', '.md', '.log'].some(ext => 
                  doc.filename?.toLowerCase().endsWith(ext)
                )
              ).length
            } else if (folder.id === 'json') {
              count = documents.filter((doc: any) => 
                doc.document_type?.toLowerCase() === 'json' ||
                doc.filename?.toLowerCase().endsWith('.json')
              ).length
            } else if (folder.id === 'image') {
              count = documents.filter((doc: any) => 
                ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'].includes(doc.document_type?.toLowerCase()) ||
                ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'].some(ext => 
                  doc.filename?.toLowerCase().endsWith(ext)
                )
              ).length
            }
            return { ...folder, count }
          })
          
          setFolders(updatedFolders)
        }
      } catch (error) {
        console.error('Error fetching document counts:', error)
        showError('Failed to load document counts')
      } finally {
        setLoading(false)
      }
    }

    fetchDocumentCounts()
  }, [])

  // Filter folders based on search (only when not searching documents)
  const filteredFolders = !isSearching ? folders.filter(folder =>
    folder.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    folder.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) : []

  const handleFolderClick = (folder: FolderType) => {
    // Navigate to folder view page
    router.push(`/documents/folders/${folder.id}`)
  }

  const handleBackToDocuments = () => {
    router.push('/documents')
  }

  const handleUploadDocument = () => {
    router.push('/documents/upload')
  }

  const handleDocumentClick = (document: Document) => {
    // Navigate to document details or folder view
    router.push(`/documents/folders/${document.folder?.id}`)
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

  return (
    <MainLayout>
      <Box sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
          <Box>
            <Typography variant="h4" gutterBottom fontWeight="bold">
              Document Folders
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Organize documents by type and format
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
              Click on a folder to view documents of that type
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button 
              variant="outlined" 
              startIcon={<ArrowBack />}
              onClick={handleBackToDocuments}
            >
              Back to Documents
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

        {/* Search Bar */}
        <Box sx={{ mb: 4 }}>
          <TextField
            fullWidth
            size="medium"
            variant="outlined"
            placeholder={isSearching ? "Search all documents..." : "Search folders or documents..."}
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
              maxWidth: '600px',
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                backgroundColor: 'white',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }
            }}
          />
          {isSearching && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Searching across all documents in all folders...
            </Typography>
          )}
        </Box>

        {/* Content Area - Show Search Results or Folders Grid */}
        {isSearching ? (
          <DocumentSearchResults
            documents={searchResults}
            searchTerm={searchTerm}
            onDocumentClick={handleDocumentClick}
          />
        ) : (
          <>
            {/* Folders Grid */}
            <Grid container spacing={3}>
              {filteredFolders.map((folder) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={folder.id}>
                  <Card
                sx={{
                  height: '200px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  border: '1px solid #e0e0e0',
                  borderRadius: '16px',
                  backgroundColor: 'white',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                    borderColor: folder.color
                  }
                }}
                onClick={() => handleFolderClick(folder)}
              >
                <CardContent sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  justifyContent: 'space-between',
                  p: 3
                }}>
                  {/* Folder Header */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Avatar 
                      sx={{ 
                        bgcolor: folder.color, 
                        width: 48, 
                        height: 48,
                        boxShadow: `0 4px 12px ${folder.color}40`
                      }}
                    >
                      {folder.icon}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" fontWeight="bold" color="text.primary">
                        {folder.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {folder.extensions.join(', ')}
                      </Typography>
                    </Box>
                  </Box>

                  {/* Folder Description */}
                  <Typography 
                    variant="body2" 
                    color="text.secondary" 
                    sx={{ 
                      mb: 2,
                      lineHeight: 1.4,
                      flexGrow: 1
                    }}
                  >
                    {folder.description}
                  </Typography>

                  {/* Folder Footer */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Chip
                      label={`${folder.count} documents`}
                      size="small"
                      sx={{
                        backgroundColor: `${folder.color}15`,
                        color: folder.color,
                        fontWeight: '600',
                        border: `1px solid ${folder.color}30`
                      }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      Click to view
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
          </>
        )}

        {/* Empty State - only show when not searching and no folders */}
        {!isSearching && filteredFolders.length === 0 && (
          <Box sx={{ 
            textAlign: 'center', 
            py: 8, 
            color: 'text.secondary' 
          }}>
            <Folder sx={{ fontSize: 64, mb: 2, color: 'text.disabled' }} />
            <Typography variant="h6" gutterBottom>
              No folders found
            </Typography>
            <Typography variant="body2">
              Try adjusting your search terms
            </Typography>
          </Box>
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
