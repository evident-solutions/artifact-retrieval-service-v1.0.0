# Integration Tests

This directory contains integration tests that test the service against a real GitLab instance.

## Prerequisites

1. A GitLab instance (GitLab.com or self-hosted)
2. A GitLab access token with `read_api` or `read_repository` scope
3. A test repository accessible with the token

## Configuration

Set the following environment variables:

```powershell
# Required
$env:GITLAB_ACCESS_TOKEN="your-gitlab-access-token"

# Optional (defaults shown)
$env:GITLAB_BASE_URL="https://gitlab.com"  # Default: https://gitlab.com
$env:GITLAB_TEST_REPOSITORY="your-org/your-repo"  # e.g., "gitlab-org/gitlab"
$env:GITLAB_TEST_FILE_PATH="README.md"  # Default: README.md
$env:GITLAB_TEST_BRANCH="main"  # Default: main

# Optional for specific tests
$env:GITLAB_TEST_TAG="v1.0.0"  # For tag-based retrieval test
$env:GITLAB_TEST_COMMIT_SHA="abc123def456"  # For commit SHA test
```

## Running Integration Tests

### Run all tests (including integration):
```powershell
pytest -v -m integration
```

### Run only integration tests:
```powershell
pytest tests/test_integration.py -v
```

### Run all tests except integration (default):
```powershell
pytest -v
# or explicitly
pytest -v -m "not integration"
```

### Run a specific integration test:
```powershell
pytest tests/test_integration.py::test_retrieve_existing_file -v
```

## Test Coverage

Integration tests cover:
- ✅ Retrieving existing files from GitLab
- ✅ Retrieving files from different branches
- ✅ Retrieving files using tags
- ✅ Retrieving files using commit SHAs
- ✅ Retrieving files from subdirectories
- ✅ MIME type detection
- ✅ Error handling for non-existent files
- ✅ Error handling for invalid repositories

## CI/CD Integration

In CI/CD pipelines, integration tests are skipped by default. To enable them:

1. Add GitLab credentials as secrets:
   - `GITLAB_ACCESS_TOKEN`
   - `GITLAB_TEST_REPOSITORY` (optional)

2. Run with integration tests:
   ```yaml
   - name: Run integration tests
     env:
       GITLAB_ACCESS_TOKEN: ${{ secrets.GITLAB_ACCESS_TOKEN }}
       GITLAB_TEST_REPOSITORY: ${{ secrets.GITLAB_TEST_REPOSITORY }}
     run: pytest -v -m integration
   ```

## Troubleshooting

### Tests are being skipped
- Check that `GITLAB_ACCESS_TOKEN` is set
- Check that `GITLAB_TEST_REPOSITORY` is set (if required by the test)

### 401 Unauthorized errors
- Verify your access token has the correct scopes
- Check that the token hasn't expired
- Verify the repository is accessible with the token

### 404 Not Found errors
- Verify the repository path is correct (format: `org/repo`)
- Check that the file path exists in the repository
- Verify the branch/tag/commit SHA exists

### Timeout errors
- Check your network connection
- Verify GitLab instance is accessible
- Consider increasing timeout in `GitLabClient` if needed

