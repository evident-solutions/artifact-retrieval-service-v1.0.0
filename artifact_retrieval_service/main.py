"""
FastAPI application main module.

Implements the AgentApiPort interface and provides health/readiness endpoints.
"""
import uuid
from contextvars import ContextVar
from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.exceptions import RequestValidationError
import httpx
import structlog

from pydantic import ValidationError

from artifact_retrieval_service.config import settings
from artifact_retrieval_service.gitlab_client import GitLabClient, GitLabClientConfig
from artifact_retrieval_service.logging_config import setup_logging, get_logger
from artifact_retrieval_service.models import ArtifactDescriptor, TraceableArtifact
from artifact_retrieval_service.validation import validate_artifact_descriptor
from artifact_retrieval_service.mapping import map_request_to_descriptor, map_artifact_to_response

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


@app.post("/api/v1/artifacts", response_model=dict)
async def retrieve_artifact(
    request_data: dict,
    gitlab_client: Annotated[GitLabClient, Depends(get_gitlab_client)],
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID", required=False)] = None,
):
    """
    Retrieve an artifact from GitLab (AgentApiPort implementation).

    Args:
        request_data: Request body containing repository, artifactPath, and versionSelector.
        gitlab_client: Injected GitLabClient dependency.
        correlation_id: Optional correlation ID from header.

    Returns:
        JSON response with artifactId and optional mimeType.

    Raises:
        HTTPException: If validation or retrieval fails.
    """
    try:
        # Map request to domain model
        try:
            descriptor = map_request_to_descriptor(request_data)
        except ValidationError as e:
            # Return 422 for request validation errors (missing/invalid fields)
            logger.warning("Request validation error", error=str(e))
            raise HTTPException(status_code=422, detail=str(e))
        
        # Validate descriptor (business logic validation)
        validate_artifact_descriptor(descriptor)
        
        # Add artifact context to logs (will be set after retrieval)
        logger.info(
            "Retrieving artifact",
            repository=descriptor.repository,
            artifact_path=descriptor.artifactPath,
            version_selector=descriptor.versionSelector,
        )
        
        # Retrieve artifact from GitLab
        # Note: retrieve_artifact handles its own context manager if needed
        artifact = await gitlab_client.retrieve_artifact(descriptor)
        
        # Add artifact ID to log context
        structlog.contextvars.bind_contextvars(artifactId=artifact.artifactId)
        logger.info(
            "Artifact retrieved successfully",
            artifact_id=artifact.artifactId,
            mime_type=artifact.mimeType,
        )
        
        # Map to response
        response_data = map_artifact_to_response(artifact)
        return response_data
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 422 from validation errors)
        raise
    except ValueError as e:
        logger.warning("Validation error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPStatusError as e:
        logger.error(
            "GitLab HTTP error",
            status_code=e.response.status_code,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve artifact from GitLab: {e.response.status_code}",
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

