"""
Request/response mapping logic for the API subsystem.

Maps between API request/response formats and domain models.
"""
from typing import Any, Dict

from artifact_retrieval_service.models import ArtifactDescriptor, TraceableArtifact


def map_request_to_descriptor(request_data: Dict[str, Any]) -> ArtifactDescriptor:
    """
    Map API request data to ArtifactDescriptor.

    Args:
        request_data: Dictionary containing repository, artifactPath, and versionSelector.

    Returns:
        ArtifactDescriptor instance.

    Raises:
        pydantic.ValidationError: If the request data is invalid.
    """
    return ArtifactDescriptor(**request_data)


def map_artifact_to_response(artifact: TraceableArtifact) -> Dict[str, Any]:
    """
    Map TraceableArtifact to API response dictionary.

    Args:
        artifact: The traceable artifact to map.

    Returns:
        Dictionary with artifactId, optional mimeType, and filePath.
    """
    response = {
        "artifactId": artifact.artifactId,
        "mimeType": artifact.mimeType,
        "filePath": artifact.filePath,
    }
    return response

