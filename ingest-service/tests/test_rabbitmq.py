import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.rabbitmq import RabbitMQClient
import aio_pika


@pytest.mark.asyncio
async def test_rabbitmq_connect_success():
    """Test successful RabbitMQ connection."""
    client = RabbitMQClient()
    
    # Mock aio_pika components
    mock_connection = AsyncMock()
    mock_connection.is_closed = False
    
    mock_channel = AsyncMock()
    mock_exchange = AsyncMock()
    mock_queue = AsyncMock()
    
    with patch('app.rabbitmq.aio_pika.connect_robust', return_value=mock_connection) as mock_connect:
        mock_connection.channel.return_value = mock_channel
        mock_channel.declare_exchange.return_value = mock_exchange
        mock_channel.declare_queue.return_value = mock_queue
        
        await client.connect()
        
        assert client.connection is not None
        assert client.channel is not None
        assert client.exchange is not None
        mock_connect.assert_called_once()


@pytest.mark.asyncio
async def test_rabbitmq_disconnect():
    """Test RabbitMQ disconnection."""
    client = RabbitMQClient()
    
    mock_connection = AsyncMock()
    mock_connection.is_closed = False
    client.connection = mock_connection
    
    await client.disconnect()
    
    mock_connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_rabbitmq_publish_message():
    """Test publishing message to RabbitMQ."""
    client = RabbitMQClient()
    
    mock_exchange = AsyncMock()
    client.exchange = mock_exchange
    
    message = {"event_type": "test", "data": {"key": "value"}}
    
    await client.publish_message(message, routing_key="webhook.test")
    
    mock_exchange.publish.assert_called_once()


@pytest.mark.asyncio
async def test_rabbitmq_publish_message_not_connected():
    """Test publishing message when not connected."""
    client = RabbitMQClient()
    
    with pytest.raises(RuntimeError, match="RabbitMQ client is not connected"):
        await client.publish_message({"test": "data"})


def test_rabbitmq_is_connected():
    """Test connection status check."""
    client = RabbitMQClient()
    
    # Not connected
    assert client.is_connected() is False
    
    # Mock connected state
    mock_connection = MagicMock()
    mock_connection.is_closed = False
    client.connection = mock_connection
    
    assert client.is_connected() is True
    
    # Mock closed connection
    mock_connection.is_closed = True
    assert client.is_connected() is False
