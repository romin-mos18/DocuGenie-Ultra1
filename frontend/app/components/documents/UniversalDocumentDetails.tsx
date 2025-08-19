'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Description,
  CloudDownload,
  Delete,
  PlayArrow,
  CheckCircle,
  Error as ErrorIcon,
  AccessTime,
  ExpandMore,
  Psychology,
  AutoAwesome,
  Language,
  Insights,
  DataObject,
  SmartToy,
  Assessment,
  AttachMoney,
  Event,
  Receipt,
  AccountBalance,
} from '@mui/icons-material';
import DocumentTypeSpecificSections from './DocumentTypeSpecificSections';
import ErrorBoundary from '../common/ErrorBoundary';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';

// Safe accessor functions to prevent crashes
const safeGet = (obj: any, path: string, defaultValue: any = null) => {
  try {
    return path.split('.').reduce((current, prop) => current?.[prop], obj) ?? defaultValue;
  } catch {
    return defaultValue;
  }
};

const safeArray = (arr: any): any[] => {
  return Array.isArray(arr) ? arr : [];
};

const safeString = (value: any): string => {
  if (typeof value === 'string') return value;
  if (typeof value === 'number') return value.toString();
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value);
  }
  return '';
};

const safeNumber = (value: any): number => {
  const num = parseFloat(value);
  return isNaN(num) ? 0 : num;
};

// Document type configurations
const DOCUMENT_TYPE_CONFIG = {
  medical_report: { color: 'primary', icon: Description, label: 'Medical Report' },
  lab_result: { color: 'success', icon: Assessment, label: 'Lab Result' },
  financial_report: { color: 'warning', icon: AttachMoney, label: 'Financial Report' },
  bank_statement: { color: 'info', icon: AccountBalance, label: 'Bank Statement' },
  appointment: { color: 'secondary', icon: Event, label: 'Appointment' },
  patient_record: { color: 'primary', icon: Description, label: 'Patient Record' },
  insurance_claim: { color: 'warning', icon: Receipt, label: 'Insurance Claim' },
  prescription: { color: 'success', icon: Description, label: 'Prescription' },
  certificate: { color: 'info', icon: Description, label: 'Certificate' },
  contract: { color: 'error', icon: Description, label: 'Contract' },
  billing: { color: 'warning', icon: Receipt, label: 'Billing Document' },
  other: { color: 'default', icon: Description, label: 'Document' },
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index} style={{ padding: '20px 0' }}>
      {value === index && children}
    </div>
  );
}

interface UniversalDocumentDetailsProps {
  documentId: number;
  document?: any;
}

