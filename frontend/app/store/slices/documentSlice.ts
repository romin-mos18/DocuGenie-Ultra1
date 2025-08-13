import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface AIInsights {
  summary: string;
  key_phrases: string[];
  action_items: string[];
  confidence_analysis: {
    high_confidence: string[];
    medium_confidence: string[];
    low_confidence: string[];
  };
}

export interface KeyInformation {
  primary_entities: Record<string, any[]>;
  secondary_entities: Record<string, any[]>;
  document_specific: Record<string, any>;
}

export interface AIClassification {
  document_type: string;
  classification_confidence: number;
  ai_learning_source: string;
  document_category: string;
}

export interface ExtractedContent {
  text_preview: string;
  word_count: number;
  extraction_method: string;
  ai_models_used: string[];
}

export interface LanguageAnalysis {
  primary_language: string;
  detection_confidence: number;
  language_code: string;
}

export interface ProcessingMetadata {
  processing_time: string;
  ai_services_used: string[];
  learning_applied: string;
}

export interface Document {
  id: number;
  title: string;
  filename: string;
  fileType: string;
  fileSize?: number;
  status: 'uploaded' | 'processing' | 'processed' | 'error';
  documentType?: string;
  ocrText?: string;
  classificationConfidence?: number;
  extractedEntities?: Record<string, any>;
  documentMetadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  
  // AI-Generated Detail View Data
  ai_processing_status?: 'pending' | 'completed' | 'failed';
  overall_confidence?: number;
  ai_classification?: AIClassification;
  extracted_content?: ExtractedContent;
  key_information?: KeyInformation;
  ai_insights?: AIInsights;
  language_analysis?: LanguageAnalysis;
  processing_metadata?: ProcessingMetadata;
}

interface DocumentState {
  documents: Document[];
  selectedDocument: Document | null;
  isLoading: boolean;
  error: string | null;
  filters: {
    status?: string;
    documentType?: string;
    searchTerm?: string;
  };
  pagination: {
    page: number;
    limit: number;
    total: number;
  };
}

const initialState: DocumentState = {
  documents: [],
  selectedDocument: null,
  isLoading: false,
  error: null,
  filters: {},
  pagination: {
    page: 1,
    limit: 10,
    total: 0,
  },
};

export const documentSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    setDocuments: (state, action: PayloadAction<Document[]>) => {
      state.documents = action.payload;
    },
    addDocument: (state, action: PayloadAction<Document>) => {
      state.documents.unshift(action.payload);
    },
    updateDocument: (state, action: PayloadAction<Document>) => {
      const index = state.documents.findIndex((doc) => doc.id === action.payload.id);
      if (index !== -1) {
        state.documents[index] = action.payload;
      }
    },
    removeDocument: (state, action: PayloadAction<number>) => {
      state.documents = state.documents.filter((doc) => doc.id !== action.payload);
    },
    setSelectedDocument: (state, action: PayloadAction<Document | null>) => {
      state.selectedDocument = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    setFilters: (state, action: PayloadAction<DocumentState['filters']>) => {
      state.filters = action.payload;
    },
    setPagination: (state, action: PayloadAction<Partial<DocumentState['pagination']>>) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    clearDocuments: (state) => {
      state.documents = [];
      state.selectedDocument = null;
      state.filters = {};
      state.pagination = initialState.pagination;
    },
  },
});

export const {
  setDocuments,
  addDocument,
  updateDocument,
  removeDocument,
  setSelectedDocument,
  setLoading,
  setError,
  setFilters,
  setPagination,
  clearDocuments,
} = documentSlice.actions;

export default documentSlice.reducer;
