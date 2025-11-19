"""
Data models for the Artifact Retrieval Service.

Defines ArtifactDescriptor and TraceableArtifact models.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ArtifactDescriptor(BaseModel):
    """Descriptor for an artifact to retrieve from GitLab."""

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "repository": "my-org/my-repo",
                "artifactPath": "path/to/artifact.json",
                "versionSelector": "v1.0.0",
            }
        },
    )

    repository: str = Field(..., description="GitLab repository identifier (e.g., 'org/repo')")
    artifactPath: str = Field(..., description="Path to the artifact within the repository")
    versionSelector: str = Field(..., description="Version selector (tag, branch, or commit SHA)")


class TraceableArtifact(BaseModel):
    """Traceable artifact retrieved from GitLab."""

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "artifactId": "artifact-123",
                "mimeType": "application/json",
                "filePath": "/path/to/downloaded/file.json",
            }
        },
    )

    artifactId: str = Field(..., description="Unique identifier for the artifact")
    mimeType: Optional[str] = Field(None, description="MIME type of the artifact content")
    filePath: Optional[str] = Field(None, description="Local file path where the artifact was downloaded")

