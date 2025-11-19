"""
Request validation logic for the API subsystem.

Validates ArtifactDescriptor objects according to business rules.
"""
import re

from artifact_retrieval_service.models import ArtifactDescriptor


def validate_artifact_descriptor(descriptor: ArtifactDescriptor) -> None:
    """
    Validate an ArtifactDescriptor according to business rules.

    Args:
        descriptor: The artifact descriptor to validate.

    Raises:
        ValueError: If validation fails with a descriptive error message.
    """
    if not descriptor.repository or not descriptor.repository.strip():
        raise ValueError("repository cannot be empty")

    if not descriptor.artifactPath or not descriptor.artifactPath.strip():
        raise ValueError("artifactPath cannot be empty")

    if not descriptor.versionSelector or not descriptor.versionSelector.strip():
        raise ValueError("versionSelector cannot be empty")

    # Validate repository format: should contain at least one slash (org/repo)
    if "/" not in descriptor.repository:
        raise ValueError(
            f"repository must be in format 'org/repo', got: {descriptor.repository}"
        )

    # Additional validation: repository should not contain invalid characters
    if not re.match(r"^[\w\-\.]+/[\w\-\.]+$", descriptor.repository):
        raise ValueError(
            f"repository format is invalid, expected 'org/repo' format: {descriptor.repository}"
        )

