import React, { useState, useEffect } from 'react';
import Header from './components/common/Header';
import MessageBubble from './components/chat/MessageBubble';
import MessageInput from './components/chat/MessageInput';
import TypingIndicator from './components/chat/TypingIndicator';
import SearchPanel from './components/search/SearchPanel';
import FileUploader from './components/upload/FileUploader';
import OfficeTools from './components/office/OfficeTools';
import { useChat } from './hooks/useChat';
import { useFileUpload } from './hooks/useFileUpload';
import { useAuth } from './contexts/AuthContext';
import './App.css';

const App: React.FC = () => {
  const { 
    messages, 
    isLoading, 
    sendChatMessage, 
    clearMessages,
    maxTokens,
    updateMaxTokens,
    temperature,
    updateTemperature,
    researchMode,
    toggleResearchMode,
  } = useChat();
  
  const { documents, selectedDocument, setSelectedDocument, uploadFile, loadDocuments } = useFileUpload();
  const { isAuthenticated, user } = useAuth();
  const [showSearch, setShowSearch] = useState(false);
  const [showFiles, setShowFiles] = useState(false);
  const [showOffice, setShowOffice] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      loadDocuments();
    }
  }, [isAuthenticated, loadDocuments]);

  const handleSend = (message: string, useWebSearch: boolean, documentId?: string, temp?: number, tokens?: number, research?: boolean) => {
    sendChatMessage(message, useWebSearch, documentId, temp, tokens, research);
  };

  const handleFileUpload = async (file: File) => {
    await uploadFile(file);
  };

  const handleDocumentCreated = (filename: string) => {
    console.log(`Document created: ${filename}`);
  };

  return (
    <div className="darkmoor-container">
      <Header />

      <main className="darkmoor-main">
        <div className="messages-area">
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          ))}
          {isLoading && <TypingIndicator message={researchMode ? "🔬 Research Mode: Searching multiple sources..." : "DarkmoorAI is thinking..."} />}
          <div className="messages-end" />
        </div>

        <div className="sidebar">
          <button
            className={`sidebar-toggle ${showSearch ? 'active' : ''}`}
            onClick={() => setShowSearch(!showSearch)}
          >
            🔍 {showSearch ? 'Hide Search' : 'Show Search'}
          </button>
          
          <button
            className={`sidebar-toggle ${showFiles ? 'active' : ''}`}
            onClick={() => setShowFiles(!showFiles)}
          >
            📄 {showFiles ? 'Hide Files' : 'My Documents'}
          </button>
          
          <button
            className={`sidebar-toggle ${showOffice ? 'active' : ''}`}
            onClick={() => setShowOffice(!showOffice)}
          >
            📝 {showOffice ? 'Hide Office' : 'Office Suite'}
          </button>
          
          {showSearch && <SearchPanel />}
          
          {showFiles && (
            <div className="files-panel">
              <h3>📁 Your Documents</h3>
              <FileUploader onUpload={handleFileUpload} />
              {documents.length > 0 && (
                <div className="document-list">
                  <h4>Uploaded Documents</h4>
                  {documents.map(doc => (
                    <div
                      key={doc.id}
                      className={`document-item ${selectedDocument?.id === doc.id ? 'selected' : ''}`}
                      onClick={() => setSelectedDocument(doc)}
                    >
                      <span>📄 {doc.filename}</span>
                      {doc.status === 'completed' && <span className="badge">✅</span>}
                      {doc.pages && <span className="badge">{doc.pages} pages</span>}
                    </div>
                  ))}
                </div>
              )}
              {selectedDocument && (
                <div className="selected-doc">
                  <p>📄 Using: <strong>{selectedDocument.filename}</strong></p>
                  <button onClick={() => setSelectedDocument(null)}>Clear</button>
                </div>
              )}
            </div>
          )}
          
          {showOffice && <OfficeTools onDocumentCreated={handleDocumentCreated} />}
        </div>
      </main>

      <MessageInput 
        onSend={handleSend} 
        isLoading={isLoading}
        maxTokens={maxTokens}
        onMaxTokensChange={updateMaxTokens}
        temperature={temperature}
        onTemperatureChange={updateTemperature}
        researchMode={researchMode}
        onResearchModeToggle={toggleResearchMode}
      />

      <div className="usage-bar">
        {isAuthenticated ? (
          <span>👋 Welcome, {user?.username || user?.email}!</span>
        ) : (
          <span>🔓 Sign in to save conversations and upload documents</span>
        )}
        {researchMode && <span className="research-badge">🔬 RESEARCH MODE ACTIVE</span>}
        <span>🧠 Powered by DeepSeek AI</span>
        <span>📄 Create resumes, invoices, budgets</span>
        <span>🔒 Your data is private</span>
      </div>
    </div>
  );
};

export default App;