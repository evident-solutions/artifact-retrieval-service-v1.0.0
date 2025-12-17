"""
FastAPI application main module.

Implements the AgentApiPort interface and provides health/readiness endpoints.
"""
import uuid
from contextvars import ContextVar
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, Request, Header
import httpx
import structlog

from artifact_retrieval_service.config import settings
from artifact_retrieval_service.gitlab_client import GitLabClient, GitLabClientConfig
from artifact_retrieval_service.logging_config import setup_logging, get_logger
from artifact_retrieval_service.models import ArtifactDescriptor, TraceableArtifact
from artifact_retrieval_service.validation import validate_artifact_descriptor

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)

# Context variable for correlation ID
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Service for retrieving artifacts from GitLab",
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Middleware to extract and set correlation ID from headers."""
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    
    # Add correlation ID to structlog context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


def get_gitlab_client() -> GitLabClient:
    """
    Dependency injection for GitLabClient.

    Returns:
        Configured GitLabClient instance.
    
    Raises:
        ValueError: If GitLab access token is not configured.
    """
    if not settings.gitlab_access_token:
        raise ValueError(
            "GITLAB_ACCESS_TOKEN environment variable is required. "
            "Please set it in your .env file or environment variables."
        )
    config = GitLabClientConfig(
        base_url=settings.gitlab_base_url,
        access_token=settings.gitlab_access_token,
        download_directory=settings.download_directory,
    )
    return GitLabClient(config)


@app.get("/healthz")
async def health_check():
    """
    Health check endpoint.

    Returns:
        JSON response with status "healthy".
    """
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.

    Returns:
        JSON response with status "ready".
    """
    # TODO: Add readiness checks (e.g., GitLab connectivity)
    return {"status": "ready"}


@app.post("/api/v1/artifacts", response_model=TraceableArtifact)
async def retrieve_artifact(
    request_data: ArtifactDescriptor,
    gitlab_client: Annotated[GitLabClient, Depends(get_gitlab_client)],
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID", required=False)] = None,
):
    """
    Retrieve an artifact from GitLab (AgentApiPort implementation).

    Args:
        request_data: Artifact descriptor with repository, artifactPath, and versionSelector.
        gitlab_client: Injected GitLabClient dependency.
        correlation_id: Optional correlation ID from header.

    Returns:
        TraceableArtifact with artifactId, optional mimeType, and filePath.

    Raises:
        HTTPException: If validation or retrieval fails.
    """
    try:
        # Validate descriptor (business logic validation)
        validate_artifact_descriptor(request_data)
        
        # Add artifact context to logs (will be set after retrieval)
        logger.info(
            "Retrieving artifact",
            repository=request_data.repository,
            artifact_path=request_data.artifactPath,
            version_selector=request_data.versionSelector,
        )
        
        # Retrieve artifact from GitLab
        # Note: retrieve_artifact handles its own context manager if needed
        artifact = await gitlab_client.retrieve_artifact(request_data)
        
        # Add artifact ID to log context
        structlog.contextvars.bind_contextvars(artifactId=artifact.artifactId)
        logger.info(
            "Artifact retrieved successfully",
            artifact_id=artifact.artifactId,
            mime_type=artifact.mimeType,
        )
        
        # Return artifact directly (FastAPI will serialize TraceableArtifact automatically)
        return artifact
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 422 from validation errors)
        raise
    except ValueError as e:
        logger.warning("Validation error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        
        # Preserve client error status codes (4xx) and map server errors (5xx) appropriately
        if 400 <= status_code < 500:
            # Client errors: preserve the original status code
            error_detail = f"GitLab API error: {status_code}"
            if status_code == 401:
                error_detail = "GitLab authentication failed. Please check your access token is valid and has the required permissions."
            elif status_code == 404:
                error_detail = "Artifact not found. Please verify the repository, path, and version selector."
            elif status_code == 403:
                error_detail = "Access forbidden. The token may not have permission to access this repository."
            
            logger.error(
                "GitLab HTTP client error",
                status_code=status_code,
                error=str(e),
            )
            raise HTTPException(
                status_code=status_code,
                detail=error_detail,
            )
        else:
            # Server errors (5xx): map to 502 Bad Gateway (upstream server error)
            logger.error(
                "GitLab HTTP server error",
                status_code=status_code,
                error=str(e),
            )
            raise HTTPException(
                status_code=502,
                detail=f"GitLab server error: {status_code}",
            )
    except httpx.RequestError as e:
        logger.error("GitLab request error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to connect to GitLab",
        )
    except Exception as e:
        logger.error("Unexpected error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# OpenTelemetry/Prometheus metrics (commented for future implementation)
# from prometheus_client import Counter, Histogram
# 
# artifact_requests_total = Counter(
#     'artifact_requests_total',
#     'Total number of artifact requests',
#     ['repository', 'status']
# )
# 
# artifact_request_duration = Histogram(
#     'artifact_request_duration_seconds',
#     'Duration of artifact requests',
#     ['repository']
# )

