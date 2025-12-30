from fastapi import APIRouter, HTTPException, status
from app.models import WebhookPayload, WebhookResponse, HealthResponse
from app.rabbitmq import rabbitmq_client
from app.metrics import (
    webhook_payload_size_bytes,
    rabbitmq_published_messages_total,
    rabbitmq_connection_status
)
from app.config import settings
import uuid
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook", response_model=WebhookResponse, status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(payload: WebhookPayload):
    """
    Receive and process webhook events.
    
    The webhook payload is validated, assigned a unique event ID,
    and published to RabbitMQ for asynchronous processing.
    """
    try:
        # Generate unique event ID
        event_id = str(uuid.uuid4())
        
        # Prepare message for RabbitMQ
        message = {
            "event_id": event_id,
            "event_type": payload.event_type,
            "source": payload.source,
            "data": payload.data,
            "timestamp": payload.timestamp.isoformat() if payload.timestamp else None,
            "correlation_id": payload.correlation_id
        }
        
        # Track payload size
        message_size = len(json.dumps(message))
        webhook_payload_size_bytes.labels(endpoint="/webhook").observe(message_size)
        
        # Publish to RabbitMQ
        routing_key = f"webhook.{payload.event_type}"
        await rabbitmq_client.publish_message(message, routing_key=routing_key)
        
        rabbitmq_published_messages_total.labels(
            routing_key=routing_key,
            status="success"
        ).inc()
        
        logger.info(f"Webhook received and published: event_id={event_id}, event_type={payload.event_type}")
        
        return WebhookResponse(
            success=True,
            message="Webhook received and queued for processing",
            event_id=event_id
        )
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        rabbitmq_published_messages_total.labels(
            routing_key="webhook.error",
            status="error"
        ).inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns the service status and RabbitMQ connection status.
    """
    rabbitmq_connected = rabbitmq_client.is_connected()
    rabbitmq_connection_status.set(1 if rabbitmq_connected else 0)
    
    return HealthResponse(
        status="healthy" if rabbitmq_connected else "degraded",
        version=settings.app_version,
        rabbitmq_connected=rabbitmq_connected
    )


@router.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }
