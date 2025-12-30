from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.config import settings
from app.metrics import validation_errors_total
import logging

logger = logging.getLogger(__name__)


class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation."""
    
    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                content_length_int = int(content_length)
                if content_length_int > settings.max_payload_size:
                    validation_errors_total.labels(error_type="payload_too_large").inc()
                    logger.warning(f"Payload too large: {content_length_int} bytes")
                    return JSONResponse(
                        status_code=413,
                        content={
                            "success": False,
                            "message": f"Payload too large. Maximum size is {settings.max_payload_size} bytes"
                        }
                    )
            except ValueError:
                validation_errors_total.labels(error_type="invalid_content_length").inc()
                logger.warning("Invalid content-length header")
        
        # Check content type for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                validation_errors_total.labels(error_type="invalid_content_type").inc()
                logger.warning(f"Invalid content type: {content_type}")
                return JSONResponse(
                    status_code=415,
                    content={
                        "success": False,
                        "message": "Content-Type must be application/json"
                    }
                )
        
        response = await call_next(request)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        logger.info(f"Response status: {response.status_code}")
        return response
