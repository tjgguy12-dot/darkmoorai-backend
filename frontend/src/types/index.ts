/**
 * DarkmoorAI Type Definitions
 */

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  role: 'user' | 'admin' | 'premium';
  is_active: boolean;
  is_verified?: boolean;
  avatar_url?: string;
  created_at?: string;
  total_messages?: number;
  total_documents?: number;
  settings?: UserSettings;
}

export interface UserSettings {
  theme: 'dark' | 'light';
  language: string;
  notifications_enabled: boolean;
  search_sources: string[];
  default_model?: string;
  temperature?: number;
  max_tokens?: number;  // Added: User adjustable token limit
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  cost?: number;
  tokens?: number;
  status?: 'sending' | 'sent' | 'error' | 'streaming' | 'loading';
}

export interface Source {
  type: 'wikipedia' | 'arxiv' | 'pubmed' | 'openlibrary' | 'gutenberg' | 'document' | 'google' | 'google_news';
  title: string;
  url?: string;
  relevance: number;
  content?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  document_id?: string;
  use_web_search: boolean;
  research_mode?: boolean;
  temperature?: number;
  max_tokens?: number;  // Added: User adjustable - up to 2200
}

export interface ChatResponse {
  answer: string;
  conversation_id: string;
  sources: Source[];
  cost: number;
  tokens_used: number;
  processing_time?: number;
}

export interface DocumentUpload {
  id: string;
  filename: string;
  size: number;
  type: string;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  pages?: number;
  chunks?: number;
  created_at?: string;
}

export interface SearchResult {
  source: string;
  title: string;
  summary: string;
  url: string;
  relevance: number;
  extra_data?: Record<string, any>;
}

export interface Conversation {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface ApiError {
  error: {
    code: number;
    message: string;
    type: string;
    details?: any;
  };
  request_id?: string;
}

export interface UsageStats {
  daily: {
    date: string;
    cost: number;
    budget: number;
    remaining: number;
    percentage: number;
  };
  monthly: {
    month: string;
    cost: number;
    projected: number;
  };
  tokens_today: number;
  budget_remaining: boolean;
}

// Token presets for user convenience
export const TOKEN_PRESETS = {
  short: 500,
  medium: 1000,
  long: 1500,
  extra_long: 2200,  // Max recommended
  max: 2200,
} as const;

export type TokenPreset = keyof typeof TOKEN_PRESETS;