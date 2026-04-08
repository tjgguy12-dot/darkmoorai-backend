import React from 'react';

interface TypingIndicatorProps {
  message?: string;
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ 
  message = "DarkmoorAI is thinking..." 
}) => {
  return (
    <div className="message assistant typing">
      <div className="message-avatar">🧠</div>
      <div className="message-content">
        <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <div className="typing-text">{message}</div>
      </div>
    </div>
  );
};

export default TypingIndicator;