export default function UniversalDocumentDetails({ documentId, document: propDocument }: UniversalDocumentDetailsProps) {
  const [document, setDocument] = useState(propDocument);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const router = useRouter();

  // Fetch document if not provided
  useEffect(() => {
    if (!propDocument && documentId) {
      fetchDocument();
    }
  }, [documentId, propDocument]);

  const fetchDocument = async () => {
    try {
      const response = await fetch(`http://localhost:8007/api/v1/documents/${documentId}`);
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.document) {
          setDocument(result.document);
        } else {
          setError('Document not found');
        }
      } else {
        setError('Failed to fetch document');
      }
    } catch (err) {
      setError('Network error while fetching document');
      console.error('Fetch error:', err);
    }
  };

  // Safe document property accessors
  const documentType = safeGet(document, 'ai_analysis.classification.document_type', 'other');
  const confidence = safeNumber(safeGet(document, 'ai_analysis.classification.confidence', 0));
  const extractedText = safeString(safeGet(document, 'ai_analysis.text_preview', ''));
  const entities = safeGet(document, 'ai_analysis.extracted_entities_list', {});
  const entityCount = safeNumber(safeGet(document, 'ai_analysis.entity_count', 0));
  const wordCount = safeNumber(safeGet(document, 'ai_analysis.word_count', 0));
  const language = safeString(safeGet(document, 'ai_analysis.language.primary_language', 'EN'));
  const processingStatus = safeString(safeGet(document, 'status', 'unknown'));

  // Get document type configuration
  const typeConfig = DOCUMENT_TYPE_CONFIG[documentType as keyof typeof DOCUMENT_TYPE_CONFIG] || DOCUMENT_TYPE_CONFIG.other;
  const TypeIcon = typeConfig.icon;

  const handleProcess = async () => {
    try {
      setIsProcessing(true);
      setError(null);

      const response = await fetch(`http://localhost:8007/api/v1/documents/${documentId}/process`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('AI processing failed');
      }

      const result = await response.json();
      
      if (result.success) {
        await fetchDocument(); // Refresh document data
      }
    } catch (err) {
      console.error('AI processing error:', err);
      setError(err instanceof Error ? err.message : 'AI processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(`http://localhost:8007/api/v1/documents/${documentId}/download`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = window.document.createElement('a');
      a.href = url;
      a.download = safeString(safeGet(document, 'filename', 'document'));
      window.document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      window.document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download document:', error);
      setError('Failed to download document. Please try again.');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8007/documents/${documentId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        router.push('/documents');
      } else {
        setError('Failed to delete document. Please try again.');
      }
    } catch (error) {
      console.error('Failed to delete document:', error);
      setError('Error deleting document. Please try again.');
    }
  };

  const renderOverviewTab = () => (
    <ErrorBoundary>
      <Grid container spacing={3}>
      {/* Document Classification */}
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Psychology sx={{ mr: 1 }} />
              Document Classification
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Type:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Chip
                  icon={<TypeIcon />}
                  label={typeConfig.label}
                  size="small"
                  color={typeConfig.color as any}
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Confidence:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">
                  {(confidence * 100).toFixed(2)}%
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Document Statistics */}
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Insights sx={{ mr: 1 }} />
              Document Statistics
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Language:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{language}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Word Count:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{wordCount.toLocaleString()}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Entities Found:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{entityCount}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Document Summary */}
      <Grid item xs={12}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Document Summary
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body1">
              {extractedText.slice(0, 500)}
              {extractedText.length > 500 && '...'}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
    </ErrorBoundary>
  );

  const renderTestResultsTab = () => {
    return (
      <ErrorBoundary>
        <DocumentTypeSpecificSections 
          document={document} 
          documentType={documentType} 
        />
      </ErrorBoundary>
    );
  };

  const renderEntitiesTab = () => (
    <ErrorBoundary>
      <Grid container spacing={3}>
        {Object.entries(entities).map(([entityType, entityList]) => {
          const entityArray = safeArray(entityList);
          if (entityArray.length === 0) return null;

          return (
            <Grid item xs={12} md={6} key={entityType}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {entityType.replace('_', ' ').toUpperCase()}
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {entityArray.slice(0, 10).map((entity: any, index: number) => (
                      <Chip
                        key={index}
                        label={safeString(entity)}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                    {entityArray.length > 10 && (
                      <Chip
                        label={`+${entityArray.length - 10} more`}
                        size="small"
                        variant="outlined"
                        color="secondary"
                      />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </ErrorBoundary>
  );

  const renderContentTab = () => (
    <ErrorBoundary>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Extracted Content
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Typography 
            variant="body2" 
            component="pre" 
            sx={{ 
              whiteSpace: 'pre-wrap', 
              maxHeight: 400, 
              overflow: 'auto',
              backgroundColor: 'grey.50',
              p: 2,
              borderRadius: 1
            }}
          >
            {extractedText || 'No text content extracted'}
          </Typography>
        </CardContent>
      </Card>
    </ErrorBoundary>
  );

  const renderQualityTab = () => (
    <ErrorBoundary>
      <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Processing Quality
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Classification Confidence:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{(confidence * 100).toFixed(2)}%</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Processing Status:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Chip
                  label={processingStatus}
                  size="small"
                  color={processingStatus === 'processed' ? 'success' : 'default'}
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Text Quality:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">
                  {wordCount > 0 ? 'Good' : 'No text extracted'}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
    </ErrorBoundary>
  );

  if (!document) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1400, mx: 'auto', p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h5" gutterBottom>
              {safeString(safeGet(document, 'filename', 'Untitled Document'))}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                icon={<TypeIcon />}
                label={typeConfig.label}
                size="small"
                color={typeConfig.color as any}
              />
              <Chip
                label={`Confidence: ${(confidence * 100).toFixed(2)}%`}
                size="small"
                variant="outlined"
              />
              <Chip
                label={`${entityCount} entities`}
                size="small"
                variant="outlined"
              />
            </Box>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'right' }}>
            <Button
              variant="contained"
              startIcon={<PlayArrow />}
              onClick={handleProcess}
              disabled={isProcessing}
              sx={{ mr: 1 }}
            >
              {isProcessing ? <CircularProgress size={20} /> : 'Reprocess'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<CloudDownload />}
              onClick={handleDownload}
              sx={{ mr: 1 }}
            >
              Download
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={handleDelete}
            >
              Delete
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs */}
      <Paper sx={{ p: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Overview" />
          <Tab label="Document Details" />
          <Tab label="Entities" />
          <Tab label="Content" />
          <Tab label="Quality" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {renderOverviewTab()}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {renderTestResultsTab()}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {renderEntitiesTab()}
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {renderContentTab()}
        </TabPanel>

        <TabPanel value={tabValue} index={4}>
          {renderQualityTab()}
        </TabPanel>
      </Paper>
    </Box>
  );
}
