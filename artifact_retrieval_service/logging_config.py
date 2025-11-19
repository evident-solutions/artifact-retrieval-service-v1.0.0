"""
Structured logging configuration with correlationId and artifactId support.
"""
import logging
import sys
from typing import Any, Dict
import structlog


def add_correlation_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add correlation ID to log events if available in context."""
    # Correlation ID should be set in request context (handled by middleware)
    return event_dict


def add_artifact_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add artifact ID to log events if available in context."""
    # Artifact ID should be set in request context (handled by middleware)
    return event_dict


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured JSON logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # Merge context variables
            structlog.processors.add_log_level,  # Add log level
            structlog.processors.TimeStamper(fmt="iso"),  # ISO timestamp
            add_correlation_id,  # Add correlation ID
            add_artifact_id,  # Add artifact ID
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,  # Format exceptions
            structlog.processors.JSONRenderer(),  # JSON output
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured structlog logger.
    """
    return structlog.get_logger(name)

