import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { useFileUpload } from '../../hooks/useFileUpload';

interface MessageInputProps {
  onSend: (message: string, useWebSearch: boolean, documentId?: string, temperature?: number, maxTokens?: number, researchMode?: boolean) => void;
  isLoading: boolean;
  maxTokens?: number;
  onMaxTokensChange?: (tokens: number) => void;
  temperature?: number;
  onTemperatureChange?: (temp: number) => void;
  researchMode?: boolean;
  onResearchModeToggle?: () => void;
}

// MASSIVE TOKEN OPTIONS - Up to 50,000!
const TOKEN_OPTIONS = [
  { label: 'Short (500)', value: 500, description: 'Quick, concise answers (1-2 paragraphs)' },
  { label: 'Medium (2,000)', value: 2000, description: 'Detailed answers (half page)' },
  { label: 'Long (5,000)', value: 5000, description: 'Very detailed (full page)' },
  { label: 'Extra Long (10,000)', value: 10000, description: 'Extremely detailed (2-3 pages)' },
  { label: 'Massive (25,000)', value: 25000, description: 'Novel-length responses (10-15 pages)' },
  { label: 'Maximum (50,000)', value: 50000, description: 'Full book chapter (20+ pages)!' },
];

const TEMPERATURE_OPTIONS = [
  { label: 'Precise', value: 0.3, description: 'Factual, consistent, predictable' },
  { label: 'Balanced', value: 0.7, description: 'Creative yet factual (recommended)' },
  { label: 'Creative', value: 1.0, description: 'Imaginative, diverse ideas' },
  { label: 'Very Creative', value: 1.5, description: 'Experimental, unique, surprising' },
];

