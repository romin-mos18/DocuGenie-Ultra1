'use client';

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Divider,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  LocalHospital,
  AttachMoney,
  AccountBalance,
  Event,
  Assignment,
  Receipt,
  Gavel,
  School,
  Person,
  TrendingUp,
  TrendingDown,
  Schedule,
  Phone,
  Email,
} from '@mui/icons-material';
import { safeGet, safeArray, safeStringValue, safeNumberValue, formatConfidence, formatFileSize } from '../../../utils/safeguards';
import { EmptyState, LoadingSkeleton } from '../common/FallbackContent';

interface DocumentTypeSpecificSectionsProps {
  document: any;
  documentType: string;
}

export const MedicalDocumentSection: React.FC<{ document: any }> = ({ document }) => {
  // Extract data from multiple sources with fallbacks
  const entities = safeGet(document, 'ai_analysis.extracted_entities_list', {}) || safeGet(document, 'ai_analysis.entities.entities', {});
  const structuredKeyInfo = safeGet(document, 'ai_analysis.structured_data.structured_data.key_info', {});
  
  // Patient Information - try multiple sources
  const patientName = safeStringValue(
    structuredKeyInfo.patient_name || 
    (safeArray(entities.names).find(name => !name.toLowerCase().includes('hospital') && !name.toLowerCase().includes('center')) || ''),
    '-'
  );
  
  const mrn = safeStringValue(
    structuredKeyInfo.medical_record_number || 
    structuredKeyInfo.patient_id ||
    (safeArray(entities.identifiers).find(id => id.length >= 5) || ''),
    '-'
  );
  
  const dob = safeStringValue(
    structuredKeyInfo.date_of_birth || 
    structuredKeyInfo.dob ||
    (safeArray(entities.dates)[0] || ''),
    '-'
  );
  
  const diagnosis = safeStringValue(
    structuredKeyInfo.diagnosis || 
    (safeArray(entities.medical_terms).find(term => term.toLowerCase().includes('diagnosis') || term.toLowerCase().includes('condition')) || ''),
    '-'
  );
  
  const provider = safeStringValue(
    structuredKeyInfo.provider || 
    structuredKeyInfo.physician ||
    structuredKeyInfo.doctor ||
    (safeArray(entities.names).find(name => name.toLowerCase().includes('dr.') || name.toLowerCase().includes('doctor')) || ''),
    '-'
  );
  
  const reportDate = safeStringValue(
    structuredKeyInfo.report_date || 
    structuredKeyInfo.date ||
    (safeArray(entities.dates)[1] || safeArray(entities.dates)[0] || ''),
    '-'
  );
  
  const testResults = safeArray(safeGet(document, 'ai_analysis.test_results', []));

  return (
    <Grid container spacing={3}>
      {/* Patient Information */}
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Person sx={{ mr: 1 }} />
              Patient Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Patient Name:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{patientName}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">MRN:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{mrn}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">DOB:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{dob}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Diagnosis:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{diagnosis}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Report Information */}
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Assignment sx={{ mr: 1 }} />
              Report Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Provider:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{provider}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Report Date:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{reportDate}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Medical Entities */}
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <LocalHospital sx={{ mr: 1 }} />
              Medical Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            {renderEntitySection(document, 'medical_terms', 'Medical Terms')}
          </CardContent>
        </Card>
      </Grid>

      {/* Test Results */}
      <Grid item xs={12}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Laboratory Test Results
            </Typography>
            <Divider sx={{ my: 2 }} />
            {testResults.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Test Name</TableCell>
                      <TableCell>Value</TableCell>
                      <TableCell>Unit</TableCell>
                      <TableCell>Reference Range</TableCell>
                      <TableCell>Flag</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {testResults.map((test: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>{safeStringValue(test.name, '-')}</TableCell>
                        <TableCell>{safeStringValue(test.value, '-')}</TableCell>
                        <TableCell>{safeStringValue(test.unit, '-')}</TableCell>
                        <TableCell>{safeStringValue(test.reference, '-')}</TableCell>
                        <TableCell>
                          <Chip
                            label={safeStringValue(test.flag) || 'Normal'}
                            size="small"
                            color={test.flag === 'High' || test.flag === 'Low' ? 'warning' : 'success'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', py: 2 }}>
                No test results available
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export const FinancialDocumentSection: React.FC<{ document: any }> = ({ document }) => {
  // Extract data from multiple sources
  const entities = safeGet(document, 'ai_analysis.extracted_entities_list', {}) || safeGet(document, 'ai_analysis.entities.entities', {});
  const structuredData = safeGet(document, 'ai_analysis.structured_data.structured_data', {});
  const keyInfo = safeGet(structuredData, 'key_info', {});
  const headers = safeArray(structuredData.headers);
  const rows = safeArray(structuredData.rows).slice(0, 10); // Show first 10 rows
  const metrics = safeGet(structuredData, 'metrics', {});
  
  // Financial Information
  const accountNumber = safeStringValue(
    keyInfo.account_number || keyInfo.account_id || 
    (safeArray(entities.identifiers).find(id => id.length >= 8) || ''),
    '-'
  );
  
  const statementDate = safeStringValue(
    keyInfo.statement_date || keyInfo.report_date || keyInfo.date ||
    (safeArray(entities.dates)[0] || ''),
    '-'
  );
  
  const totalAmount = safeStringValue(
    keyInfo.total_amount || keyInfo.balance || keyInfo.total ||
    (safeArray(entities.amounts)[0] || ''),
    '-'
  );
  
  const institution = safeStringValue(
    keyInfo.institution || keyInfo.bank_name || keyInfo.company ||
    (safeArray(entities.organizations)[0] || ''),
    '-'
  );

  return (
    <Grid container spacing={3}>
      {/* Financial Information */}
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <AccountBalance sx={{ mr: 1 }} />
              Financial Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Institution:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{institution}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Account Number:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{accountNumber}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Statement Date:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{statementDate}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Total Amount:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{totalAmount}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Financial Metrics */}
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <TrendingUp sx={{ mr: 1 }} />
              Financial Metrics
            </Typography>
            <Divider sx={{ my: 2 }} />
            {Object.keys(metrics).length > 0 ? (
              <Grid container spacing={2}>
                {Object.entries(metrics).map(([key, value]) => (
                  <React.Fragment key={key}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">
                        {typeof value === 'number' ? value.toLocaleString() : safeStringValue(value)}
                      </Typography>
                    </Grid>
                  </React.Fragment>
                ))}
              </Grid>
            ) : (
              <Typography variant="body2" color="textSecondary">
                No financial metrics calculated
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Financial Entities */}
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <AttachMoney sx={{ mr: 1 }} />
              Financial Entities
            </Typography>
            <Divider sx={{ my: 2 }} />
            {renderEntitySection(document, 'financial_terms', 'Financial Terms')}
            {renderEntitySection(document, 'amounts', 'Amounts')}
          </CardContent>
        </Card>
      </Grid>

      {/* Data Preview */}
      {headers.length > 0 && rows.length > 0 && (
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Data Preview ({rows.length} of {structuredData.total_rows || rows.length} rows)
              </Typography>
              <Divider sx={{ my: 2 }} />
              <TableContainer sx={{ maxHeight: 400 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {headers.map((header: string, index: number) => (
                        <TableCell key={index}>{header}</TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {rows.map((row: any, index: number) => (
                      <TableRow key={index}>
                        {headers.map((header: string, cellIndex: number) => (
                          <TableCell key={cellIndex}>
                            {safeStringValue(row[header])}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
};

export const AppointmentDocumentSection: React.FC<{ document: any }> = ({ document }) => {
  // Extract data from multiple sources
  const entities = safeGet(document, 'ai_analysis.extracted_entities_list', {}) || safeGet(document, 'ai_analysis.entities.entities', {});
  const keyInfo = safeGet(document, 'ai_analysis.structured_data.structured_data.key_info', {});
  
  // Appointment Information
  const appointmentId = safeStringValue(
    keyInfo.appointment_id || keyInfo.appointment_number ||
    (safeArray(entities.identifiers).find(id => id.includes('APPT') || id.length >= 6) || ''),
    '-'
  );
  
  const patientName = safeStringValue(
    keyInfo.patient_name ||
    (safeArray(entities.names).find(name => !name.toLowerCase().includes('dr.') && !name.toLowerCase().includes('hospital')) || ''),
    '-'
  );
  
  const appointmentDate = safeStringValue(
    keyInfo.appointment_date || keyInfo.date ||
    (safeArray(entities.dates)[0] || ''),
    '-'
  );
  
  const appointmentTime = safeStringValue(
    keyInfo.appointment_time || keyInfo.time || '',
    '-'
  );
  
  const provider = safeStringValue(
    keyInfo.provider || keyInfo.doctor || keyInfo.physician ||
    (safeArray(entities.names).find(name => name.toLowerCase().includes('dr.')) || ''),
    '-'
  );
  
  const appointmentType = safeStringValue(
    keyInfo.appointment_type || keyInfo.type || '',
    '-'
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Event sx={{ mr: 1 }} />
              Appointment Details
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Appointment ID:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{appointmentId}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Patient:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{patientName}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Date:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{appointmentDate}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Time:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{appointmentTime}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Provider:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{provider}</Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Type:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{appointmentType}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Schedule sx={{ mr: 1 }} />
              Contact Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            {renderEntitySection(document, 'emails', 'Email Addresses')}
            {renderEntitySection(document, 'phone_numbers', 'Phone Numbers')}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export const LegalDocumentSection: React.FC<{ document: any }> = ({ document }) => {
  const keyInfo = safeGet(document, 'ai_analysis.structured_data.key_info', {});

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Gavel sx={{ mr: 1 }} />
              Document Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              {Object.entries(keyInfo)
                .filter(([key, value]) => value)
                .map(([key, value]) => (
                  <React.Fragment key={key}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">{safeStringValue(value)}</Typography>
                    </Grid>
                  </React.Fragment>
                ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Person sx={{ mr: 1 }} />
              Extracted Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            {renderEntitySection(document, 'names', 'Names')}
            {renderEntitySection(document, 'organizations', 'Organizations')}
            {renderEntitySection(document, 'dates', 'Important Dates')}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export const CertificateDocumentSection: React.FC<{ document: any }> = ({ document }) => {
  const keyInfo = safeGet(document, 'ai_analysis.structured_data.key_info', {});
  const recipientName = safeStringValue(keyInfo.recipient_name);
  const certificateNumber = safeStringValue(keyInfo.certificate_number);
  const issueDate = safeStringValue(keyInfo.issue_date);

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <School sx={{ mr: 1 }} />
              Certificate Details
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              {recipientName && (
                <>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Recipient:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">{recipientName}</Typography>
                  </Grid>
                </>
              )}
              {certificateNumber && (
                <>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Certificate Number:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">{certificateNumber}</Typography>
                  </Grid>
                </>
              )}
              {issueDate && (
                <>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Issue Date:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">{issueDate}</Typography>
                  </Grid>
                </>
              )}
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Assignment sx={{ mr: 1 }} />
              Additional Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            {renderEntitySection(document, 'organizations', 'Issuing Organizations')}
            {renderEntitySection(document, 'dates', 'Important Dates')}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// Helper function to render entity sections
const renderEntitySection = (document: any, entityType: string, label: string) => {
  const entities = safeArray(safeGet(document, `ai_analysis.extracted_entities_list.${entityType}`, []));
  
  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        {label}:
      </Typography>
      {entities.length > 0 ? (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {entities.slice(0, 5).map((entity: any, index: number) => (
            <Chip
              key={index}
              label={safeStringValue(entity)}
              size="small"
              variant="outlined"
            />
          ))}
          {entities.length > 5 && (
            <Chip
              label={`+${entities.length - 5} more`}
              size="small"
              variant="outlined"
              color="secondary"
            />
          )}
        </Box>
      ) : (
        <Typography variant="body2" color="textSecondary">
          -
        </Typography>
      )}
    </Box>
  );
};

// Main component that renders the appropriate section based on document type
const DocumentTypeSpecificSections: React.FC<DocumentTypeSpecificSectionsProps> = ({ 
  document, 
  documentType 
}) => {
  // Medical document types
  if (['medical_report', 'lab_result', 'patient_record', 'prescription'].includes(documentType)) {
    return <MedicalDocumentSection document={document} />;
  }

  // Financial document types
  if (['financial_report', 'bank_statement', 'billing'].includes(documentType)) {
    return <FinancialDocumentSection document={document} />;
  }

  // Appointment
  if (documentType === 'appointment') {
    return <AppointmentDocumentSection document={document} />;
  }

  // Legal documents
  if (['contract', 'legal_document', 'insurance_claim', 'insurance'].includes(documentType)) {
    return <LegalDocumentSection document={document} />;
  }

  // Certificate
  if (documentType === 'certificate') {
    return <CertificateDocumentSection document={document} />;
  }

  // Default fallback - show enhanced info for all other document types
  const entityCount = safeStringValue(safeGet(document, 'ai_analysis.entity_count', 0));
  const wordCount = safeStringValue(safeGet(document, 'ai_analysis.word_count', 0));
  const hasStructuredData = safeGet(document, 'ai_analysis.has_structured_data', false);
  const dataType = safeStringValue(safeGet(document, 'ai_analysis.data_type', ''));
  const language = safeStringValue(safeGet(document, 'ai_analysis.language.primary_language', 'EN'));
  const confidence = safeNumberValue(safeGet(document, 'ai_analysis.classification.confidence', 0));

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Document Analysis Summary
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Document Type:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Chip 
                  label={documentType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} 
                  size="small" 
                  color="primary"
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">AI Confidence:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{(confidence * 100).toFixed(2)}%</Typography>
              </Grid>
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
                <Typography variant="body2">{wordCount}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Entities Found:</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2">{entityCount}</Typography>
              </Grid>
              {hasStructuredData && (
                <>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Data Format:</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Chip 
                      label={dataType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} 
                      size="small" 
                      color="secondary"
                    />
                  </Grid>
                </>
              )}
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Processing Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
              This document has been successfully processed using our AI pipeline. 
              {hasStructuredData && ` Structured data extraction was performed on this ${dataType.replace(/_/g, ' ')} file.`}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Content analysis extracted {entityCount} entities across multiple categories, 
              providing rich metadata for search and organization.
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Show entities if available */}
      {parseInt(entityCount) > 0 && (
        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Extracted Entities
              </Typography>
              <Divider sx={{ my: 2 }} />
              {renderEntitySection(document, 'names', 'Names')}
              {renderEntitySection(document, 'dates', 'Dates')}
              {renderEntitySection(document, 'organizations', 'Organizations')}
              {renderEntitySection(document, 'amounts', 'Amounts')}
              {renderEntitySection(document, 'identifiers', 'Identifiers')}
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
};

export default DocumentTypeSpecificSections;
