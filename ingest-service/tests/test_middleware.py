import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    with TestClient(app) as c:
        yield c


def test_validation_middleware_payload_too_large(client):
    """Test validation middleware rejects payloads that are too large."""
    # Create a large payload that exceeds the limit
    large_payload = {
        "event_type": "test.event",
        "source": "test-source",
        "data": {"key": "x" * 2000000}  # Very large data
    }
    
    # Set a custom content-length header to simulate large payload
    headers = {"content-length": "2000000"}
    response = client.post("/webhook", json=large_payload, headers=headers)
    assert response.status_code == 413


def test_validation_middleware_invalid_content_type(client):
    """Test validation middleware rejects invalid content types."""
    response = client.post(
        "/webhook",
        data="not json",
        headers={"content-type": "text/plain"}
    )
    assert response.status_code == 415
    assert "application/json" in response.json()["message"]


def test_validation_middleware_accepts_valid_request(client):
    """Test validation middleware accepts valid requests."""
    from unittest.mock import patch, AsyncMock
    
    with patch('app.routes.rabbitmq_client.publish_message', new_callable=AsyncMock):
        payload = {
            "event_type": "user.created",
            "source": "auth-service",
            "data": {"user_id": "123"}
        }
        
        response = client.post("/webhook", json=payload)
        assert response.status_code == 202


def test_logging_middleware():
    """Test that logging middleware is applied."""
    # This is a basic test to ensure middleware doesn't break the application
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
