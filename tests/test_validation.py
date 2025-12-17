"""
Tests for request validation logic.
"""

import pytest

from artifact_retrieval_service.models import ArtifactDescriptor
from artifact_retrieval_service.validation import validate_artifact_descriptor


class TestValidateArtifactDescriptor:
    """Tests for validate_artifact_descriptor function."""

    def test_validate_valid_descriptor(self):
        """Test validation of a valid descriptor."""
        descriptor = ArtifactDescriptor(
            repository="my-org/my-repo",
            artifactPath="path/to/artifact.json",
            versionSelector="v1.0.0",
        )
        # Should not raise
        validate_artifact_descriptor(descriptor)

    def test_validate_empty_repository_raises_error(self):
        """Test that empty repository raises ValidationError."""
        descriptor = ArtifactDescriptor(
            repository="",
            artifactPath="path/to/artifact.json",
            versionSelector="v1.0.0",
        )
        with pytest.raises(ValueError, match="repository"):
            validate_artifact_descriptor(descriptor)

    def test_validate_empty_artifact_path_raises_error(self):
        """Test that empty artifactPath raises ValidationError."""
        descriptor = ArtifactDescriptor(
            repository="my-org/my-repo",
            artifactPath="",
            versionSelector="v1.0.0",
        )
        with pytest.raises(ValueError, match="artifactPath"):
            validate_artifact_descriptor(descriptor)

    def test_validate_empty_version_selector_raises_error(self):
        """Test that empty versionSelector raises ValidationError."""
        descriptor = ArtifactDescriptor(
            repository="my-org/my-repo",
            artifactPath="path/to/artifact.json",
            versionSelector="",
        )
        with pytest.raises(ValueError, match="versionSelector"):
            validate_artifact_descriptor(descriptor)

    def test_validate_invalid_repository_format_raises_error(self):
        """Test that invalid repository format raises ValidationError."""
        descriptor = ArtifactDescriptor(
            repository="invalid-repo-format",
            artifactPath="path/to/artifact.json",
            versionSelector="v1.0.0",
        )
        with pytest.raises(ValueError, match="repository"):
            validate_artifact_descriptor(descriptor)

    def test_validate_valid_repository_with_slashes(self):
        """Test that valid repository format with slashes passes."""
        descriptor = ArtifactDescriptor(
            repository="my-org/my-repo",
            artifactPath="path/to/artifact.json",
            versionSelector="v1.0.0",
        )
        # Should not raise
        validate_artifact_descriptor(descriptor)
