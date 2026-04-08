"""
Pydantic Schemas
Request/response validation models for DarkmoorAI
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"


class SourceType(str, Enum):
    WIKIPEDIA = "wikipedia"
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    OPENLIBRARY = "openlibrary"
    GUTENBERG = "gutenberg"
    DOCUMENT = "document"
    CACHE = "cache"


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user information"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User registration data"""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserLogin(BaseModel):
    """User login data"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update data"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    total_messages: int = 0
    total_documents: int = 0
    settings: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class UserSettings(BaseModel):
    """User settings schema"""
    theme: str = Field("dark", pattern="^(light|dark)$")
    language: str = Field("en", min_length=2, max_length=5)
    notifications_enabled: bool = True
    search_sources: List[str] = Field(default=["wikipedia", "arxiv", "pubmed", "openlibrary"])
    default_model: str = "deepseek-chat"
    temperature: float = Field(0.7, ge=0, le=2)
    
    class Config:
        from_attributes = True


# ============================================================================
# Auth Schemas
# ============================================================================

class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


# ============================================================================
# Chat Schemas
# ============================================================================

class Message(BaseModel):
    """Chat message"""
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Chat request"""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    document_id: Optional[str] = None
    use_web_search: bool = True
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(2000, ge=1, le=4000)


class Source(BaseModel):
    """Information source"""
    type: SourceType
    title: str
    content: str
    url: Optional[str] = None
    relevance: float = Field(..., ge=0, le=1)
    extra_data: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """Chat response"""
    answer: str
    conversation_id: str
    sources: List[Source] = []
    cost: float = 0.0
    tokens_used: int = 0
    processing_time: float = 0.0


class Conversation(BaseModel):
    """Conversation summary"""
    id: str
    title: str
    message_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationDetail(Conversation):
    """Full conversation with messages"""
    messages: List[Message] = []


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    document_id: str
    filename: str
    status: str
    message: str


class DocumentResponse(BaseModel):
    """Document details"""
    id: str
    filename: str
    file_size: int
    mime_type: str
    status: str
    pages: int = 0
    chunks: int = 0
    created_at: datetime
    summary: Optional[str] = None
    key_points: List[str] = []
    
    class Config:
        from_attributes = True


class DocumentProcessRequest(BaseModel):
    """Document processing request"""
    document_id: str
    generate_summary: bool = True
    extract_key_points: bool = True


# ============================================================================
# Search Schemas
# ============================================================================

class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., min_length=2, max_length=500)
    sources: Optional[List[SourceType]] = None
    max_results: int = Field(5, ge=1, le=20)


class SearchResult(BaseModel):
    """Search result"""
    source: SourceType
    title: str
    summary: str
    url: Optional[str] = None
    relevance: float = Field(..., ge=0, le=1)
    extra_data: Dict[str, Any] = {}


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results: List[SearchResult] = []
    total: int = 0
    processing_time: float = 0.0


# ============================================================================
# Subscription Schemas
# ============================================================================

class SubscriptionPlan(BaseModel):
    """Subscription plan details"""
    id: str
    name: str
    price: int  # in cents
    features: List[str] = []
    limits: Dict[str, Any] = {}


class SubscriptionResponse(BaseModel):
    """Subscription details"""
    id: str
    tier: SubscriptionTier
    status: SubscriptionStatus
    current_period_end: Optional[str] = None
    messages_used: int = 0
    documents_used: int = 0
    tokens_used: int = 0
    limits: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    """Invoice details"""
    id: str
    amount: int
    currency: str = "usd"
    status: str
    invoice_pdf: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApiKey(BaseModel):
    """API key response"""
    id: str
    name: str
    key_preview: str
    created_at: datetime
    expires_at: Optional[str] = None
    last_used_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaymentMethod(BaseModel):
    """Payment method"""
    id: str
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    is_default: bool = False


# ============================================================================
# Cost Tracking Schemas
# ============================================================================

class DailyUsage(BaseModel):
    """Daily usage statistics"""
    date: str
    cost: float
    budget: float
    remaining: float
    percentage: float


class MonthlyUsage(BaseModel):
    """Monthly usage statistics"""
    month: str
    cost: float
    projected: float
    days_used: int
    days_in_month: int


class UsageStats(BaseModel):
    """User usage statistics"""
    user_id: str
    daily: DailyUsage
    monthly: MonthlyUsage
    tokens_today: int = 0
    actions_today: Dict[str, int] = {}
    budget_remaining: bool = True


# ============================================================================
# Knowledge Source Schemas
# ============================================================================

class WikipediaResult(BaseModel):
    """Wikipedia search result"""
    title: str
    summary: str
    url: str
    page_id: int
    categories: List[str] = []
    extra_data: Dict[str, Any] = {}


class ArxivResult(BaseModel):
    """arXiv search result"""
    title: str
    summary: str
    url: str
    pdf_url: str
    authors: List[str] = []
    published: str
    categories: List[str] = []
    extra_data: Dict[str, Any] = {}


class PubMedResult(BaseModel):
    """PubMed search result"""
    title: str
    abstract: str
    url: str
    pmid: str
    doi: Optional[str] = None
    authors: List[str] = []
    journal: str
    publication_date: str
    extra_data: Dict[str, Any] = {}


class OpenLibraryResult(BaseModel):
    """Open Library search result"""
    title: str
    author: str
    year: Optional[int] = None
    subjects: List[str] = []
    cover_url: Optional[str] = None
    url: str
    extra_data: Dict[str, Any] = {}


class GutenbergResult(BaseModel):
    """Project Gutenberg result"""
    title: str
    author: str
    url: str
    downloads: int = 0
    language: str = "en"
    subjects: List[str] = []
    extra_data: Dict[str, Any] = {}


# ============================================================================
# Feedback Schemas
# ============================================================================

class FeedbackRequest(BaseModel):
    """User feedback request"""
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response"""
    success: bool
    message: str


# ============================================================================
# Admin Schemas
# ============================================================================

class AdminUserUpdate(BaseModel):
    """Admin user update"""
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    subscription_tier: Optional[SubscriptionTier] = None


class SystemMetrics(BaseModel):
    """System metrics"""
    requests_total: int = 0
    errors_total: int = 0
    active_users: int = 0
    documents_processed: int = 0
    search_queries: int = 0
    api_calls: int = 0
    cost_total: float = 0.0
    queue_size: int = 0
    database_pool_size: int = 0
    cache_hit_ratio: float = 0.0


class SystemConfigUpdate(BaseModel):
    """System configuration update"""
    daily_budget_per_user: Optional[float] = Field(None, ge=0, le=10)
    max_tokens_per_query: Optional[int] = Field(None, ge=100, le=10000)
    rate_limit_requests: Optional[int] = Field(None, ge=10, le=1000)
    rate_limit_period: Optional[int] = Field(None, ge=10, le=3600)


# ============================================================================
# System Schemas
# ============================================================================

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    service: str = "darkmoorai-backend"


class DetailedHealth(BaseModel):
    """Detailed health check"""
    status: str
    timestamp: str
    version: str
    environment: str
    checks: Dict[str, Any] = {}


class SystemInfo(BaseModel):
    """System information"""
    name: str = "DarkmoorAI Backend"
    version: str = "1.0.0"
    description: str = "🧠 Intelligence, evolved"
    environment: str
    features: Dict[str, bool] = {}
    limits: Dict[str, Any] = {}
    documentation: str = "/docs"


class ErrorResponse(BaseModel):
    """Error response"""
    error: Dict[str, Any]
    request_id: Optional[str] = None