import { useState, useCallback } from 'react';
import { sendMessage } from '../services/api';
import { Message, TOKEN_PRESETS } from '../types';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `# 🧠 Welcome to DarkmoorAI

I'm your intelligent assistant powered by DeepSeek AI. I can help you with:

📄 **Documents** - Upload PDFs, Word files, Excel sheets
🔍 **Research** - Search Wikipedia, arXiv, PubMed
💬 **Questions** - Ask anything, get answers with citations
📝 **Office Suite** - Create resumes, invoices, budgets
🌐 **Google Search** - Get real-time information from the web
🔬 **Research Mode** - Searches ALL sources (Google, News, Wikipedia, arXiv, PubMed)

**What would you like help with today?**

---
💡 **Tips:**
- 🔬 Turn on **Research Mode** for comprehensive answers with multiple sources
- 📝 Adjust response length using the dropdown
- 🎨 Change creativity level for different response styles
- 📄 Upload documents to ask questions about them`,
      timestamp: new Date(),
      status: 'sent',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [maxTokens, setMaxTokens] = useState<number>(1500); // Default to Long
  const [temperature, setTemperature] = useState<number>(0.7);
  const [researchMode, setResearchMode] = useState<boolean>(false);

  const sendChatMessage = useCallback(async (
    content: string,
    useWebSearch: boolean = true,
    documentId?: string,
    temperatureOverride?: number,
    maxTokensOverride?: number,
    researchModeOverride?: boolean
  ) => {
    if (!content.trim()) return;

    // Use overrides if provided, otherwise use current settings
    const tokensToUse = maxTokensOverride !== undefined ? maxTokensOverride : maxTokens;
    const tempToUse = temperatureOverride !== undefined ? temperatureOverride : temperature;
    const researchToUse = researchModeOverride !== undefined ? researchModeOverride : researchMode;

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
      status: 'sent',
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setIsStreaming(true);

    // Add assistant placeholder
    const assistantId = `assistant-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      status: 'streaming',
    }]);

    try {
      const response = await sendMessage({
        message: content.trim(),
        use_web_search: useWebSearch,
        document_id: documentId,
        temperature: tempToUse,
        max_tokens: tokensToUse,
        research_mode: researchToUse,
      });

      setMessages(prev => prev.map(msg =>
        msg.id === assistantId
          ? {
              ...msg,
              content: response.answer,
              sources: response.sources || [],
              cost: response.cost,
              tokens: response.tokens_used,
              status: 'sent',
            }
          : msg
      ));

    } catch (error: any) {
      console.error('Chat error:', error);
      
      let errorMessage = "Sorry, I encountered an error. Please try again.";
      
      if (error.response?.status === 504) {
        errorMessage = "The AI service is taking too long. Please try a shorter question or reduce the response length.";
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = "Request timed out. Please try again with a simpler question or shorter response length.";
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      setMessages(prev => prev.map(msg =>
        msg.id === assistantId
          ? { ...msg, content: errorMessage, status: 'error' }
          : msg
      ));
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  }, [maxTokens, temperature, researchMode]);

  const clearMessages = useCallback(() => {
    setMessages([messages[0]]);
  }, [messages]);

  const regenerateLastMessage = useCallback(() => {
    const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
    if (lastUserMessage) {
      sendChatMessage(lastUserMessage.content);
    }
  }, [messages, sendChatMessage]);

  const updateMaxTokens = useCallback((tokens: number) => {
    setMaxTokens(tokens);
  }, []);

  const updateTemperature = useCallback((temp: number) => {
    setTemperature(temp);
  }, []);

  const toggleResearchMode = useCallback(() => {
    setResearchMode(prev => !prev);
  }, []);

  return { 
    messages, 
    isLoading, 
    isStreaming, 
    sendChatMessage, 
    clearMessages,
    regenerateLastMessage,
    maxTokens,
    updateMaxTokens,
    temperature,
    updateTemperature,
    researchMode,
    toggleResearchMode,
  };
}