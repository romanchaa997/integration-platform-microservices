from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
from datetime import datetime


class WebhookPayload(BaseModel):
    """Model for incoming webhook payloads."""
    
    event_type: str = Field(..., min_length=1, max_length=100, description="Type of webhook event")
    source: str = Field(..., min_length=1, max_length=100, description="Source system identifier")
    data: Dict[str, Any] = Field(..., description="Event payload data")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Event timestamp")
    correlation_id: Optional[str] = Field(None, max_length=100, description="Correlation ID for tracking")
    
    @field_validator('event_type')
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validate event type format."""
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError('event_type must contain only alphanumeric characters, underscores, and dots')
        return v
    
    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate source format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('source must contain only alphanumeric characters, underscores, and hyphens')
        return v


class WebhookResponse(BaseModel):
    """Model for webhook response."""
    
    success: bool = Field(..., description="Whether the webhook was successfully received")
    message: str = Field(..., description="Response message")
    event_id: Optional[str] = Field(None, description="Generated event ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthResponse(BaseModel):
    """Model for health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    rabbitmq_connected: bool = Field(..., description="RabbitMQ connection status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
