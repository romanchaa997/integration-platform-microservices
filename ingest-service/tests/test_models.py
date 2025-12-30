import pytest
from app.models import WebhookPayload, WebhookResponse, HealthResponse
from pydantic import ValidationError
from datetime import datetime


def test_webhook_payload_valid():
    """Test valid webhook payload."""
    payload = WebhookPayload(
        event_type="user.created",
        source="auth-service",
        data={"user_id": "123", "email": "test@example.com"}
    )
    
    assert payload.event_type == "user.created"
    assert payload.source == "auth-service"
    assert payload.data == {"user_id": "123", "email": "test@example.com"}
    assert isinstance(payload.timestamp, datetime)


def test_webhook_payload_with_optional_fields():
    """Test webhook payload with optional fields."""
    payload = WebhookPayload(
        event_type="order.completed",
        source="order-service",
        data={"order_id": "456"},
        correlation_id="corr-123"
    )
    
    assert payload.correlation_id == "corr-123"
    assert isinstance(payload.timestamp, datetime)


def test_webhook_payload_invalid_event_type():
    """Test webhook payload with invalid event type."""
    with pytest.raises(ValidationError) as exc_info:
        WebhookPayload(
            event_type="user@created",  # Invalid character
            source="auth-service",
            data={"user_id": "123"}
        )
    
    assert "event_type" in str(exc_info.value)


def test_webhook_payload_invalid_source():
    """Test webhook payload with invalid source."""
    with pytest.raises(ValidationError) as exc_info:
        WebhookPayload(
            event_type="user.created",
            source="auth@service",  # Invalid character
            data={"user_id": "123"}
        )
    
    assert "source" in str(exc_info.value)


def test_webhook_payload_missing_required_fields():
    """Test webhook payload with missing required fields."""
    with pytest.raises(ValidationError) as exc_info:
        WebhookPayload(
            event_type="user.created",
            source="auth-service"
            # Missing data field
        )
    
    assert "data" in str(exc_info.value)


def test_webhook_response():
    """Test webhook response model."""
    response = WebhookResponse(
        success=True,
        message="Webhook received",
        event_id="evt-123"
    )
    
    assert response.success is True
    assert response.message == "Webhook received"
    assert response.event_id == "evt-123"
    assert isinstance(response.timestamp, datetime)


def test_health_response():
    """Test health response model."""
    response = HealthResponse(
        status="healthy",
        version="1.0.0",
        rabbitmq_connected=True
    )
    
    assert response.status == "healthy"
    assert response.version == "1.0.0"
    assert response.rabbitmq_connected is True
    assert isinstance(response.timestamp, datetime)
