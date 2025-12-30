from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = "ingest-service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # RabbitMQ settings
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_queue: str = "webhook_events"
    rabbitmq_exchange: str = "webhook_exchange"
    
    # Prometheus settings
    metrics_enabled: bool = True
    
    # Validation settings
    max_payload_size: int = 1048576  # 1MB in bytes
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
