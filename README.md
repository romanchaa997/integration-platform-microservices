# Integration Platform Microservices

Parallel microservices integration platform: Ingest, Normalize, Execute, Writer, AI enrichment, monitoring, K8s scaling, and SaaS layer

## Architecture

This platform consists of multiple microservices designed to work together for processing integration workflows at scale.

## Microservices

### 🔵 Ingest Service

**Status**: ✅ Implemented

A high-performance FastAPI microservice for ingesting webhook events with RabbitMQ queue integration.

**Features**:
- FastAPI framework with async request handling
- Webhook endpoints for event ingestion
- RabbitMQ integration for reliable message queuing
- Validation middleware (payload size, content type)
- Prometheus metrics for monitoring
- Comprehensive unit tests (24 tests)
- Docker support with docker-compose

**Tech Stack**: Python 3.11+, FastAPI, RabbitMQ, Prometheus

📖 [Full Documentation](./ingest-service/README.md)

### 🔶 Normalize Service

**Status**: 🚧 Coming Soon

### 🔷 Execute Service

**Status**: 🚧 Coming Soon

### 🟢 Writer Service

**Status**: 🚧 Coming Soon

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. **Start all services**:
```bash
./start.sh
# Or manually:
docker compose up -d
```

2. **Access the services**:
   - Ingest Service: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672 (guest/guest)
   - Prometheus: http://localhost:9090

3. **Test the webhook endpoint**:
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "order.created",
    "source": "order-service",
    "data": {"order_id": "12345"}
  }'
```

4. **Stop services**:
```bash
docker compose down
```

### Local Development

See individual service README files for local development instructions.

## Project Structure

```
.
├── ingest-service/          # Webhook ingestion service
│   ├── app/                 # Application code
│   ├── tests/               # Unit tests
│   ├── Dockerfile           # Container definition
│   ├── requirements.txt     # Python dependencies
│   └── README.md            # Service documentation
├── docker-compose.yml       # Multi-service orchestration
├── prometheus.yml           # Monitoring configuration
└── start.sh                 # Quick start script
```

## Monitoring

### Prometheus Metrics

Access Prometheus at http://localhost:9090 to view metrics:

- `webhook_requests_total`: Total webhook requests
- `webhook_request_duration_seconds`: Request latency
- `webhook_payload_size_bytes`: Payload sizes
- `rabbitmq_published_messages_total`: Messages published
- `rabbitmq_connection_status`: RabbitMQ health

### RabbitMQ Management

Access RabbitMQ Management UI at http://localhost:15672:
- Username: `guest`
- Password: `guest`

View queues, exchanges, and message rates.

## Development

### Adding a New Service

1. Create a new directory for the service
2. Implement the service following the existing patterns
3. Add comprehensive tests
4. Update docker-compose.yml
5. Document in service README
6. Update this main README

### Testing

Each service has its own test suite. To run tests for a specific service:

```bash
cd <service-name>
pip install -r requirements.txt
pytest
```

### Code Quality

- Write comprehensive unit tests
- Follow Python best practices (PEP 8)
- Use type hints
- Implement proper error handling
- Add appropriate logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## License

See LICENSE file for details.
