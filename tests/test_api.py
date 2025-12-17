"""
Tests for FastAPI endpoints (AgentApiPort, health, ready).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from httpx import Response, HTTPStatusError

from artifact_retrieval_service.models import ArtifactDescriptor, TraceableArtifact
from artifact_retrieval_service.main import app, get_gitlab_client
from artifact_retrieval_service.gitlab_client import GitLabClient, GitLabClientConfig


@pytest.fixture
def mock_gitlab_client():
    """Create a mock GitLabClient."""
    client = AsyncMock(spec=GitLabClient)
    # Make it work as async context manager
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


@pytest.fixture
def client(mock_gitlab_client):
    """Create a test client with mocked GitLabClient."""

    def override_get_gitlab_client():
        return mock_gitlab_client

    app.dependency_overrides[get_gitlab_client] = override_get_gitlab_client
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Tests for /healthz endpoint."""

    def test_health_endpoint_returns_200(self, client):
        """Test that /healthz returns 200 OK."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestReadyEndpoint:
    """Tests for /ready endpoint."""

    def test_ready_endpoint_returns_200(self, client):
        """Test that /ready returns 200 OK."""
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}


class TestAgentApiEndpoint:
    """Tests for AgentApiPort endpoint (POST /api/v1/artifacts)."""

    def test_retrieve_artifact_success(self, client, mock_gitlab_client):
        """Test successful artifact retrieval."""
        mock_artifact = TraceableArtifact(
            artifactId="test-artifact-123",
            mimeType="application/json",
            filePath="/path/to/downloaded/file.json",
        )

        # Mock the internal method since retrieve_artifact uses async context manager
        async def mock_retrieve(descriptor):
            return mock_artifact

        mock_gitlab_client._retrieve_artifact_internal = AsyncMock(return_value=mock_artifact)
        mock_gitlab_client.retrieve_artifact = AsyncMock(return_value=mock_artifact)

        request_data = {
            "repository": "my-org/my-repo",
            "artifactPath": "path/to/artifact.json",
            "versionSelector": "v1.0.0",
        }

        response = client.post("/api/v1/artifacts", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["artifactId"] == "test-artifact-123"
        assert data["mimeType"] == "application/json"
        assert data["filePath"] == "/path/to/downloaded/file.json"

    def test_retrieve_artifact_invalid_request(self, client):
        """Test that invalid request returns 422 (request validation error - missing fields)."""
        request_data = {
            "repository": "my-org/my-repo",
            # Missing artifactPath and versionSelector
        }

        response = client.post("/api/v1/artifacts", json=request_data)
        assert response.status_code == 422

    def test_retrieve_artifact_validation_error(self, client, mock_gitlab_client):
        """Test that validation errors return 400."""
        from artifact_retrieval_service.validation import validate_artifact_descriptor

        # Mock validation to raise error
        def mock_validate(descriptor):
            raise ValueError("repository cannot be empty")

        request_data = {
            "repository": "",
            "artifactPath": "path/to/artifact.json",
            "versionSelector": "v1.0.0",
        }

        response = client.post("/api/v1/artifacts", json=request_data)
        assert response.status_code == 400

    def test_retrieve_artifact_gitlab_error(self, client, mock_gitlab_client):
        """Test that GitLab errors return 500."""
        mock_request = MagicMock()
        mock_response = Response(404, text="Not Found")
        error = HTTPStatusError("Not Found", request=mock_request, response=mock_response)

        mock_gitlab_client.retrieve_artifact = AsyncMock(side_effect=error)

        request_data = {
            "repository": "my-org/my-repo",
            "artifactPath": "path/to/artifact.json",
            "versionSelector": "v1.0.0",
        }

        response = client.post("/api/v1/artifacts", json=request_data)
        assert response.status_code == 500

    def test_retrieve_artifact_includes_correlation_id(self, client, mock_gitlab_client):
        """Test that request includes correlation ID in logs."""
        mock_artifact = TraceableArtifact(artifactId="test-artifact-123")
        mock_gitlab_client.retrieve_artifact = AsyncMock(return_value=mock_artifact)

        request_data = {
            "repository": "my-org/my-repo",
            "artifactPath": "path/to/artifact.json",
            "versionSelector": "v1.0.0",
        }

        response = client.post(
            "/api/v1/artifacts",
            json=request_data,
            headers={"X-Correlation-ID": "test-correlation-123"},
        )

        assert response.status_code == 200
        # Correlation ID should be in response headers
        assert "X-Correlation-ID" in response.headers
