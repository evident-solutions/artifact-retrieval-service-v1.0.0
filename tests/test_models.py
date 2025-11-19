"""
Tests for data models: ArtifactDescriptor and TraceableArtifact.
"""
import pytest
from pydantic import ValidationError

from artifact_retrieval_service.models import ArtifactDescriptor, TraceableArtifact


class TestArtifactDescriptor:
    """Tests for ArtifactDescriptor model."""

    def test_artifact_descriptor_creation_with_all_fields(self):
        """Test creating ArtifactDescriptor with all required fields."""
        descriptor = ArtifactDescriptor(
            repository="my-org/my-repo",
            artifactPath="path/to/artifact.json",
            versionSelector="v1.0.0",
        )
        assert descriptor.repository == "my-org/my-repo"
        assert descriptor.artifactPath == "path/to/artifact.json"
        assert descriptor.versionSelector == "v1.0.0"

    def test_artifact_descriptor_missing_repository_raises_error(self):
        """Test that missing repository field raises ValidationError."""
        with pytest.raises(ValidationError):
            ArtifactDescriptor(
                artifactPath="path/to/artifact.json",
                versionSelector="v1.0.0",
            )

    def test_artifact_descriptor_missing_artifact_path_raises_error(self):
        """Test that missing artifactPath field raises ValidationError."""
        with pytest.raises(ValidationError):
            ArtifactDescriptor(
                repository="my-org/my-repo",
                versionSelector="v1.0.0",
            )

    def test_artifact_descriptor_missing_version_selector_raises_error(self):
        """Test that missing versionSelector field raises ValidationError."""
        with pytest.raises(ValidationError):
            ArtifactDescriptor(
                repository="my-org/my-repo",
                artifactPath="path/to/artifact.json",
            )

    def test_artifact_descriptor_empty_strings_are_valid(self):
        """Test that empty strings are accepted (validation logic may reject them later)."""
        descriptor = ArtifactDescriptor(
            repository="",
            artifactPath="",
            versionSelector="",
        )
        assert descriptor.repository == ""
        assert descriptor.artifactPath == ""
        assert descriptor.versionSelector == ""


class TestTraceableArtifact:
    """Tests for TraceableArtifact model."""

    def test_traceable_artifact_creation_with_required_field(self):
        """Test creating TraceableArtifact with required artifactId."""
        artifact = TraceableArtifact(artifactId="artifact-123")
        assert artifact.artifactId == "artifact-123"
        assert artifact.mimeType is None
        assert artifact.filePath is None

    def test_traceable_artifact_creation_with_mime_type(self):
        """Test creating TraceableArtifact with optional mimeType."""
        artifact = TraceableArtifact(
            artifactId="artifact-123",
            mimeType="application/json",
        )
        assert artifact.artifactId == "artifact-123"
        assert artifact.mimeType == "application/json"
        assert artifact.filePath is None

    def test_traceable_artifact_creation_with_file_path(self):
        """Test creating TraceableArtifact with filePath."""
        artifact = TraceableArtifact(
            artifactId="artifact-123",
            mimeType="application/json",
            filePath="/path/to/file.json",
        )
        assert artifact.artifactId == "artifact-123"
        assert artifact.mimeType == "application/json"
        assert artifact.filePath == "/path/to/file.json"

    def test_traceable_artifact_missing_artifact_id_raises_error(self):
        """Test that missing artifactId field raises ValidationError."""
        with pytest.raises(ValidationError):
            TraceableArtifact(mimeType="application/json")

