import api from './axios';
import { Document } from '../../app/store/slices/documentSlice';

interface DocumentFilters {
  status?: string;
  documentType?: string;
  searchTerm?: string;
}

interface DocumentListResponse {
  documents: Document[];
  total: number;
}

interface DocumentUploadResponse {
  document: Document;
  message: string;
}

interface DocumentProcessResponse {
  document: Document;
  message: string;
}

interface AIAnalysisResponse {
  success: boolean;
  ai_analysis: any;
  message: string;
}

export const documentsApi = {
  getDocuments: async (
    page: number = 1,
    limit: number = 10,
    filters?: DocumentFilters
  ): Promise<DocumentListResponse> => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filters?.status && { status: filters.status }),
      ...(filters?.documentType && { document_type: filters.documentType }),
      ...(filters?.searchTerm && { search: filters.searchTerm }),
    });

    const response = await api.get<DocumentListResponse>(`/documents?${params}`);
    return response.data;
  },

  getDocument: async (id: number): Promise<Document> => {
    const response = await api.get<Document>(`/documents/${id}`);
    return response.data;
  },

  uploadDocument: async (file: File, title?: string): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) {
      formData.append('title', title);
    }

    const response = await api.post<DocumentUploadResponse>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  processDocument: async (id: number): Promise<DocumentProcessResponse> => {
    const response = await api.post<DocumentProcessResponse>(`/documents/${id}/process`);
    return response.data;
  },

  processDocumentWithAI: async (id: number): Promise<DocumentProcessResponse> => {
    const response = await api.post<DocumentProcessResponse>(`/documents/${id}/process-ai`);
    return response.data;
  },

  getDocumentAIAnalysis: async (id: number): Promise<AIAnalysisResponse> => {
    const response = await api.get<AIAnalysisResponse>(`/documents/${id}/ai-analysis`);
    return response.data;
  },

  deleteDocument: async (id: number): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },

  downloadDocument: async (id: number): Promise<Blob> => {
    const response = await api.get(`/documents/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  getDocumentAnalysis: async (id: number): Promise<Document> => {
    const response = await api.get<Document>(`/documents/${id}/analysis`);
    return response.data;
  },

  getAIStats: async (): Promise<{
    supported_formats: string[];
    document_types: string[];
    ai_service_stats: Record<string, any>;
  }> => {
    const response = await api.get('/documents/ai/stats');
    return response.data;
  },

  batchUpload: async (files: File[]): Promise<DocumentUploadResponse[]> => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post<DocumentUploadResponse[]>('/documents/batch-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
