"""Pytest configuration and fixtures."""
import os
from unittest.mock import MagicMock

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Set environment variables for testing."""
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "test-access-key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret-key"
    os.environ["DEBUG"] = "true"
    os.environ["MAX_FILE_SIZE_MB"] = "25"


@pytest.fixture
def mock_bedrock_client():
    """Mock boto3 bedrock client."""
    client = MagicMock()
    
    # Mock invoke_agent response
    client.invoke_agent.return_value = {
        "completion": [
            {
                "chunk": {
                    "bytes": b"This is a test agent response with analysis insights."
                }
            }
        ]
    }
    
    return client
