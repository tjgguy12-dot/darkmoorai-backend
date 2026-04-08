"""
API Integration Tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "DarkmoorAI"

def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/api/v1/health/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_not_found():
    """Test 404 handling"""
    response = client.get("/nonexistent")
    assert response.status_code == 404