"""
Unit tests for PCD-Lite main application
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "PCD-Lite API" in data["message"]

def test_search_endpoint():
    """Test search endpoint with basic query"""
    search_data = {
        "query": "find comedy movies",
        "query_type": "text",
        "session_id": "test-session-123"
    }
    
    response = client.post("/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "request_id" in data
    assert "session_id" in data
    assert "variant" in data
    assert "parsed_filters" in data
    assert "recommendations" in data
    assert "total_results" in data
    assert "processing_time_ms" in data
    
    # Check variant is valid
    assert data["variant"] in ["A", "B"]
    
    # Check recommendations are returned
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0

def test_search_voice_query():
    """Test search endpoint with voice query"""
    search_data = {
        "query": "find funny movies with tom hanks",
        "query_type": "voice",
        "session_id": "test-session-456"
    }
    
    response = client.post("/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check voice processing was applied
    assert "debug_info" in data
    assert data["debug_info"]["query_type"] == "voice"

def test_search_complex_query():
    """Test search endpoint with complex query"""
    search_data = {
        "query": "find action movies shorter than 120 minutes with tom cruise",
        "query_type": "text",
        "session_id": "test-session-789"
    }
    
    response = client.post("/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check parsed filters
    filters = data["parsed_filters"]
    assert "genres" in filters
    assert "actors" in filters
    assert "runtime_max" in filters
    assert filters["runtime_max"] == 120

def test_click_tracking():
    """Test click tracking endpoint"""
    click_data = {
        "request_id": "test-request-123",
        "session_id": "test-session-123",
        "movie_id": 1,
        "position": 1,
        "variant": "A"
    }
    
    response = client.post("/click", json=click_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "message" in data

def test_debug_endpoint():
    """Test debug endpoint"""
    # First make a search to populate debug info
    search_data = {
        "query": "test query",
        "query_type": "text",
        "session_id": "debug-session-123"
    }
    client.post("/search", json=search_data)
    
    # Then check debug info
    response = client.get("/debug/last-query")
    assert response.status_code == 200
    data = response.json()
    assert "last_query" in data
    assert "parsed_filters" in data
    assert "variant" in data

def test_analytics_endpoint():
    """Test analytics endpoint"""
    response = client.get("/analytics?days=7")
    assert response.status_code == 200
    data = response.json()
    assert "period_days" in data
    assert "metrics" in data
    assert data["period_days"] == 7

def test_variant_performance_endpoint():
    """Test variant performance endpoint"""
    response = client.get("/analytics/variants?days=7")
    assert response.status_code == 200
    data = response.json()
    assert "period_days" in data
    assert "performance" in data
    assert "variant_a" in data["performance"]
    assert "variant_b" in data["performance"]

def test_catalog_endpoint():
    """Test catalog endpoint"""
    response = client.get("/catalog?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "total_movies" in data
    assert "returned_movies" in data
    assert "movies" in data
    assert len(data["movies"]) <= 5

def test_voice_suggestions_endpoint():
    """Test voice suggestions endpoint"""
    response = client.get("/voice/suggestions?partial_query=comedy")
    assert response.status_code == 200
    data = response.json()
    assert "partial_query" in data
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)

def test_session_events_endpoint():
    """Test session events endpoint"""
    session_id = "test-session-events-123"
    response = client.get(f"/session/{session_id}/events")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "event_count" in data
    assert "events" in data

def test_fault_injection():
    """Test fault injection"""
    search_data = {
        "query": "test error handling",
        "query_type": "text",
        "session_id": "error-session-123"
    }
    
    response = client.post("/search?fail=1", json=search_data)
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Simulated server error" in data["detail"]

def test_search_without_session_id():
    """Test search without session ID (should generate one)"""
    search_data = {
        "query": "find drama movies",
        "query_type": "text"
    }
    
    response = client.post("/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_id"] is not None

def test_search_without_request_id():
    """Test search without request ID (should generate one)"""
    search_data = {
        "query": "find action movies",
        "query_type": "text",
        "session_id": "test-session-no-request-id"
    }
    
    response = client.post("/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["request_id"] is not None

def test_invalid_query_type():
    """Test search with invalid query type"""
    search_data = {
        "query": "find comedy movies",
        "query_type": "invalid",
        "session_id": "test-session-invalid-type"
    }
    
    response = client.post("/search", json=search_data)
    # Should still work as it defaults to text
    assert response.status_code == 200

def test_empty_query():
    """Test search with empty query"""
    search_data = {
        "query": "",
        "query_type": "text",
        "session_id": "test-session-empty"
    }
    
    response = client.post("/search", json=search_data)
    assert response.status_code == 200
    data = response.json()
    # Should return some results even with empty query
    assert "recommendations" in data
