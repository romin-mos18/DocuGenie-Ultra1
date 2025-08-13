'use client'

import React from 'react'
import MainLayout from '../../components/layout/MainLayout'
import DocumentUpload from '../../components/documents/DocumentUpload'
import {
  Box,
  Typography
} from '@mui/material'

export default function UploadPage() {
  return (
    <MainLayout>
      <Box sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Upload Documents
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Upload your healthcare documents for AI-powered processing
          </Typography>
        </Box>

        {/* Upload Component - Full Width */}
        <DocumentUpload />
      </Box>
    </MainLayout>
  )
}