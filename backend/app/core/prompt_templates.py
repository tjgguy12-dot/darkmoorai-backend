"""
Prompt Templates Module
DarkmoorAI - Complete prompt management system
"""

from typing import List, Dict, Optional


class PromptTemplates:
    """Collection of prompt templates for DarkmoorAI"""
    
    def __init__(self):
        """Initialize prompt templates"""
        self.system_prompts = {
            "default": "You are DarkmoorAI, a helpful, harmless, and honest AI assistant.",
            "professional": "You are DarkmoorAI, a professional AI assistant focused on business.",
            "creative": "You are DarkmoorAI, a creative AI assistant for brainstorming.",
            "academic": "You are DarkmoorAI, an academic AI assistant for research.",
            "technical": "You are DarkmoorAI, a technical AI assistant specializing in programming.",
            "friendly": "You are DarkmoorAI, a friendly and approachable AI assistant.",
            "concise": "You are DarkmoorAI, a concise AI assistant. Give short, direct answers."
        }
    
    def build_rag_prompt(self, question: str, contexts: List[str]) -> str:
        """Build RAG prompt with context"""
        context_text = "\n\n".join([f"Source {i+1}: {ctx}" for i, ctx in enumerate(contexts)])
        return f"""You are DarkmoorAI, a helpful AI assistant.

Use this information to answer the question:

{context_text}

Question: {question}

Answer:"""
    
    def build_summary_prompt(self, text: str, max_length: int = 500) -> str:
        """Build summary prompt"""
        return f"""Summarize the following text in {max_length} words or less:

{text}

Summary:"""
    
    def build_key_points_prompt(self, text: str, num_points: int = 5) -> str:
        """Build key points extraction prompt"""
        return f"""Extract the {num_points} most important key points from the following text:

{text}

Key Points:
1. """
    
    def build_code_explanation_prompt(self, code: str, language: str) -> str:
        """Build code explanation prompt"""
        return f"""Explain the following {language} code:

Explanation:"""
    
    def build_translation_prompt(self, text: str, target_language: str) -> str:
        """Build translation prompt"""
        return f"""Translate the following text to {target_language}:

{text}

Translation:"""
    
    def build_sentiment_prompt(self, text: str) -> str:
        """Build sentiment analysis prompt"""
        return f"""Analyze the sentiment of the following text:

{text}

Sentiment:"""
    
    def get_system_prompt(self, personality: str = "default") -> str:
        """Get system prompt"""
        return self.system_prompts.get(personality, self.system_prompts["default"])


# Global instance
prompt_templates = PromptTemplates()