const MessageInput: React.FC<MessageInputProps> = ({ 
  onSend, 
  isLoading, 
  maxTokens = 50000,
  onMaxTokensChange,
  temperature = 0.7,
  onTemperatureChange,
  researchMode = false,
  onResearchModeToggle,
}) => {
  const [message, setMessage] = useState('');
  const [useWebSearch, setUseWebSearch] = useState(true);
  const [showTokenSelector, setShowTokenSelector] = useState(false);
  const [showTempSelector, setShowTempSelector] = useState(false);
  const [showFilePreview, setShowFilePreview] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { uploadFile, uploading, documents, removeDocument } = useFileUpload();

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSend = () => {
    if (!message.trim() || isLoading) return;
    const activeDoc = documents.find(d => d.status === 'completed');
    onSend(message.trim(), researchMode ? true : useWebSearch, activeDoc?.id, temperature, maxTokens, researchMode);
    setMessage('');
    setShowFilePreview(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Check file size (500MB max)
      if (file.size > 500 * 1024 * 1024) {
        alert('File too large! Maximum size is 500MB');
        return;
      }
      setShowFilePreview(true);
      await uploadFile(file);
    }
  };

  const getCurrentTokenLabel = () => {
    const option = TOKEN_OPTIONS.find(opt => opt.value === maxTokens);
    return option ? option.label : `Massive (${maxTokens.toLocaleString()} tokens)`;
  };

  const getCurrentTempLabel = () => {
    const option = TEMPERATURE_OPTIONS.find(opt => opt.value === temperature);
    return option ? option.label : 'Balanced';
  };

  const getTokenInfo = () => {
    if (maxTokens >= 50000) return "📖 Can write entire book chapters!";
    if (maxTokens >= 25000) return "📚 Novel-length responses";
    if (maxTokens >= 10000) return "📄 Extremely detailed";
    if (maxTokens >= 5000) return "📝 Very detailed answers";
    return "📋 Quick responses";
  };

  return (
    <div className="input-container">
      <div className="input-actions">
        <button
          className={`action-pill ${researchMode ? 'active research-mode' : ''}`}
          onClick={onResearchModeToggle}
          title="Research Mode - Searches ALL sources (Google, Bing, News, Wikipedia, arXiv, PubMed)"
        >
          🔬 Research Mode {researchMode && 'ON'}
        </button>
        
        {!researchMode && (
          <button
            className={`action-pill ${useWebSearch ? 'active' : ''}`}
            onClick={() => setUseWebSearch(!useWebSearch)}
            title="Search the web for current information"
          >
            🌐 Web Search
          </button>
        )}
        
        <button
          className="action-pill"
          onClick={() => fileInputRef.current?.click()}
          title="Upload documents up to 500MB (PDF, Word, Excel, Images, PPT)"
        >
          📎 Attach File (500MB max)
        </button>
        
        <div className="dropdown-container">
          <button
            className={`action-pill ${showTokenSelector ? 'active' : ''}`}
            onClick={() => setShowTokenSelector(!showTokenSelector)}
            title="Adjust response length - up to 50,000 tokens!"
          >
            📝 {getCurrentTokenLabel()}
          </button>
          {showTokenSelector && (
            <div className="dropdown-menu token-menu massive-token-menu">
              {TOKEN_OPTIONS.map(option => (
                <button
                  key={option.value}
                  className={`dropdown-item ${maxTokens === option.value ? 'active' : ''}`}
                  onClick={() => {
                    onMaxTokensChange?.(option.value);
                    setShowTokenSelector(false);
                  }}
                >
                  <span className="dropdown-label">{option.label}</span>
                  <span className="dropdown-desc">{option.description}</span>
                </button>
              ))}
              <div className="dropdown-divider"></div>
              <div className="dropdown-info">
                ⚡ 50,000 tokens = ~20 pages of text!<br />
                💰 Costs ~$0.014 per maximum response<br />
                🔥 Perfect for comprehensive research, book analysis, and long-form content
              </div>
            </div>
          )}
        </div>
        
        <div className="dropdown-container">
          <button
            className={`action-pill ${showTempSelector ? 'active' : ''}`}
            onClick={() => setShowTempSelector(!showTempSelector)}
            title="Adjust creativity level"
          >
            🎨 {getCurrentTempLabel()}
          </button>
          {showTempSelector && (
            <div className="dropdown-menu temp-menu">
              {TEMPERATURE_OPTIONS.map(option => (
                <button
                  key={option.value}
                  className={`dropdown-item ${temperature === option.value ? 'active' : ''}`}
                  onClick={() => {
                    onTemperatureChange?.(option.value);
                    setShowTempSelector(false);
                  }}
                >
                  <span className="dropdown-label">{option.label}</span>
                  <span className="dropdown-desc">{option.description}</span>
                </button>
              ))}
              <div className="dropdown-divider"></div>
              <div className="dropdown-info">
                🔥 Higher temperature = more creative responses<br />
                ❄️ Lower temperature = more factual responses
              </div>
            </div>
          )}
        </div>
        
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          accept=".pdf,.docx,.doc,.xlsx,.xls,.txt,.jpg,.jpeg,.png,.pptx,.csv"
        />
      </div>

      {showFilePreview && documents.length > 0 && (
        <div className="file-preview">
          {documents.map(doc => (
            <div key={doc.id} className="file-item">
              <span>📄 {doc.filename}</span>
              <span className="file-size">({(doc.size / (1024 * 1024)).toFixed(2)} MB)</span>
              {doc.status === 'uploading' && (
                <div className="progress-bar" style={{ width: `${doc.progress}%` }} />
              )}
              {doc.status === 'completed' && <span className="success">✅ Processed</span>}
              {doc.status === 'failed' && <span className="error">❌ Failed</span>}
              <button onClick={() => removeDocument(doc.id)}>✕</button>
            </div>
          ))}
        </div>
      )}

      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          className="message-input"
          placeholder={researchMode 
            ? "🔬 RESEARCH MODE ACTIVE! I'll search Google, Bing, News, Wikipedia, arXiv, PubMed. Ask anything for comprehensive answers up to 50,000 tokens..."
            : "Ask DarkmoorAI anything... Upload 500MB documents, ask complex questions, get massive answers up to 50,000 tokens!"}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={isLoading || uploading}
        />
        <button 
          className="send-btn" 
          onClick={handleSend} 
          disabled={!message.trim() || isLoading}
          title="Send message"
        >
          ➤
        </button>
      </div>

      <div className="input-footer">
        {researchMode ? (
          <>
            <span>🔬 RESEARCH MODE ACTIVE</span>
            <span>📚 Searching: Google • Bing • DuckDuckGo • Yahoo • Brave • News • Wikipedia • arXiv • PubMed</span>
            <span>📝 Response: {getCurrentTokenLabel()} ({getTokenInfo()})</span>
            <span>🎨 Creativity: {getCurrentTempLabel()}</span>
            <span>💾 Memory: 1000 messages remembered</span>
          </>
        ) : (
          <>
            <span>🧠 RAG optimized — only relevant content sent to AI</span>
            <span>📝 Response: {getCurrentTokenLabel()} ({getTokenInfo()})</span>
            <span>🎨 Creativity: {getCurrentTempLabel()}</span>
            <span>📂 Upload up to 500MB documents</span>
            <span>💾 Remembers 1000 messages</span>
            <span>🔒 Your data stays private</span>
          </>
        )}
      </div>
    </div>
  );
};

export default MessageInput;