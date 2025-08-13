'use client'

import React, { useState } from 'react'
import MainLayout from '../components/layout/MainLayout'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Button,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  Divider
} from '@mui/material'
import {
  Psychology,
  Visibility,
  Category,
  Analytics,
  TrendingUp,
  CheckCircle,
  Schedule,
  Error
} from '@mui/icons-material'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`ai-tabpanel-${index}`}
      aria-labelledby={`ai-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  )
}

export default function AIFeaturesPage() {
  const [tabValue, setTabValue] = useState(0)

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  // Enhanced AI processing data from requirements
  const ocrStats = {
    accuracy: 96.8,
    totalProcessed: 2847,
    avgProcessingTime: 3.2,
    engines: [
      { name: 'PaddleOCR', accuracy: 96.8, usage: 65, description: 'Primary OCR engine for high accuracy' },
      { name: 'TrOCR', accuracy: 94.2, usage: 25, description: 'Handwriting recognition specialist' },
      { name: 'Tesseract', accuracy: 91.5, usage: 10, description: 'Fallback engine for legacy documents' }
    ]
  }

  const classificationStats = {
    accuracy: 93.2,
    totalClassified: 2842,
    totalTypes: 2000, // As per requirements: 2000+ document types
    categories: [
      { name: 'Clinical Trial Protocol', count: 1200, accuracy: 95.4 },
      { name: 'Lab Report', count: 850, accuracy: 92.1 },
      { name: 'Medical Record', count: 450, accuracy: 91.8 },
      { name: 'Informed Consent Form', count: 200, accuracy: 96.7 },
      { name: 'Prescription', count: 142, accuracy: 89.3 },
      { name: 'Radiology Report', count: 180, accuracy: 94.8 },
      { name: 'Pathology Report', count: 95, accuracy: 93.5 },
      { name: 'Regulatory Submission', count: 65, accuracy: 97.2 }
    ]
  }

  const recentProcessing = [
    {
      id: 1,
      fileName: 'Clinical_Trial_Protocol.pdf',
      ocrAccuracy: 98.5,
      classification: 'Clinical Trial',
      classificationConfidence: 97.2,
      entitiesFound: 24,
      processingTime: 2.8,
      status: 'completed'
    },
    {
      id: 2,
      fileName: 'Lab_Report_001.pdf',
      ocrAccuracy: 95.1,
      classification: 'Lab Report',
      classificationConfidence: 94.8,
      entitiesFound: 18,
      processingTime: 3.1,
      status: 'completed'
    },
    {
      id: 3,
      fileName: 'Patient_Record.jpg',
      ocrAccuracy: null,
      classification: null,
      classificationConfidence: null,
      entitiesFound: null,
      processingTime: null,
      status: 'processing'
    }
  ]

  return (
    <MainLayout>
      <Box sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            AI Features & Analytics
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Monitor AI processing performance and capabilities
          </Typography>
        </Box>

        {/* Overview Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: '#1976d2', mr: 2 }}>
                    <Visibility />
                  </Avatar>
                  <Typography variant="h6">OCR Accuracy</Typography>
                </Box>
                <Typography variant="h3" fontWeight="bold" color="primary">
                  {ocrStats.accuracy}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Optical Character Recognition
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: '#388e3c', mr: 2 }}>
                    <Category />
                  </Avatar>
                  <Typography variant="h6">Classification</Typography>
                </Box>
                <Typography variant="h3" fontWeight="bold" color="success.main">
                  {classificationStats.accuracy}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Document categorization
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: '#f57c00', mr: 2 }}>
                    <Analytics />
                  </Avatar>
                  <Typography variant="h6">Entity Extraction</Typography>
                </Box>
                <Typography variant="h3" fontWeight="bold" color="warning.main">
                  91.5%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Medical entity recognition
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: '#7b1fa2', mr: 2 }}>
                    <TrendingUp />
                  </Avatar>
                  <Typography variant="h6">Avg Processing</Typography>
                </Box>
                <Typography variant="h3" fontWeight="bold" color="secondary">
                  {ocrStats.avgProcessingTime}s
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Per document
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Detailed Analytics */}
        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="OCR Performance" />
              <Tab label="Classification" />
              <Tab label="Entity Extraction" />
              <Tab label="Recent Processing" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  OCR Engine Performance
                </Typography>
                {ocrStats.engines.map((engine) => (
                  <Box key={engine.name} sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">{engine.name}</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {engine.accuracy}% accuracy
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={engine.accuracy} 
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {engine.usage}% usage rate
                    </Typography>
                  </Box>
                ))}
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Processing Statistics
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Total Documents Processed
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {ocrStats.totalProcessed.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Average Processing Time
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {ocrStats.avgProcessingTime}s
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Typography variant="h6" gutterBottom>
              Document Classification Performance
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Document Type</TableCell>
                    <TableCell align="right">Documents Classified</TableCell>
                    <TableCell align="right">Accuracy</TableCell>
                    <TableCell align="right">Performance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {classificationStats.categories.map((category) => (
                    <TableRow key={category.name}>
                      <TableCell>{category.name}</TableCell>
                      <TableCell align="right">{category.count.toLocaleString()}</TableCell>
                      <TableCell align="right">{category.accuracy}%</TableCell>
                      <TableCell align="right">
                        <LinearProgress
                          variant="determinate"
                          value={category.accuracy}
                          sx={{ width: 100 }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6" gutterBottom>
              Medical Entity Extraction
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Entity Types Supported
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {['Patient Names', 'Provider Names', 'Medications', 'Conditions', 'Procedures', 'Dates', 'Lab Values', 'Dosages'].map((entity) => (
                    <Chip key={entity} label={entity} variant="outlined" />
                  ))}
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Extraction Statistics
                </Typography>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Average Entities per Document: <strong>22.4</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Extraction Accuracy: <strong>91.5%</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Entities Extracted: <strong>63,728</strong>
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Typography variant="h6" gutterBottom>
              Recent AI Processing Results
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>File Name</TableCell>
                    <TableCell>OCR Accuracy</TableCell>
                    <TableCell>Classification</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Entities</TableCell>
                    <TableCell>Time (s)</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentProcessing.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                            <Psychology />
                          </Avatar>
                          {item.fileName}
                        </Box>
                      </TableCell>
                      <TableCell>
                        {item.ocrAccuracy ? `${item.ocrAccuracy}%` : 'Processing...'}
                      </TableCell>
                      <TableCell>
                        {item.classification ? (
                          <Chip label={item.classification} size="small" />
                        ) : (
                          'Processing...'
                        )}
                      </TableCell>
                      <TableCell>
                        {item.classificationConfidence ? `${item.classificationConfidence}%` : 'N/A'}
                      </TableCell>
                      <TableCell>
                        {item.entitiesFound || 'Processing...'}
                      </TableCell>
                      <TableCell>
                        {item.processingTime || 'Processing...'}
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={item.status === 'completed' ? <CheckCircle /> : <Schedule />}
                          label={item.status.toUpperCase()}
                          color={item.status === 'completed' ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
        </Paper>
      </Box>
    </MainLayout>
  )
}
