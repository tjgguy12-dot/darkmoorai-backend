import axios, { AxiosInstance } from 'axios';
import { ChatRequest, ChatResponse, SearchResult, DocumentUpload, User, TokenResponse } from '../types';

const API_BASE = 'http://localhost:8000/api/v1';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000, // 120 seconds for large documents
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('darkmoor_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timed out. Please try a simpler question.';
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('darkmoor_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// AUTHENTICATION
// ============================================================================

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await axios.post(`${API_BASE}/auth/login`, formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return response.data;
};

export const register = async (email: string, username: string, password: string): Promise<User> => {
  const response = await api.post('/auth/register', { email, username, password });
  return response.data;
};

export const logout = async (): Promise<void> => {
  try {
    await api.post('/auth/logout');
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    localStorage.removeItem('darkmoor_token');
  }
};

export const getProfile = async (): Promise<User> => {
  const response = await api.get('/user/profile');
  return response.data;
};

// ============================================================================
// CHAT
// ============================================================================

export const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post('/chat/chat', request);
  return response.data;
};

// ============================================================================
// DOCUMENTS
// ============================================================================

export const uploadDocument = async (file: File, onProgress?: (progress: number) => void) => {
  const formData = new FormData();
  formData.append('file', file);
  const token = localStorage.getItem('darkmoor_token');

  const response = await axios.post(`${API_BASE}/documents/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      Authorization: token ? `Bearer ${token}` : '',
    },
    timeout: 180000,
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });
  return response.data;
};

export const getDocuments = async (): Promise<DocumentUpload[]> => {
  const response = await api.get('/documents');
  return response.data;
};

export const deleteDocument = async (documentId: string): Promise<void> => {
  await api.delete(`/documents/${documentId}`);
};

// ============================================================================
// SEARCH
// ============================================================================

export const searchWikipedia = async (query: string, maxResults: number = 5): Promise<SearchResult[]> => {
  const response = await api.get('/search/wikipedia', { params: { q: query, max_results: maxResults } });
  return response.data;
};

export const searchArxiv = async (query: string, maxResults: number = 5): Promise<SearchResult[]> => {
  const response = await api.get('/search/arxiv', { params: { q: query, max_results: maxResults } });
  return response.data;
};

// ============================================================================
// OFFICE SUITE
// ============================================================================

export const createResume = async (data: any): Promise<Blob> => {
  const response = await api.post('/office/template/resume', data, { responseType: 'blob' });
  return response.data;
};

export const createInvoice = async (data: any): Promise<Blob> => {
  const response = await api.post('/office/template/invoice', data, { responseType: 'blob' });
  return response.data;
};

export const createBudget = async (data: any): Promise<Blob> => {
  const response = await api.post('/office/template/budget', data, { responseType: 'blob' });
  return response.data;
};

export const createReport = async (data: any): Promise<Blob> => {
  const response = await api.post('/office/template/report', data, { responseType: 'blob' });
  return response.data;
};

export const createBusinessLetter = async (data: any): Promise<Blob> => {
  const response = await api.post('/office/template/business_letter', data, { responseType: 'blob' });
  return response.data;
};

export const createPresentation = async (data: any): Promise<Blob> => {
  const response = await api.post('/office/template/presentation', data, { responseType: 'blob' });
  return response.data;
};

export const convertDocument = async (file: File, outputFormat: string): Promise<Blob> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('output_format', outputFormat);
  
  const response = await api.post('/office/convert', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    responseType: 'blob',
  });
  return response.data;
};

// ============================================================================
// USER
// ============================================================================

export const getUsageStats = async () => {
  const response = await api.get('/user/usage');
  return response.data;
};

export default api;