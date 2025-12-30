from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from pythonjsonlogger import jsonlogger

from app.config import settings
from app.routes import router
from app.rabbitmq import rabbitmq_client
from app.middleware import ValidationMiddleware, LoggingMiddleware
from app.metrics import metrics_endpoint, MetricsMiddleware

# Configure logging
def setup_logging():
    """Configure JSON logging for the application."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if not settings.debug else logging.DEBUG)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # JSON formatter
    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)


setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    try:
        await rabbitmq_client.connect()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ during startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await rabbitmq_client.disconnect()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Ingest service for receiving and queuing webhook events",
    lifespan=lifespan
)

# Add middleware
if settings.metrics_enabled:
    app.add_middleware(MetricsMiddleware)

app.add_middleware(ValidationMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routes
app.include_router(router)

# Add metrics endpoint
if settings.metrics_enabled:
    @app.get("/metrics")
    async def metrics():
        return await metrics_endpoint()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
