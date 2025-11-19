"""
Tests for request/response mapping logic.
"""
import pytest

from artifact_retrieval_service.models import ArtifactDescriptor, TraceableArtifact
from artifact_retrieval_service.mapping import map_request_to_descriptor, map_artifact_to_response


class TestMapRequestToDescriptor:
    """Tests for map_request_to_descriptor function."""

    def test_map_valid_request_dict(self):
        """Test mapping a valid request dictionary to ArtifactDescriptor."""
        request_data = {
            "repository": "my-org/my-repo",
            "artifactPath": "path/to/artifact.json",
            "versionSelector": "v1.0.0",
        }
        descriptor = map_request_to_descriptor(request_data)
        assert isinstance(descriptor, ArtifactDescriptor)
        assert descriptor.repository == "my-org/my-repo"
        assert descriptor.artifactPath == "path/to/artifact.json"
        assert descriptor.versionSelector == "v1.0.0"

    def test_map_request_with_missing_fields_raises_error(self):
        """Test that missing fields raise ValidationError."""
        request_data = {
            "repository": "my-org/my-repo",
            # Missing artifactPath and versionSelector
        }
        with pytest.raises(Exception):  # pydantic ValidationError
            map_request_to_descriptor(request_data)


class TestMapArtifactToResponse:
    """Tests for map_artifact_to_response function."""

    def test_map_artifact_with_mime_type(self):
        """Test mapping TraceableArtifact to response dict with mimeType."""
        artifact = TraceableArtifact(
            artifactId="artifact-123",
            mimeType="application/json",
            filePath="/path/to/file.json",
        )
        response = map_artifact_to_response(artifact)
        assert response == {
            "artifactId": "artifact-123",
            "mimeType": "application/json",
            "filePath": "/path/to/file.json",
        }

    def test_map_artifact_without_mime_type(self):
        """Test mapping TraceableArtifact to response dict without mimeType."""
        artifact = TraceableArtifact(artifactId="artifact-123")
        response = map_artifact_to_response(artifact)
        assert response == {
            "artifactId": "artifact-123",
            "mimeType": None,
            "filePath": None,
        }

