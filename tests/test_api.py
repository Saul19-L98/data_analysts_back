"""Integration tests for the ingest endpoint."""
import io

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app
    return TestClient(app)


class TestIngestEndpoint:
    """Test suite for the ingest API endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_ingest_missing_file(self, client):
        """Test ingest without file returns 422."""
        response = client.post(
            "/api/v1/ingest",
            data={"message": "test", "agent_id": "test-agent", "agent_alias_id": "test-alias"},
        )
        assert response.status_code == 422

    def test_ingest_missing_agent_id(self, client):
        """Test ingest without agent_id returns 422."""
        csv_content = b"col1,col2\nval1,val2"
        files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        data = {"message": "test", "agent_alias_id": "test-alias"}

        response = client.post("/api/v1/ingest", files=files, data=data)
        assert response.status_code == 422

    def test_ingest_missing_agent_alias_id(self, client):
        """Test ingest without agent_alias_id returns 422."""
        csv_content = b"col1,col2\nval1,val2"
        files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        data = {"message": "test", "agent_id": "test-agent"}

        response = client.post("/api/v1/ingest", files=files, data=data)
        assert response.status_code == 422

    def test_ingest_empty_agent_id(self, client):
        """Test ingest with empty agent_id returns 422."""
        csv_content = b"col1,col2\nval1,val2"
        files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        data = {"message": "test", "agent_id": "  ", "agent_alias_id": "test-alias"}

        response = client.post("/api/v1/ingest", files=files, data=data)
        assert response.status_code == 422

    def test_docs_accessible(self, client):
        """Test API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_accessible(self, client):
        """Test alternative API documentation is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
