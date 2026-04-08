"""
DarkmoorAI Configuration Module
Environment-based configuration with validation
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path
from dotenv import load_dotenv

# FORCE load .env from the correct location
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)
print(f"📁 Loading .env from: {env_path}")

class Config(BaseSettings):
    """
    Application configuration with environment variable support
    """
    
    # ============================================================================
    # Environment & Server
    # ============================================================================
    ENV: str = Field(default="development", env="ENV")
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=4, env="WORKERS")
    
    # ============================================================================
    # API
    # ============================================================================
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
        env="CORS_ORIGINS"
    )
    
    # ============================================================================
    # Database
    # ============================================================================
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: int = Field(default=5432, env="DB_PORT")
    DB_NAME: str = Field(default="darkmoorai", env="DB_NAME")
    DB_USER: str = Field(default="postgres", env="DB_USER")
    DB_PASSWORD: str = Field(default="postgres", env="DB_PASSWORD")
    DB_POOL_SIZE: int = Field(default=5, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=10, env="DB_MAX_OVERFLOW")
    
    @property
    def DATABASE_URL(self) -> str:
        """Get database URL"""
        if self.ENV == "development":
            return f"sqlite:///./darkmoorai.db"
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # ============================================================================
    # Redis
    # ============================================================================
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    @property
    def REDIS_URL(self) -> Optional[str]:
        """Get Redis URL – returns None for development to avoid invalid scheme"""
        if self.ENV == "development":
            return None
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ============================================================================
    # DeepSeek API
    # ============================================================================
    DEEPSEEK_API_KEY: str = Field(default="", env="DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com/v1", env="DEEPSEEK_BASE_URL")
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat", env="DEEPSEEK_MODEL")
    
    @field_validator("DEEPSEEK_API_KEY")
    def validate_deepseek_key(cls, v):
        """Validate DeepSeek API key"""
        if not v or len(v) < 10:
            print(f"⚠️ WARNING: DeepSeek API key is missing or too short!")
        else:
            print(f"✅ DeepSeek API key loaded: {v[:10]}...{v[-4:]}")
        return v
    
    # ============================================================================
    # Model Settings
    # ============================================================================
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    EMBEDDING_DIM: int = 384
    CHUNK_SIZE: int = Field(default=2000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")
    MAX_RETRIEVED_CHUNKS: int = Field(default=20, env="MAX_RETRIEVED_CHUNKS")
    
    # ============================================================================
    # File Upload
    # ============================================================================
    UPLOAD_DIR: Path = Field(default=Path("./data/uploads"), env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=500 * 1024 * 1024, env="MAX_FILE_SIZE")  # 500MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".jpg", ".jpeg", ".png"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # ============================================================================
    # Vector Store
    # ============================================================================
    VECTOR_STORE_DIR: Path = Field(default=Path("./data/vector_store"), env="VECTOR_STORE_DIR")
    MAX_VECTORS_PER_USER: int = Field(default=100000, env="MAX_VECTORS_PER_USER")
    
    # ============================================================================
    # Cache
    # ============================================================================
    CACHE_DIR: Path = Field(default=Path("./data/cache"), env="CACHE_DIR")
    CACHE_TTL: int = Field(default=7 * 24 * 3600, env="CACHE_TTL")
    
    # ============================================================================
    # Authentication
    # ============================================================================
    JWT_SECRET: str = Field(default="change-this-secret-in-production", env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRES_IN: int = Field(default=7 * 24 * 3600, env="JWT_EXPIRES_IN")
    BCRYPT_ROUNDS: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    # ============================================================================
    # Rate Limiting
    # ============================================================================
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=60, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(default=60, env="RATE_LIMIT_PERIOD")
    
    # ============================================================================
    # Cost Control
    # ============================================================================
    DAILY_BUDGET_PER_USER: float = Field(default=0.10, env="DAILY_BUDGET_PER_USER")
    MAX_TOKENS_PER_QUERY: int = Field(default=50000, env="MAX_TOKENS_PER_QUERY")
    DEEPSEEK_MAX_TOKENS: int = 50000
    WARN_AT_COST: float = Field(default=0.01, env="WARN_AT_COST")
    
    # ============================================================================
    # DeepSeek Pricing
    # ============================================================================
    DEEPSEEK_INPUT_COST_PER_MILLION: float = 0.14
    DEEPSEEK_OUTPUT_COST_PER_MILLION: float = 0.28
    
    # ============================================================================
    # Conversation Memory
    # ============================================================================
    MAX_CONVERSATION_MESSAGES: int = Field(default=1000, env="MAX_CONVERSATION_MESSAGES")
    CONVERSATION_SUMMARY_THRESHOLD: int = Field(default=100, env="CONVERSATION_SUMMARY_THRESHOLD")
    
    # ============================================================================
    # Free APIs
    # ============================================================================
    WIKIPEDIA_USER_AGENT: str = Field(
        default="DarkmoorAI/1.0 (contact@darkmoor.ai)",
        env="WIKIPEDIA_USER_AGENT"
    )
    
    # ============================================================================
    # Email (SMTP)
    # ============================================================================
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASS: Optional[str] = Field(default=None, env="SMTP_PASS")
    EMAIL_FROM: Optional[str] = Field(default="noreply@darkmoor.ai", env="EMAIL_FROM")
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    SMTP_FROM_NAME: str = Field(default="DarkmoorAI", env="SMTP_FROM_NAME")
    
    # ============================================================================
    # Stripe (optional)
    # ============================================================================
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    # ============================================================================
    # Slack, GitHub, SendGrid (optional)
    # ============================================================================
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    SLACK_WEBHOOK_TOKEN: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_TOKEN")
    GITHUB_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="GITHUB_WEBHOOK_SECRET")
    SENDGRID_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="SENDGRID_WEBHOOK_SECRET")
    
    # ============================================================================
    # Monitoring
    # ============================================================================
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    class Config:
        """Pydantic settings config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Create global config instance
config = Config()

# Create directories
config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
(config.UPLOAD_DIR / "temp").mkdir(exist_ok=True)
config.VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
config.CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Print configuration summary
if config.ENV == "development":
    print("\n" + "="*60)
    print("🧠 DARKMOORAI BACKEND CONFIGURATION")
    print("="*60)
    print(f"Environment: {config.ENV}")
    print(f"Debug: {config.DEBUG}")
    print(f"Server: http://{config.HOST}:{config.PORT}")
    print(f"DeepSeek API: {'✅ Configured' if config.DEEPSEEK_API_KEY else '❌ Not configured'}")
    if config.DEEPSEEK_API_KEY:
        print(f"🔑 API KEY from config: {config.DEEPSEEK_API_KEY[:10]}...{config.DEEPSEEK_API_KEY[-4:]}")
    print(f"JWT Secret: {'✅ Set' if config.JWT_SECRET != 'change-this-secret-in-production' else '⚠️ Using default'}")
    print(f"Max File Size: {config.MAX_FILE_SIZE / 1024 / 1024:.0f}MB")
    print(f"Max Tokens: {config.MAX_TOKENS_PER_QUERY:,}")
    print(f"Max Messages: {config.MAX_CONVERSATION_MESSAGES}")
    print(f"SMTP: {'✅ Configured' if config.SMTP_HOST else '❌ Not configured (emails will print to console)'}")
    print("="*60 + "\n")