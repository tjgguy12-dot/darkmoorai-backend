"""
CORS Middleware
Handle Cross-Origin Resource Sharing
"""

from fastapi.middleware.cors import CORSMiddleware
from app.config import config

# This is configured directly in main.py
# This file exists for documentation and organization

"""
CORS Configuration:
- Allows requests from configured origins
- Supports credentials (cookies, auth headers)
- Allows all standard methods
- Allows all headers

Configured in app/main.py:
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""