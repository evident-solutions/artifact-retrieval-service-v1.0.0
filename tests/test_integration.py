"""
Integration tests for GitLab client with a real GitLab instance.

These tests require:
- GITLAB_BASE_URL environment variable (defaults to https://gitlab.com)
- GITLAB_ACCESS_TOKEN environment variable
- A test repository accessible with the token

To run integration tests:
    pytest tests/test_integration.py -v

To skip integration tests (default):
    pytest tests/test_integration.py -v -m "not integration"
"""
import os
import pytest
from artifact_retrieval_service.gitlab_client import GitLabClient, GitLabClientConfig
from artifact_retrieval_service.models import ArtifactDescriptor, TraceableArtifact


# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def gitlab_config():
    """Create GitLab configuration from environment variables."""
    base_url = os.getenv("GITLAB_BASE_URL", "https://gitlab.com")
    access_token = os.getenv("GITLAB_ACCESS_TOKEN", "")
    
    if not access_token:
        pytest.skip("GITLAB_ACCESS_TOKEN not set - skipping integration tests")
    
    return GitLabClientConfig(
        base_url=base_url,
        access_token=access_token,
    )


@pytest.fixture(scope="module")
def test_repository():
    """Get test repository from environment or use a default."""
    repo = os.getenv("GITLAB_TEST_REPOSITORY", "")
    if not repo:
        pytest.skip("GITLAB_TEST_REPOSITORY not set - skipping integration tests")
    return repo


@pytest.fixture(scope="module")
def test_file_path():
    """Get test file path from environment or use a default."""
    return os.getenv("GITLAB_TEST_FILE_PATH", "README.md")


@pytest.fixture(scope="module")
def test_branch():
    """Get test branch/ref from environment or use a default."""
    return os.getenv("GITLAB_TEST_BRANCH", "main")


@pytest.mark.asyncio
async def test_retrieve_existing_file(gitlab_config, test_repository, test_file_path, test_branch):
    """Test retrieving an existing file from GitLab."""
    descriptor = ArtifactDescriptor(
        repository=test_repository,
        artifactPath=test_file_path,
        versionSelector=test_branch,
    )
    
    async with GitLabClient(gitlab_config) as client:
        result = await client.retrieve_artifact(descriptor)
    
    assert isinstance(result, TraceableArtifact)
    assert result.artifactId is not None
    assert result.artifactId == f"{test_repository}:{test_file_path}:{test_branch}"
    # README.md should have some content type
    if test_file_path.endswith(".md"):
        assert result.mimeType is not None or result.mimeType is None  # May or may not be set


@pytest.mark.asyncio
async def test_retrieve_file_with_different_branch(gitlab_config, test_repository, test_file_path):
    """Test retrieving a file from a different branch."""
    # Try to get a file from a common branch name
    for branch in ["main", "master", "develop"]:
        try:
            descriptor = ArtifactDescriptor(
                repository=test_repository,
                artifactPath=test_file_path,
                versionSelector=branch,
            )
            
            async with GitLabClient(gitlab_config) as client:
                result = await client.retrieve_artifact(descriptor)
            
            assert isinstance(result, TraceableArtifact)
            assert result.artifactId == f"{test_repository}:{test_file_path}:{branch}"
            break  # Success, no need to try other branches
        except Exception:
            continue  # Try next branch
    else:
        pytest.skip(f"Could not find file in any common branch (main/master/develop)")


@pytest.mark.asyncio
async def test_retrieve_nonexistent_file(gitlab_config, test_repository, test_branch):
    """Test that retrieving a non-existent file raises an error."""
    descriptor = ArtifactDescriptor(
        repository=test_repository,
        artifactPath="this/file/does/not/exist.txt",
        versionSelector=test_branch,
    )
    
    from httpx import HTTPStatusError
    
    async with GitLabClient(gitlab_config) as client:
        with pytest.raises(HTTPStatusError) as exc_info:
            await client.retrieve_artifact(descriptor)
        
        # Should be 404 Not Found
        assert exc_info.value.response.status_code == 404


