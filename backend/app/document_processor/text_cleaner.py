"""
Text Cleaner Module
Clean and normalize extracted text
"""

import re
import unicodedata
from typing import Optional

class TextCleaner:
    """
    Clean and normalize text from documents
    """
    
    def __init__(self):
        # Common patterns to clean
        self.patterns = [
            (r'\s+', ' '),  # Multiple spaces
            (r'\n\s+\n', '\n\n'),  # Lines with only spaces
            (r'[^\x00-\x7F]+', self._replace_unicode),  # Non-ASCII
            (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+', '[URL]'),  # URLs
            (r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]'),  # Emails
        ]
    
    def clean(self, text: str, options: Optional[dict] = None) -> str:
        """
        Clean text with specified options
        """
        if not text:
            return ""
        
        options = options or {}
        
        # Basic cleaning
        text = self._basic_clean(text)
        
        # Remove URLs if requested
        if options.get('remove_urls', True):
            text = self._remove_urls(text)
        
        # Remove emails if requested
        if options.get('remove_emails', True):
            text = self._remove_emails(text)
        
        # Remove extra whitespace
        if options.get('normalize_whitespace', True):
            text = self._normalize_whitespace(text)
        
        # Fix common OCR errors
        if options.get('fix_ocr', True):
            text = self._fix_ocr_errors(text)
        
        # Remove control characters
        if options.get('remove_control_chars', True):
            text = self._remove_control_chars(text)
        
        return text.strip()
    
    def _basic_clean(self, text: str) -> str:
        """Basic cleaning"""
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Replace common problematic characters
        replacements = {
            '\u2018': "'", '\u2019': "'",  # Smart quotes
            '\u201c': '"', '\u201d': '"',  # Smart double quotes
            '\u2013': '-', '\u2014': '--',  # Dashes
            '\u2026': '...',  # Ellipsis
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+'
        return re.sub(url_pattern, '[URL]', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses"""
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        return re.sub(email_pattern, '[EMAIL]', text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace"""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors"""
        fixes = [
            (r'(\d)l(\d)', r'\g<1>1\g<2>'),  # l mistaken for 1
            (r'0([A-Z])', r'O\g<1>'),  # 0 mistaken for O
            (r'([A-Z])0', r'\g<1>O'),  # 0 mistaken for O
            (r'rn', r'm'),  # rn mistaken for m
            (r'cl', r'd'),  # cl mistaken for d
        ]
        
        for pattern, repl in fixes:
            text = re.sub(pattern, repl, text)
        
        return text
    
    def _remove_control_chars(self, text: str) -> str:
        """Remove control characters"""
        return ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    
    def _replace_unicode(self, match) -> str:
        """Replace unicode with ascii equivalent"""
        char = match.group(0)
        try:
            return unicodedata.normalize('NFKD', char).encode('ascii', 'ignore').decode()
        except:
            return ''
    
    def extract_sentences(self, text: str) -> list:
        """Extract sentences from text"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_paragraphs(self, text: str) -> list:
        """Extract paragraphs from text"""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    def remove_boilerplate(self, text: str) -> str:
        """Remove common boilerplate text"""
        boilerplate_patterns = [
            r'(?i)copyright © \d{4}.*?\n',
            r'(?i)all rights reserved.*?\n',
            r'(?i)terms and conditions.*?\n',
            r'(?i)privacy policy.*?\n',
        ]
        
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def truncate(self, text: str, max_length: int, add_ellipsis: bool = True) -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:
            truncated = truncated[:last_space]
        
        if add_ellipsis:
            truncated += '...'
        
        return truncated

# Global instance
text_cleaner = TextCleaner()