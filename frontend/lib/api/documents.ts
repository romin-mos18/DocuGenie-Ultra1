// Documents API - Updated to use AI-powered document processing
import axios from './axios';

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  status: string;
  upload_date: string;
  processed_date?: string;
  file_size: number;
  document_type: string;
  documentType: string;
  confidence: number;
  ai_analysis: {
    success?: boolean;
    classification?: {
      document_type: string;
      confidence: number;
      success: boolean;
      text_length?: number;
      cleaned_text?: string;
    };
    entities?: {
      success: boolean;
      entities: {
        dates?: string[];
        names?: string[];
        organizations?: string[];
        locations?: string[];
        medical_terms?: string[];
        financial_terms?: string[];
        numbers?: string[];
        amounts?: string[];
        identifiers?: string[];
        emails?: string[];
        phone_numbers?: string[];
        addresses?: string[];
      };
      entity_count: number;
      text_length?: number;
    };
    language?: {
      primary_language: string;
      confidence: number;
      detected_languages?: string[];
    };
    structured_data?: {
      success: boolean;
      data_type: string;
      structured_data: {
        headers?: string[];
        rows?: Record<string, any>[];
        total_rows?: number;
        metrics?: Record<string, any>;
        key_info?: Record<string, any>;
        data?: any;
        structure?: any;
      };
      row_count?: number;
      column_count?: number;
    };
    processing_timestamp: string;
    text_preview: string;
    word_count: number;
    entity_count: number;
    extracted_entities_list: Record<string, any[]>;
    processing_method: string;
    has_structured_data?: boolean;
    data_type?: string;
    test_results?: Array<{
      name: string;
      value: string;
      unit: string;
      reference: string;
      flag: string;
    }>;
  };
  classification?: {
    document_type: string;
    confidence: number;
    success: boolean;
    reasoning?: string[];
    alternatives?: Array<{
      type: string;
      confidence: number;
      reasoning: string[];
    }>;
  };
  key_information?: Record<string, any>;
  processing_stats?: Record<string, any>;
  ai_summary?: string;
  extractedEntities?: Record<string, any[]>;
  documentMetadata?: {
    ai_processing_time?: number;
    word_count?: number;
  };
  classificationConfidence?: number;
  entitiesFound?: number;
  language?: string | { primary_language: string; confidence: number };
}

export interface DocumentUploadResponse {
  success: boolean;
  message: string;
  document_id: number;
  filename: string;
  file_type: string;
  file_size: number;
  processing_status: string;
  document_type: string;
  documentType: string;
  confidence: number;
  ai_analysis: {
    success: boolean;
    document_type: string;
    confidence: number;
    summary: string;
    processing_method: string;
    extraction_successful: boolean;
    analysis_successful: boolean;
  };
  classification: {
    document_type: string;
    confidence: number;
    success: boolean;
  };
}

// Documents API functions - using AI-powered processing
export const documentsApi = {
  // Upload document with AI processing
  uploadDocument: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Use compatibility endpoint that routes to AI processing
    const response = await axios.post('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minute timeout for AI processing
    });
    
    return response.data;
  },

  // Get all AI-processed documents
  getDocuments: async (): Promise<{ documents: Document[]; total: number }> => {
    // Use compatibility endpoint that routes to AI processing
    const response = await axios.get('/api/v1/documents');
    return response.data;
  },

  // Get document details with AI analysis
  getDocumentDetails: async (documentId: string): Promise<{
    success: boolean;
    document: Document;
    ai_analysis: any;
    extracted_text: string;
    ai_summary: string;
  }> => {
    const response = await axios.get(`/api/v1/documents/${documentId}`);
    return response.data;
  },

  // Delete document
  deleteDocument: async (documentId: string): Promise<{
    success: boolean;
    message: string;
    document_id: string;
    deleted_at: string;
  }> => {
    const response = await axios.delete(`/api/v1/documents/${documentId}`);
    return response.data;
  },

  // Get AI processing statistics
  getAIStats: async (): Promise<any> => {
    const response = await axios.get('/api/ai/status');
    return response.data;
  }
};

// Helper function for document type labeling - CONTENT-BASED ONLY
export const getDocumentTypeLabel = (document: any): string => {
  // Priority 1: Use AI classification from content analysis
  const aiDocType = document.ai_analysis?.document_type || 
                   document.ai_analysis?.classification?.document_type ||
                   document.document_type;
  
  if (aiDocType && aiDocType !== 'unknown' && aiDocType !== 'other') {
    console.log(`🤖 Using AI content classification: ${aiDocType} for ${document.filename}`);
    return formatDocumentType(aiDocType);
  }
  
  // Priority 2: Check classification object
  if (document.classification?.document_type && 
      document.classification.document_type !== 'unknown' && 
      document.classification.document_type !== 'other') {
    console.log(`🤖 Using classification object: ${document.classification.document_type} for ${document.filename}`);
    return formatDocumentType(document.classification.document_type);
  }
  
  // Priority 3: Check documentType field
  if (document.documentType && 
      document.documentType !== 'Unknown' && 
      document.documentType !== 'Document - Needs AI Analysis') {
    console.log(`📋 Using documentType field: ${document.documentType} for ${document.filename}`);
    return document.documentType;
  }
  
  // Log when no AI classification is available
  console.warn(`⚠️ No AI classification available for ${document.filename}`);
  console.log('Document object:', document);
  
  return 'Document - Pending AI Analysis';
};

// Format document type for display
export const formatDocumentType = (documentType: string): string => {
  if (!documentType || documentType === 'unknown' || documentType === 'other') {
    return 'Document - Pending Analysis';
  }
  
  // Map AI document types to display labels - Updated with all detected types
  const typeMap: Record<string, string> = {
    'medical_report': 'Medical Report',
    'lab_result': 'Lab Result', 
    'financial_report': 'Financial Report',
    'bank_statement': 'Bank Statement',
    'appointment': 'Appointment',
    'patient_record': 'Patient Record',
    'insurance_claim': 'Insurance Claim',
    'prescription': 'Prescription',
    'clinical_trial': 'Clinical Trial',
    'consent_form': 'Consent Form',
    'insurance': 'Insurance Document',
    'billing': 'Billing Document',
    'administrative': 'Administrative Document',
    'certificate': 'Certificate',
    'technical_document': 'Technical Document',
    'technical_report': 'Technical Report',
    'qa_document': 'QA Document',
    'guide': 'Guide',
    'tutorial': 'Tutorial',
    'manual': 'Manual',
    'presentation': 'Presentation',
    'legal_document': 'Legal Document',
    'contract': 'Contract',
    'unknown': 'Document - Pending Analysis',
    'other': 'Document - Needs Review'
  };
  
  return typeMap[documentType] || documentType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Get confidence level color
export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'success';
  if (confidence >= 0.6) return 'warning';
  return 'error';
};

// Get confidence level label
export const getConfidenceLabel = (confidence: number): string => {
  if (confidence >= 0.8) return 'High Confidence';
  if (confidence >= 0.6) return 'Medium Confidence';
  return 'Low Confidence';
};

export default documentsApi;