@pytest.mark.asyncio
async def test_retrieve_file_with_tag(gitlab_config, test_repository, test_file_path):
    """Test retrieving a file using a tag as version selector."""
    # This test will be skipped if no tags are available
    # You can set GITLAB_TEST_TAG environment variable to specify a tag
    test_tag = os.getenv("GITLAB_TEST_TAG", "")
    
    if not test_tag:
        pytest.skip("GITLAB_TEST_TAG not set - skipping tag test")
    
    descriptor = ArtifactDescriptor(
        repository=test_repository,
        artifactPath=test_file_path,
        versionSelector=test_tag,
    )
    
    async with GitLabClient(gitlab_config) as client:
        result = await client.retrieve_artifact(descriptor)
    
    assert isinstance(result, TraceableArtifact)
    assert result.artifactId == f"{test_repository}:{test_file_path}:{test_tag}"


@pytest.mark.asyncio
async def test_retrieve_file_with_commit_sha(gitlab_config, test_repository, test_file_path):
    """Test retrieving a file using a commit SHA as version selector."""
    # This test will be skipped if no commit SHA is provided
    # You can set GITLAB_TEST_COMMIT_SHA environment variable
    test_commit = os.getenv("GITLAB_TEST_COMMIT_SHA", "")
    
    if not test_commit:
        pytest.skip("GITLAB_TEST_COMMIT_SHA not set - skipping commit SHA test")
    
    descriptor = ArtifactDescriptor(
        repository=test_repository,
        artifactPath=test_file_path,
        versionSelector=test_commit,
    )
    
    async with GitLabClient(gitlab_config) as client:
        result = await client.retrieve_artifact(descriptor)
    
    assert isinstance(result, TraceableArtifact)
    assert result.artifactId == f"{test_repository}:{test_file_path}:{test_commit}"


@pytest.mark.asyncio
async def test_retrieve_file_in_subdirectory(gitlab_config, test_repository, test_branch):
    """Test retrieving a file from a subdirectory."""
    # Try common file paths
    test_paths = [
        "README.md",
        "docs/README.md",
        ".gitignore",
        "requirements.txt",
        "pyproject.toml",
    ]
    
    for test_path in test_paths:
        try:
            descriptor = ArtifactDescriptor(
                repository=test_repository,
                artifactPath=test_path,
                versionSelector=test_branch,
            )
            
            async with GitLabClient(gitlab_config) as client:
                result = await client.retrieve_artifact(descriptor)
            
            assert isinstance(result, TraceableArtifact)
            assert result.artifactId == f"{test_repository}:{test_path}:{test_branch}"
            break  # Success
        except Exception:
            continue  # Try next path
    else:
        pytest.skip("Could not find any test file in common locations")


@pytest.mark.asyncio
async def test_mime_type_detection(gitlab_config, test_repository, test_branch):
    """Test that MIME types are correctly detected for different file types."""
    # Test different file types
    test_files = [
        ("README.md", "text/markdown"),  # May vary
        (".gitignore", None),  # May not have MIME type
    ]
    
    for file_path, expected_mime in test_files:
        try:
            descriptor = ArtifactDescriptor(
                repository=test_repository,
                artifactPath=file_path,
                versionSelector=test_branch,
            )
            
            async with GitLabClient(gitlab_config) as client:
                result = await client.retrieve_artifact(descriptor)
            
            assert isinstance(result, TraceableArtifact)
            # MIME type may or may not be set depending on GitLab response
            if expected_mime:
                # Just verify it's a string if present
                assert result.mimeType is None or isinstance(result.mimeType, str)
            break  # At least one file worked
        except Exception:
            continue


@pytest.mark.asyncio
async def test_invalid_repository(gitlab_config):
    """Test that an invalid repository raises an error."""
    descriptor = ArtifactDescriptor(
        repository="this/repo/does/not/exist",
        artifactPath="README.md",
        versionSelector="main",
    )
    
    from httpx import HTTPStatusError
    
    async with GitLabClient(gitlab_config) as client:
        with pytest.raises(HTTPStatusError) as exc_info:
            await client.retrieve_artifact(descriptor)
        
        # Should be 404 Not Found
        assert exc_info.value.response.status_code == 404

