import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock, patch


@pytest.fixture
def client():
    """Test client fixture."""
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_endpoint_connected(client):
    """Test health endpoint when RabbitMQ is connected."""
    with patch('app.routes.rabbitmq_client.is_connected', return_value=True):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["rabbitmq_connected"] is True
        assert "version" in data
        assert "timestamp" in data


def test_health_endpoint_disconnected(client):
    """Test health endpoint when RabbitMQ is disconnected."""
    with patch('app.routes.rabbitmq_client.is_connected', return_value=False):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["rabbitmq_connected"] is False


def test_webhook_endpoint_success(client):
    """Test successful webhook submission."""
    with patch('app.routes.rabbitmq_client.publish_message', new_callable=AsyncMock):
        payload = {
            "event_type": "user.created",
            "source": "auth-service",
            "data": {"user_id": "123", "email": "test@example.com"}
        }
        
        response = client.post("/webhook", json=payload)
        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "event_id" in data
        assert "message" in data
        assert "timestamp" in data


def test_webhook_endpoint_invalid_payload(client):
    """Test webhook with invalid payload."""
    payload = {
        "event_type": "user@created",  # Invalid character
        "source": "auth-service",
        "data": {"user_id": "123"}
    }
    
    response = client.post("/webhook", json=payload)
    assert response.status_code == 422  # Validation error


def test_webhook_endpoint_missing_fields(client):
    """Test webhook with missing required fields."""
    payload = {
        "event_type": "user.created",
        "source": "auth-service"
        # Missing data field
    }
    
    response = client.post("/webhook", json=payload)
    assert response.status_code == 422


def test_webhook_endpoint_rabbitmq_error(client):
    """Test webhook when RabbitMQ publish fails."""
    with patch('app.routes.rabbitmq_client.publish_message', 
               new_callable=AsyncMock, 
               side_effect=Exception("RabbitMQ error")):
        payload = {
            "event_type": "user.created",
            "source": "auth-service",
            "data": {"user_id": "123"}
        }
        
        response = client.post("/webhook", json=payload)
        assert response.status_code == 500


def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    # Check for some expected metrics
    assert b"webhook_requests_total" in response.content or b"python_info" in response.content
