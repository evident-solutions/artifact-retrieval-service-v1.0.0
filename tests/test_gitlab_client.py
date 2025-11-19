"""
Tests for GitLabClient interface and implementation.
"""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import Response, RequestError

from artifact_retrieval_service.models import ArtifactDescriptor, TraceableArtifact
from artifact_retrieval_service.gitlab_client import GitLabClient, GitLabClientConfig


class TestGitLabClientConfig:
    """Tests for GitLabClientConfig."""

    def test_config_creation_with_all_fields(self):
        """Test creating GitLabClientConfig with all fields."""
        config = GitLabClientConfig(
            base_url="https://gitlab.com",
            access_token="token-123",
        )
        assert config.base_url == "https://gitlab.com"
        assert config.access_token == "token-123"

    def test_config_missing_base_url_raises_error(self):
        """Test that missing base_url raises error."""
        with pytest.raises(Exception):  # pydantic ValidationError
            GitLabClientConfig(access_token="token-123")

    def test_config_missing_access_token_raises_error(self):
        """Test that missing access_token raises error."""
        with pytest.raises(Exception):  # pydantic ValidationError
            GitLabClientConfig(base_url="https://gitlab.com")


class TestGitLabClient:
    """Tests for GitLabClient implementation."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create a test GitLabClientConfig."""
        return GitLabClientConfig(
            base_url="https://gitlab.com",
            access_token="test-token",
            download_directory=str(tmp_path / "downloads"),
        )

    @pytest.fixture
    def descriptor(self):
        """Create a test ArtifactDescriptor."""
        return ArtifactDescriptor(
            repository="my-org/my-repo",
            artifactPath="path/to/artifact.json",
            versionSelector="v1.0.0",
        )

    @pytest.mark.asyncio
    async def test_retrieve_artifact_success(self, config, descriptor):
        """Test successful artifact retrieval."""
        
        mock_request = MagicMock()
        mock_response = Response(
            status_code=200,
            content=b"artifact content",
            headers={"Content-Type": "application/json"},
            request=mock_request,
        )
        
        with patch("httpx.AsyncClient") as mock_client_class:
            # Create a mock client instance that will be returned by AsyncClient()
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.aclose = AsyncMock()
            # Make AsyncClient() return this instance
            mock_client_class.return_value = mock_client_instance
            
            client = GitLabClient(config)
            result = await client.retrieve_artifact(descriptor)
            
            assert result.artifactId is not None
            assert isinstance(result, TraceableArtifact)
            assert result.filePath is not None
            assert os.path.exists(result.filePath)
            mock_client_instance.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_artifact_with_mime_type(self, config, descriptor):
        """Test artifact retrieval includes MIME type from response headers."""
        mock_request = MagicMock()
        mock_response = Response(
            status_code=200,
            content=b"artifact content",
            headers={"Content-Type": "application/json"},
            request=mock_request,
        )
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.aclose = AsyncMock()
            mock_client_class.return_value = mock_client_instance
            
            client = GitLabClient(config)
            result = await client.retrieve_artifact(descriptor)
            
            assert result.mimeType == "application/json"
            assert result.filePath is not None

    @pytest.mark.asyncio
    async def test_retrieve_artifact_http_error(self, config, descriptor):
        """Test handling of HTTP errors."""
        from httpx import HTTPStatusError
        
        mock_response = Response(status_code=404, text="Not Found", request=MagicMock())
        # Make raise_for_status raise an HTTPStatusError
        mock_response.raise_for_status = MagicMock(side_effect=HTTPStatusError("Not Found", request=MagicMock(), response=mock_response))
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.aclose = AsyncMock()
            mock_client_class.return_value = mock_client_instance
            
            client = GitLabClient(config)
            
            with pytest.raises(HTTPStatusError):
                await client.retrieve_artifact(descriptor)

    @pytest.mark.asyncio
    async def test_retrieve_artifact_network_error(self, config, descriptor):
        """Test handling of network errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(side_effect=RequestError("Network error"))
            mock_client_instance.aclose = AsyncMock()
            mock_client_class.return_value = mock_client_instance
            
            client = GitLabClient(config)
            
            with pytest.raises(RequestError):
                await client.retrieve_artifact(descriptor)

    @pytest.mark.asyncio
    async def test_retrieve_artifact_sets_authorization_header(self, config, descriptor):
        """Test that authorization header is set correctly."""
        mock_request = MagicMock()
        mock_response = Response(
            status_code=200,
            content=b"artifact content",
            request=mock_request,
        )
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client_instance.aclose = AsyncMock()
            mock_client_class.return_value = mock_client_instance
            
            client = GitLabClient(config)
            await client.retrieve_artifact(descriptor)
            
            # Verify the client was created with correct headers
            call_args = mock_client_class.call_args
            assert call_args is not None
            headers = call_args.kwargs.get("headers", {})
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test-token"

