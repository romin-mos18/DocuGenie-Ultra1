'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Avatar,
  Button,
  IconButton,
  Tooltip,
  Divider
} from '@mui/material'
import {
  Description,
  TableChart,
  TextSnippet,
  DataObject,
  Image,
  Visibility,
  Download,
  Folder,
  AccessTime,
  Storage
} from '@mui/icons-material'

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
  }
  folder?: {
    id: string
    name: string
    color: string
    icon: React.ReactNode
  }
}

interface DocumentSearchResultsProps {
  documents: Document[]
  searchTerm: string
  onDocumentClick: (document: Document) => void
}

export default function DocumentSearchResults({ 
  documents, 
  searchTerm, 
  onDocumentClick 
}: DocumentSearchResultsProps) {
  const router = useRouter()

  const getFileIcon = (filename: string, color: string = '#666') => {
    if (!filename) return <Description sx={{ color }} />
    
    const ext = filename.split('.').pop()?.toLowerCase()
    if (['pdf'].includes(ext || '')) return <Description sx={{ color }} />
    if (['doc', 'docx', 'txt', 'rtf', 'md'].includes(ext || '')) return <TextSnippet sx={{ color }} />
    if (['xls', 'xlsx', 'csv'].includes(ext || '')) return <TableChart sx={{ color }} />
    if (['json', 'xml'].includes(ext || '')) return <DataObject sx={{ color }} />
    if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'].includes(ext || '')) return <Image sx={{ color }} />
    return <Description sx={{ color }} />
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Unknown'
    }
  }

  const highlightSearchTerm = (text: string, searchTerm: string) => {
    if (!searchTerm.trim()) return text
    
    const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
    const parts = text.split(regex)
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <span key={index} style={{ backgroundColor: '#ffeb3b', fontWeight: 'bold' }}>
          {part}
        </span>
      ) : part
    )
  }

  const handleViewInFolder = (document: Document) => {
    if (document.folder) {
      router.push(`/documents/folders/${document.folder.id}`)
    }
  }

  if (documents.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No documents found
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Try adjusting your search terms or browse folders directly
        </Typography>
      </Box>
    )
  }

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="h6" color="text.primary">
          Search Results
        </Typography>
        <Chip 
          label={`${documents.length} document${documents.length !== 1 ? 's' : ''} found`}
          size="small"
          variant="outlined"
        />
      </Box>

      <Grid container spacing={2}>
        {documents.map((document) => (
          <Grid item xs={12} key={document.id}>
            <Card 
              variant="outlined" 
              sx={{ 
                cursor: 'pointer',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  boxShadow: 2,
                  transform: 'translateY(-1px)'
                }
              }}
              onClick={() => onDocumentClick(document)}
            >
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                  {/* Document Icon */}
                  <Avatar
                    sx={{
                      bgcolor: document.folder?.color || '#666',
                      width: 48,
                      height: 48,
                      mt: 0.5
                    }}
                  >
                    {getFileIcon(document.filename, '#fff')}
                  </Avatar>

                  {/* Document Info */}
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    {/* Filename with highlighting */}
                    <Typography 
                      variant="subtitle1" 
                      sx={{ 
                        fontWeight: 600,
                        mb: 0.5,
                        wordBreak: 'break-word'
                      }}
                    >
                      {highlightSearchTerm(document.filename, searchTerm)}
                    </Typography>

                    {/* Folder Information */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Folder sx={{ fontSize: 16, color: document.folder?.color || '#666' }} />
                      <Typography variant="body2" color="text.secondary">
                        in
                      </Typography>
                      <Chip
                        label={document.folder?.name || 'Unknown Folder'}
                        size="small"
                        sx={{
                          bgcolor: `${document.folder?.color || '#666'}15`,
                          color: document.folder?.color || '#666',
                          fontWeight: 500,
                          '&:hover': {
                            bgcolor: `${document.folder?.color || '#666'}25`,
                            cursor: 'pointer'
                          }
                        }}
                        onClick={(e) => {
                          e.stopPropagation()
                          handleViewInFolder(document)
                        }}
                      />
                    </Box>

                    {/* Document Metadata */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Storage sx={{ fontSize: 14, color: 'text.secondary' }} />
                        <Typography variant="caption" color="text.secondary">
                          {formatFileSize(document.file_size)}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <AccessTime sx={{ fontSize: 14, color: 'text.secondary' }} />
                        <Typography variant="caption" color="text.secondary">
                          {formatDate(document.upload_date)}
                        </Typography>
                      </Box>

                      {(document.ai_analysis?.document_type || document.ai_analysis?.classification?.document_type) && (
                        <Chip
                          label={(document.ai_analysis.document_type || document.ai_analysis.classification?.document_type || '').replace('_', ' ').toUpperCase()}
                          size="small"
                          variant="outlined"
                          sx={{ height: 20, fontSize: '0.6rem' }}
                        />
                      )}

                      {document.ai_analysis?.entity_count && (
                        <Typography variant="caption" color="text.secondary">
                          {document.ai_analysis.entity_count} entities
                        </Typography>
                      )}
                    </Box>
                  </Box>

                  {/* Action Buttons */}
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Tooltip title="View Document">
                      <IconButton 
                        size="small" 
                        onClick={(e) => {
                          e.stopPropagation()
                          onDocumentClick(document)
                        }}
                      >
                        <Visibility fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    
                    <Tooltip title="View in Folder">
                      <IconButton 
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleViewInFolder(document)
                        }}
                      >
                        <Folder fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Back to Folders Button */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Button
          variant="outlined"
          onClick={() => router.push('/documents/folders')}
          startIcon={<Folder />}
        >
          Browse All Folders
        </Button>
      </Box>
    </Box>
  )
}
