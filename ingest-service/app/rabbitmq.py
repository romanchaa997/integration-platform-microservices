import aio_pika
import json
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """RabbitMQ client for publishing webhook events."""
    
    def __init__(self):
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
    
    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            connection_url = f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_password}@{settings.rabbitmq_host}:{settings.rabbitmq_port}/"
            self.connection = await aio_pika.connect_robust(connection_url)
            self.channel = await self.connection.channel()
            
            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                settings.rabbitmq_exchange,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            # Declare queue
            queue = await self.channel.declare_queue(
                settings.rabbitmq_queue,
                durable=True
            )
            
            # Bind queue to exchange
            await queue.bind(self.exchange, routing_key="webhook.*")
            
            logger.info(f"Connected to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def disconnect(self):
        """Close RabbitMQ connection."""
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    async def publish_message(self, message: dict, routing_key: str = "webhook.received"):
        """Publish a message to RabbitMQ."""
        if not self.exchange:
            raise RuntimeError("RabbitMQ client is not connected")
        
        try:
            message_body = json.dumps(message).encode()
            
            await self.exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type="application/json"
                ),
                routing_key=routing_key
            )
            
            logger.debug(f"Published message to RabbitMQ with routing key: {routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish message to RabbitMQ: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if connected to RabbitMQ."""
        return self.connection is not None and not self.connection.is_closed


# Global RabbitMQ client instance
rabbitmq_client = RabbitMQClient()
