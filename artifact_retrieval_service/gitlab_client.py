"""
GitLab client for retrieving artifacts.

Implements the GitLabPort interface for outgoing ArtifactDescriptor requests
and incoming TraceableArtifact responses.
"""
import os
from pathlib import Path
from typing import Protocol
import httpx
from pydantic import BaseModel, ConfigDict, Field

from artifact_retrieval_service.models import ArtifactDescriptor, TraceableArtifact


class GitLabPort(Protocol):
    """Protocol defining the GitLab port interface."""

    async def retrieve_artifact(self, descriptor: ArtifactDescriptor) -> TraceableArtifact:
        """
        Retrieve an artifact from GitLab.

        Args:
            descriptor: Artifact descriptor with repository, path, and version info.

        Returns:
            Traceable artifact with artifactId and optional mimeType.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        ...


class GitLabClientConfig(BaseModel):
    """Configuration for GitLabClient."""

    model_config = ConfigDict(frozen=True)

    base_url: str = Field(..., description="GitLab base URL (e.g., 'https://gitlab.com')")
    access_token: str = Field(..., description="GitLab access token for authentication")
    download_directory: str = Field(
        default="./downloads",
        description="Directory where artifacts are downloaded",
    )


class GitLabClient:
    """
    HTTP client for retrieving artifacts from GitLab.

    Implements GitLabPort interface with authentication and error handling.
    """

    def __init__(self, config: GitLabClientConfig):
        """
        Initialize GitLabClient.

        Args:
            config: Configuration containing base_url and access_token.
        """
        self.config = config
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def retrieve_artifact(self, descriptor: ArtifactDescriptor) -> TraceableArtifact:
        """
        Retrieve artifact metadata from GitLab.

        Args:
            descriptor: Artifact descriptor with repository, path, and version info.

        Returns:
            Traceable artifact with artifactId and optional mimeType.

        Raises:
            httpx.HTTPStatusError: If the HTTP request returns an error status.
            httpx.RequestError: If the HTTP request fails due to network issues.
        """
        # If client is not initialized, create a temporary one
        if not self._client:
            async with self:
                return await self._retrieve_artifact_internal(descriptor)
        # Otherwise use existing client
        return await self._retrieve_artifact_internal(descriptor)

    async def _retrieve_artifact_internal(self, descriptor: ArtifactDescriptor) -> TraceableArtifact:
        """Internal method to retrieve artifact (assumes client is initialized)."""
        # Construct GitLab API URL for file content
        # Format: /api/v4/projects/{project}/repository/files/{file_path}/raw?ref={ref}
        project_path = descriptor.repository.replace("/", "%2F")
        file_path = descriptor.artifactPath.replace("/", "%2F")
        url = f"/api/v4/projects/{project_path}/repository/files/{file_path}/raw"
        params = {"ref": descriptor.versionSelector}

        response = await self._client.get(url, params=params)
        response.raise_for_status()

        # Extract MIME type from response headers if available
        mime_type = response.headers.get("Content-Type")
        if mime_type:
            # Remove charset if present (e.g., "application/json; charset=utf-8" -> "application/json")
            mime_type = mime_type.split(";")[0].strip()

        # Generate artifactId (in a real implementation, this might come from GitLab metadata)
        # For now, we'll create a deterministic ID based on the descriptor
        artifact_id = f"{descriptor.repository}:{descriptor.artifactPath}:{descriptor.versionSelector}"

        # Download and save the file content
        file_path_local = await self._save_artifact_content(
            descriptor=descriptor,
            content=response.content,
            mime_type=mime_type,
        )

        return TraceableArtifact(
            artifactId=artifact_id,
            mimeType=mime_type if mime_type else None,
            filePath=file_path_local,
        )

    async def _save_artifact_content(
        self,
        descriptor: ArtifactDescriptor,
        content: bytes,
        mime_type: str | None,
    ) -> str:
        """
        Save artifact content to the download directory.

        Args:
            descriptor: Artifact descriptor with repository, path, and version info.
            content: File content as bytes.
            mime_type: MIME type of the content (optional).

        Returns:
            Absolute path to the saved file.
        """
        # Create download directory structure: downloads/{repository}/{versionSelector}/{file_path}
        download_dir = Path(self.config.download_directory).resolve()
        
        # Sanitize repository name for filesystem (replace / with _)
        repo_safe = descriptor.repository.replace("/", "_")
        version_safe = descriptor.versionSelector.replace("/", "_").replace("\\", "_")
        
        # Create directory structure
        artifact_dir = download_dir / repo_safe / version_safe
        artifact_dir.mkdir(parents=True, exist_ok=True)
        
        # Get filename from artifact path
        file_name = os.path.basename(descriptor.artifactPath)
        if not file_name:
            # If no filename, use a default based on MIME type or extension
            if mime_type:
                extension = self._get_extension_from_mime_type(mime_type)
            else:
                extension = ".txt"
            file_name = f"artifact{extension}"
        
        # Handle subdirectories in artifact path
        artifact_subdir = os.path.dirname(descriptor.artifactPath)
        if artifact_subdir:
            # Create subdirectory structure
            subdir_path = artifact_dir / artifact_subdir.replace("/", os.sep)
            subdir_path.mkdir(parents=True, exist_ok=True)
            file_path = subdir_path / file_name
        else:
            file_path = artifact_dir / file_name
        
        # Save file content
        file_path.write_bytes(content)
        
        # Return absolute path as string
        return str(file_path.resolve())

    @staticmethod
    def _get_extension_from_mime_type(mime_type: str) -> str:
        """Get file extension from MIME type."""
        mime_to_ext = {
            "text/plain": ".txt",
            "text/markdown": ".md",
            "application/json": ".json",
            "application/xml": ".xml",
            "text/xml": ".xml",
            "application/yaml": ".yaml",
            "text/yaml": ".yaml",
            "application/zip": ".zip",
            "application/pdf": ".pdf",
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/gif": ".gif",
        }
        return mime_to_ext.get(mime_type, ".bin")

