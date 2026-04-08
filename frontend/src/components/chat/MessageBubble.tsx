import React, { useState } from 'react';
import { Message, Source } from '../../types';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MessageBubbleProps {
  message: Message;
  onRegenerate?: () => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onRegenerate }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getSourceIcon = (type: string) => {
    const icons: Record<string, string> = {
      wikipedia: '📖',
      arxiv: '🔬',
      pubmed: '🏥',
      openlibrary: '📚',
      document: '📄',
    };
    return icons[type] || '🔗';
  };

  return (
    <div className={`message ${message.role === 'user' ? 'user' : 'assistant'}`}>
      <div className="message-avatar">
        {message.role === 'user' ? '👤' : '🧠'}
      </div>
      <div className="message-content">
        <div className="message-header">
          <span className="message-sender">
            {message.role === 'user' ? 'You' : 'DarkmoorAI'}
          </span>
          <span className="message-time">{formatTime(message.timestamp)}</span>
        </div>
        
        <div className="message-text">
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div">
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className="inline-code" {...props}>{children}</code>
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <div className="sources-label">📚 Sources:</div>
            <div className="sources-list">
              {message.sources.map((source, idx) => (
                <a
                  key={idx}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-badge"
                >
                  {getSourceIcon(source.type)} {source.title}
                  <span className="relevance">{Math.round(source.relevance * 100)}%</span>
                </a>
              ))}
            </div>
          </div>
        )}

        {message.cost !== undefined && message.role === 'assistant' && (
          <div className="message-cost">
            💰 Cost: ${message.cost.toFixed(6)} • {message.tokens?.toLocaleString()} tokens
          </div>
        )}

        {message.role === 'assistant' && (
          <div className="message-actions">
            <button className="action-btn" onClick={handleCopy} title="Copy">
              {copied ? '✓' : '📋'}
            </button>
            {onRegenerate && (
              <button className="action-btn" onClick={onRegenerate} title="Regenerate">
                🔄
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;