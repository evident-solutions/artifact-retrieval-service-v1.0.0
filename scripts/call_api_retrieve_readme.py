"""
Simple helper script to call the FastAPI endpoint
POST /api/v1/artifacts to retrieve a README (or any file)
from a GitLab repository using the service's public API.

Usage:
    python call_api_retrieve_readme.py

Configuration (environment variables):
    API_BASE_URL        Base URL of the running service (default: http://localhost:8000)
    GITLAB_REPOSITORY   Repository path (default: evident-solutions/artifact-retrieval-artifacts-v1)
    GITLAB_FILE_PATH    Path to the file within the repo (default: README.md)
    GITLAB_REF          Branch/tag/commit (default: main)
    CORRELATION_ID      Optional correlation ID header value
"""

import os
import sys
import httpx


def main() -> None:
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    repository = os.getenv("GITLAB_REPOSITORY", "evident-solutions/artifact-retrieval-artifacts-v1")
    file_path = os.getenv("GITLAB_FILE_PATH", "README.md")
    version_selector = os.getenv("GITLAB_REF", "main")
    correlation_id = os.getenv("CORRELATION_ID")

    url = f"{api_base_url.rstrip('/')}/api/v1/artifacts"
    payload = {
        "repository": repository,
        "artifactPath": file_path,
        "versionSelector": version_selector,
    }
    headers: dict[str, str] = {}
    if correlation_id:
        headers["X-Correlation-ID"] = correlation_id

    print(f"POST {url}")
    print(f"Payload: {payload}")
    if correlation_id:
        print(f"Correlation ID: {correlation_id}")
    print()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        print(f"Request failed with status {exc.response.status_code}: {exc.response.text}")
        sys.exit(1)
    except httpx.RequestError as exc:
        print(f"Request error: {exc}")
        sys.exit(1)

    print("Success! API response:")
    print(data)


if __name__ == "__main__":
    main()
