#!/bin/bash
# Quick Start Script for Ingest Service

echo "=========================================="
echo "FastAPI Ingest Service - Quick Start"
echo "=========================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker is available"
echo ""

# Check if Docker Compose is available
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose is available"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose first."
    exit 1
fi

echo ""
echo "Starting services with Docker Compose..."
echo ""

# Start services
docker compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Services Started Successfully!"
    echo "=========================================="
    echo ""
    echo "📊 Access Points:"
    echo "   - Ingest Service:       http://localhost:8000"
    echo "   - API Documentation:    http://localhost:8000/docs"
    echo "   - Health Check:         http://localhost:8000/health"
    echo "   - Metrics:              http://localhost:8000/metrics"
    echo "   - RabbitMQ Management:  http://localhost:15672 (guest/guest)"
    echo "   - Prometheus:           http://localhost:9090"
    echo ""
    echo "📝 Example webhook request:"
    echo '   curl -X POST http://localhost:8000/webhook \'
    echo '     -H "Content-Type: application/json" \'
    echo '     -d '"'"'{'
    echo '       "event_type": "test.event",'
    echo '       "source": "test-source",'
    echo '       "data": {"message": "Hello World"}'
    echo '     }'"'"
    echo ""
    echo "🛑 To stop services: docker compose down"
    echo "📋 To view logs: docker compose logs -f ingest-service"
    echo ""
else
    echo "❌ Failed to start services"
    exit 1
fi
