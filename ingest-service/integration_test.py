#!/usr/bin/env python3
"""
Integration test script for the Ingest Service.
Tests the service endpoints without requiring RabbitMQ.
"""

import sys
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Add the app directory to the path
sys.path.insert(0, '/home/runner/work/integration-platform-microservices/integration-platform-microservices/ingest-service')

from app.main import app


def test_service():
    """Run integration tests for the service."""
    
    print("=" * 60)
    print("Ingest Service Integration Tests")
    print("=" * 60)
    print()
    
    # Mock RabbitMQ client
    with patch('app.routes.rabbitmq_client') as mock_rabbitmq:
        mock_rabbitmq.is_connected.return_value = True
        mock_rabbitmq.publish_message = AsyncMock()
        
        client = TestClient(app)
        
        # Test 1: Root endpoint
        print("Test 1: Root endpoint")
        response = client.get("/")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("  ✅ PASSED\n")
        
        # Test 2: Health check
        print("Test 2: Health check endpoint")
        response = client.get("/health")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("  ✅ PASSED\n")
        
        # Test 3: Webhook submission
        print("Test 3: Webhook submission")
        webhook_data = {
            "event_type": "user.created",
            "source": "auth-service",
            "data": {
                "user_id": "12345",
                "email": "test@example.com",
                "name": "Test User"
            },
            "correlation_id": "test-correlation-123"
        }
        response = client.post("/webhook", json=webhook_data)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 202
        assert response.json()["success"] is True
        assert "event_id" in response.json()
        print("  ✅ PASSED\n")
        
        # Test 4: Validation - Invalid event type
        print("Test 4: Validation - Invalid event type")
        invalid_data = {
            "event_type": "user@created",  # Invalid character
            "source": "auth-service",
            "data": {"test": "data"}
        }
        response = client.post("/webhook", json=invalid_data)
        print(f"  Status: {response.status_code}")
        assert response.status_code == 422
        print("  ✅ PASSED\n")
        
        # Test 5: Validation - Missing required field
        print("Test 5: Validation - Missing required field")
        incomplete_data = {
            "event_type": "user.created",
            "source": "auth-service"
            # Missing 'data' field
        }
        response = client.post("/webhook", json=incomplete_data)
        print(f"  Status: {response.status_code}")
        assert response.status_code == 422
        print("  ✅ PASSED\n")
        
        # Test 6: Metrics endpoint
        print("Test 6: Metrics endpoint")
        response = client.get("/metrics")
        print(f"  Status: {response.status_code}")
        print(f"  Content Type: {response.headers.get('content-type')}")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        print("  ✅ PASSED\n")
        
        # Test 7: Middleware - Content type validation
        print("Test 7: Middleware - Content type validation")
        response = client.post(
            "/webhook",
            data="not json",
            headers={"content-type": "text/plain"}
        )
        print(f"  Status: {response.status_code}")
        assert response.status_code == 415
        print("  ✅ PASSED\n")
    
    print("=" * 60)
    print("All integration tests passed! ✅")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_service()
        print("\n✅ Service is ready for deployment!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
