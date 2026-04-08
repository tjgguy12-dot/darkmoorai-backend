"""
Production configuration overrides for Render
"""
from app.config import config

# Override for production
if config.ENV == "production":
    # Use PostgreSQL (Render provides DATABASE_URL)
    # The DATABASE_URL from Render already has the correct format
    pass