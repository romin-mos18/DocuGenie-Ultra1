// AI-powered documents API client
import axios from './axios';

export interface AIDocumentUploadResponse {
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

export interface AIDocument {
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
  ai_summary: string;
  ai_analysis: {
    success: boolean;
    document_type: string;
    confidence: number;
    processing_method: string;
    extraction_successful: boolean;
    analysis_successful: boolean;
    word_count: number;
    processing_time: number;
  };
  classification: {
    document_type: string;
    confidence: number;
    success: boolean;
    reasoning: string[];
    alternatives: Array<{
      type: string;
      confidence: number;
      reasoning: string[];
    }>;
  };
  key_information: Record<string, any>;
  processing_stats: Record<string, any>;
}

export interface AIDocumentDetails extends AIDocument {
  ai_analysis: {
    success: boolean;
    processing_method: string;
    processing_time: number;
    extraction: {
      text: string;
      word_count: number;
      confidence: number;
      method: string;
    };
    content_analysis: {
      word_count: number;
      sentence_count: number;
      readability_score: number;
      avg_sentence_length: number;
    };
    structural_analysis: {
      has_headers: boolean;
      has_medical_terms: boolean;
      has_dates: boolean;
      document_structure: Record<string, any>;
    };
    classification: {
      document_type: string;
      confidence: number;
      reasoning: string[];
      alternatives: Array<{
        type: string;
        confidence: number;
      }>;
    };
    summary: {
      summary: string;
      summary_type: string;
      word_count: number;
    };
    key_information: Record<string, any>;
    processing_stats: Record<string, any>;
  };
  extracted_text: string;
  ai_summary: string;
}

export interface AIStats {
  success: boolean;
  ai_processing_stats: {
    processor_stats: {
      service_name: string;
      processing_stats: {
        total_processed: number;
        successful: number;
        failed: number;
        last_processed: string;
      };
      capabilities: Record<string, boolean>;
      supported_types: string[];
      document_types: string[];
    };
    document_stats: {
      total_documents: number;
      processed_successfully: number;
      currently_processing: number;
      failed_processing: number;
      success_rate: number;
    };
    classification_stats: {
      document_type_distribution: Record<string, number>;
      average_confidence: number;
      high_confidence_docs: number;
      low_confidence_docs: number;
    };
    capabilities: Record<string, boolean>;
    supported_types: string[];
  };
}

// AI Documents API functions
export const aiDocumentsApi = {
  // Upload document with AI processing
  uploadWithAI: async (file: File): Promise<AIDocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post('/ai-documents/ai-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 second timeout for AI processing
    });
    
    return response.data;
  },

  // Get all AI-processed documents
  getAIDocuments: async (): Promise<{ documents: AIDocument[]; total: number }> => {
    const response = await axios.get('/ai-documents/ai-documents');
    return response.data;
  },

  // Get detailed AI analysis for a document
  getAIDocumentDetails: async (documentId: string): Promise<{
    success: boolean;
    document: AIDocument;
    ai_analysis: AIDocumentDetails['ai_analysis'];
    extracted_text: string;
    ai_summary: string;
  }> => {
    const response = await axios.get(`/ai-documents/ai-documents/${documentId}`);
    return response.data;
  },

  // Delete AI document
  deleteAIDocument: async (documentId: string): Promise<{
    success: boolean;
    message: string;
    document_id: string;
    deleted_at: string;
  }> => {
    const response = await axios.delete(`/ai-documents/ai-documents/${documentId}`);
    return response.data;
  },

  // Get AI processing statistics
  getAIStats: async (): Promise<AIStats> => {
    const response = await axios.get('/ai-documents/ai-stats');
    return response.data;
  },

  // Reprocess document with AI
  reprocessDocument: async (documentId: string): Promise<{
    success: boolean;
    message: string;
    document_id: string;
    document_type: string;
    confidence: number;
    processing_time: number;
  }> => {
    const response = await axios.post(`/ai-documents/ai-documents/${documentId}/reprocess`);
    return response.data;
  },

  // Legacy compatibility - use AI upload for regular uploads
  uploadDocument: async (file: File): Promise<AIDocumentUploadResponse> => {
    return aiDocumentsApi.uploadWithAI(file);
  },

  // Legacy compatibility - use AI documents for regular document list
  getDocuments: async (): Promise<{ documents: AIDocument[]; total: number }> => {
    return aiDocumentsApi.getAIDocuments();
  }
};

// Helper functions
export const getDocumentTypeLabel = (documentType: string): string => {
  const labels: Record<string, string> = {
    'medical_report': 'Medical Report',
    'lab_result': 'Lab Result',
    'prescription': 'Prescription',
    'clinical_trial': 'Clinical Trial',
    'consent_form': 'Consent Form',
    'insurance': 'Insurance',
    'billing': 'Billing',
    'administrative': 'Administrative',
    'other': 'Other',
    'unknown': 'Unknown'
  };
  
  return labels[documentType] || documentType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'success';
  if (confidence >= 0.6) return 'warning';
  return 'error';
};

export const getConfidenceLabel = (confidence: number): string => {
  if (confidence >= 0.8) return 'High Confidence';
  if (confidence >= 0.6) return 'Medium Confidence';
  return 'Low Confidence';
};

export const formatProcessingTime = (seconds: number): string => {
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
  return `${seconds.toFixed(1)}s`;
};

export default aiDocumentsApi;
