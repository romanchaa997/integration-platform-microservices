import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.rabbitmq import rabbitmq_client


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_rabbitmq():
    """Mock RabbitMQ client fixture."""
    with patch('app.routes.rabbitmq_client') as mock:
        mock.is_connected.return_value = True
        mock.publish_message = AsyncMock()
        yield mock


@pytest.fixture(autouse=True)
def reset_rabbitmq_client():
    """Reset RabbitMQ client after each test."""
    yield
    # Clean up any connections
    if rabbitmq_client.connection:
        rabbitmq_client.connection = None
    if rabbitmq_client.channel:
        rabbitmq_client.channel = None
    if rabbitmq_client.exchange:
        rabbitmq_client.exchange = None
