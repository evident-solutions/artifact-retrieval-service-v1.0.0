"""
Script to retrieve README file from GitLab repository.

Usage:
    python retrieve_readme.py

Environment variables required:
    GITLAB_ACCESS_TOKEN: GitLab access token
    GITLAB_BASE_URL: GitLab base URL (default: https://gitlab.com)
    GITLAB_REPOSITORY: Repository path in format namespace/project (default: evident-solutions/artifact-retrieval-artifacts-v1)
    GITLAB_BRANCH: Branch name (default: main)
"""
import os
import sys
import asyncio
from artifact_retrieval_service.gitlab_client import GitLabClient, GitLabClientConfig
from artifact_retrieval_service.models import ArtifactDescriptor


async def retrieve_readme():
    """Retrieve README file from GitLab repository."""
    # Get configuration from environment variables
    access_token = os.getenv("GITLAB_ACCESS_TOKEN")
    if not access_token:
        print("ERROR: GITLAB_ACCESS_TOKEN environment variable is required")
        print("Set it with: $env:GITLAB_ACCESS_TOKEN='your-token'")
        sys.exit(1)
    
    base_url = os.getenv("GITLAB_BASE_URL", "https://gitlab.com")
    repository = os.getenv("GITLAB_REPOSITORY", "evident-solutions/artifact-retrieval-artifacts-v1")
    branch = os.getenv("GITLAB_BRANCH", "main")
    file_path = os.getenv("GITLAB_FILE_PATH", "README.md")
    
    print(f"Retrieving {file_path} from {repository} (branch: {branch})...")
    print(f"GitLab URL: {base_url}")
    print()
    
    # Create GitLab client configuration
    config = GitLabClientConfig(
        base_url=base_url,
        access_token=access_token,
    )
    
    # Create artifact descriptor
    descriptor = ArtifactDescriptor(
        repository=repository,
        artifactPath=file_path,
        versionSelector=branch,
    )
    
    try:
        # Retrieve the file
        async with GitLabClient(config) as client:
            artifact = await client.retrieve_artifact(descriptor)
        
        print("Successfully retrieved artifact!")
        print(f"   Artifact ID: {artifact.artifactId}")
        if artifact.mimeType:
            print(f"   MIME Type: {artifact.mimeType}")
        if artifact.filePath:
            print(f"   Downloaded to: {artifact.filePath}")
        print()
        
        # Read and display the downloaded file content
        if artifact.filePath and os.path.exists(artifact.filePath):
            with open(artifact.filePath, "r", encoding="utf-8") as f:
                content = f.read()
            
            print(f"File Content ({len(content)} characters):")
            print("=" * 80)
            print(content)
            print("=" * 80)
        else:
            print("Warning: File was not downloaded or file path is not available")
        
    except Exception as e:
        print(f"Error retrieving file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(retrieve_readme())

