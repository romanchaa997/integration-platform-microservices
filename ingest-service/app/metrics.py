from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response
import time

# Define metrics
webhook_requests_total = Counter(
    'webhook_requests_total',
    'Total number of webhook requests',
    ['method', 'endpoint', 'status']
)

webhook_request_duration_seconds = Histogram(
    'webhook_request_duration_seconds',
    'Webhook request duration in seconds',
    ['method', 'endpoint']
)

webhook_payload_size_bytes = Histogram(
    'webhook_payload_size_bytes',
    'Webhook payload size in bytes',
    ['endpoint']
)

rabbitmq_published_messages_total = Counter(
    'rabbitmq_published_messages_total',
    'Total number of messages published to RabbitMQ',
    ['routing_key', 'status']
)

rabbitmq_connection_status = Gauge(
    'rabbitmq_connection_status',
    'RabbitMQ connection status (1=connected, 0=disconnected)'
)

validation_errors_total = Counter(
    'validation_errors_total',
    'Total number of validation errors',
    ['error_type']
)


async def metrics_endpoint() -> Response:
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


class MetricsMiddleware:
    """Middleware to collect request metrics."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        method = request.method
        path = request.url.path
        
        # Skip metrics endpoint itself
        if path == "/metrics":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        # Track response status
        status_code = 200
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.time() - start_time
            webhook_requests_total.labels(method=method, endpoint=path, status=status_code).inc()
            webhook_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)
