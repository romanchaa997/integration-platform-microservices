# Ingest Service

A high-performance FastAPI microservice for ingesting webhook events with RabbitMQ queue integration, validation middleware, async request handling, and Prometheus metrics.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Webhook Endpoints**: RESTful API for receiving webhook events
- **RabbitMQ Integration**: Asynchronous message queue for reliable event processing
- **Validation Middleware**: Request validation including payload size and content type checks
- **Async Request Handling**: Non-blocking I/O for high throughput
- **Prometheus Metrics**: Built-in metrics for monitoring and observability
- **Docker Support**: Containerized deployment with docker-compose
- **Comprehensive Testing**: Unit tests with pytest
- **JSON Logging**: Structured logging for better observability

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ HTTP POST /webhook
       ▼
┌─────────────────────────────┐
│   Validation Middleware     │
│  - Payload size check       │
│  - Content type validation  │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│   FastAPI Application       │
│  - Request validation       │
│  - Async handling           │
│  - Metrics collection       │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│   RabbitMQ Publisher        │
│  - Queue: webhook_events    │
│  - Exchange: webhook_exchange│
└─────────────────────────────┘
```

## API Endpoints

### POST /webhook
Receive and queue webhook events for processing.

**Request Body:**
```json
{
  "event_type": "user.created",
  "source": "auth-service",
  "data": {
    "user_id": "123",
    "email": "user@example.com"
  },
  "correlation_id": "optional-correlation-id"
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "message": "Webhook received and queued for processing",
  "event_id": "uuid-generated-event-id",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /health
Health check endpoint for monitoring service and RabbitMQ status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "rabbitmq_connected": true,
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /
Service information endpoint.

**Response (200 OK):**
```json
{
  "service": "ingest-service",
  "version": "1.0.0",
  "status": "running"
}
```

### GET /metrics
Prometheus metrics endpoint for monitoring.

**Metrics Available:**
- `webhook_requests_total`: Total number of webhook requests
- `webhook_request_duration_seconds`: Request duration histogram
- `webhook_payload_size_bytes`: Payload size histogram
- `rabbitmq_published_messages_total`: Total messages published to RabbitMQ
- `rabbitmq_connection_status`: RabbitMQ connection status
- `validation_errors_total`: Total validation errors

## Installation

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- RabbitMQ (if running locally without Docker)

### Local Development (with Docker Compose)

1. **Start all services:**
```bash
docker-compose up -d
```

This will start:
- Ingest service on port 8000
- RabbitMQ on ports 5672 (AMQP) and 15672 (Management UI)
- Prometheus on port 9090

2. **View logs:**
```bash
docker-compose logs -f ingest-service
```

3. **Stop services:**
```bash
docker-compose down
```

### Local Development (without Docker)

1. **Create virtual environment:**
```bash
cd ingest-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USER=guest
export RABBITMQ_PASSWORD=guest
export DEBUG=true
```

4. **Run the application:**
```bash
python -m app.main
# Or with uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

Configuration is managed through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | ingest-service | Application name |
| `APP_VERSION` | 1.0.0 | Application version |
| `DEBUG` | false | Enable debug mode |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `RABBITMQ_HOST` | rabbitmq | RabbitMQ hostname |
| `RABBITMQ_PORT` | 5672 | RabbitMQ port |
| `RABBITMQ_USER` | guest | RabbitMQ username |
| `RABBITMQ_PASSWORD` | guest | RabbitMQ password |
| `RABBITMQ_QUEUE` | webhook_events | Queue name |
| `RABBITMQ_EXCHANGE` | webhook_exchange | Exchange name |
| `METRICS_ENABLED` | true | Enable Prometheus metrics |
| `MAX_PAYLOAD_SIZE` | 1048576 | Maximum payload size in bytes (1MB) |

## Testing

### Run all tests:
```bash
cd ingest-service
pytest
```

### Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_routes.py
```

### Run tests with verbose output:
```bash
pytest -v
```

## Monitoring

### Prometheus
Access Prometheus UI at http://localhost:9090

Example queries:
- Request rate: `rate(webhook_requests_total[5m])`
- Average request duration: `rate(webhook_request_duration_seconds_sum[5m]) / rate(webhook_request_duration_seconds_count[5m])`
- RabbitMQ connection status: `rabbitmq_connection_status`

### RabbitMQ Management
Access RabbitMQ Management UI at http://localhost:15672
- Username: guest
- Password: guest

## Example Usage

### Send a webhook event:
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "order.created",
    "source": "order-service",
    "data": {
      "order_id": "12345",
      "customer_id": "67890",
      "total": 99.99
    },
    "correlation_id": "order-12345"
  }'
```

### Check service health:
```bash
curl http://localhost:8000/health
```

### View metrics:
```bash
curl http://localhost:8000/metrics
```

## Development

### Code Structure
```
ingest-service/
├── app/
│   ├── __init__.py
│   ├── main.py           # Application entry point
│   ├── config.py         # Configuration management
│   ├── models.py         # Pydantic models
│   ├── routes.py         # API routes
│   ├── rabbitmq.py       # RabbitMQ client
│   ├── middleware.py     # Custom middleware
│   └── metrics.py        # Prometheus metrics
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Test fixtures
│   ├── test_models.py
│   ├── test_routes.py
│   ├── test_rabbitmq.py
│   └── test_middleware.py
├── Dockerfile
└── requirements.txt
```

### Adding New Endpoints
1. Define route in `app/routes.py`
2. Add corresponding tests in `tests/test_routes.py`
3. Update metrics if needed in `app/metrics.py`
4. Document the endpoint in this README

### Best Practices
- Always use async/await for I/O operations
- Add appropriate metrics for new endpoints
- Write tests for new features
- Follow Pydantic validation patterns
- Use structured logging (JSON format)

## Troubleshooting

### RabbitMQ Connection Issues
- Check RabbitMQ is running: `docker-compose ps`
- Check logs: `docker-compose logs rabbitmq`
- Verify connection settings in environment variables

### Application Not Starting
- Check all required environment variables are set
- Verify Python version (3.11+ required)
- Check for port conflicts on 8000

### Tests Failing
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Run tests in isolation: `pytest tests/test_routes.py -v`
- Check for mock issues in test fixtures

## License

See LICENSE file in the repository root.
