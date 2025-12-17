# Artifact Retrieval Service

A well-tested, production-ready Python service for retrieving artifacts from GitLab, implementing the ArtifactRetrievalService as described in the SysML model `ArtifactRetrievalServiceProduct_minimal_fully_traced_v3.sysml` under `docs`.

## Features

- **Agent API Port**: RESTful API for retrieving artifacts (implements `AgentApiPort` interface, defined in the sysml model in `docs`)
- **GitLab Integration**: Secure HTTP client with authentication for GitLab API
- **Request Validation**: Comprehensive validation of artifact descriptors
- **Structured Logging**: JSON logs with `correlationId` and `artifactId` tracking
- **Health Monitoring**: `/healthz` and `/ready` endpoints for Kubernetes readiness/liveness probes
- **Dependency Injection**: Clean architecture with testable components
- **Observability**: OpenTelemetry/Prometheus metrics support (commented for future implementation)
- **CI/CD Ready**: GitHub Actions workflow for linting, testing, coverage, and Docker builds

## Architecture

The service is organized into subsystems as per the SysML model:

- **ApiSubsystem**: FastAPI gateway, request validation, and request mapping
- **GitLabSubsystem**: GitLab HTTP client with authentication and file download
- **MonitoringSubsystem**: Structured logging and health/readiness endpoints

### Data Models

- `ArtifactDescriptor`: Contains `repository`, `artifactPath`, and `versionSelector`
- `TraceableArtifact`: Contains `artifactId`, optional `mimeType`, and `filePath` (download location)

### Architecture Diagrams

Visual architecture documentation is available in the `docs/` directory:

- **Architecture Diagram** (`docs/architecture.puml`): High-level component view with subsystems
- **Sequence Diagram** (`docs/sequence.puml`): Request flow and interactions
- **Component Diagram** (`docs/component.puml`): Module dependencies
- **Class Diagram** (`docs/class_diagram.puml`): Python class structure and relationships

See `docs/README.md` for instructions on viewing PlantUML diagrams.

## Prerequisites

- Python 3.12+ (tested with Python 3.12.10)
- Git
- Docker (optional, for containerized deployment)

## Setup

### 1. Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
# Install production dependencies
pip install -r requirements.txt

# Or install with dev dependencies
pip install -r requirements-dev.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# GitLab Configuration (Required)
GITLAB_BASE_URL=https://gitlab.com
GITLAB_ACCESS_TOKEN=your-gitlab-access-token-here

# Application Configuration (Optional)
APP_NAME=Artifact Retrieval Service
APP_VERSION=1.0.0
LOG_LEVEL=INFO
DOWNLOAD_DIRECTORY=./downloads  # Directory where artifacts are downloaded
```

**⚠️ Security Note**: Never commit `.env` files or hard-code secrets. Use environment variables or a secrets management system in production.

### 4. Install Pre-commit Hooks (Optional)

```powershell
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

## Running the Service

### Development Mode

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run with uvicorn
uvicorn artifact_retrieval_service.main:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`

### Production Mode

```powershell
uvicorn artifact_retrieval_service.main:app --host 0.0.0.0 --port 8000
```

### Docker

```powershell
# Build image
docker build -t artifact-retrieval-service:latest .

# Run container
docker run -p 8000:8000 \
  -e GITLAB_BASE_URL=https://gitlab.com \
  -e GITLAB_ACCESS_TOKEN=your-token \
  artifact-retrieval-service:latest
```

## API Documentation

Once the service is running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check

```http
GET /healthz
```

Returns:
```json
{
  "status": "healthy"
}
```

### Readiness Check

```http
GET /ready
```

Returns:
```json
{
  "status": "ready"
}
```

### Retrieve Artifact (AgentApiPort)

```http
POST /api/v1/artifacts
Content-Type: application/json
X-Correlation-ID: optional-correlation-id

{
  "repository": "my-org/my-repo",
  "artifactPath": "path/to/artifact.json",
  "versionSelector": "v1.0.0"
}
```

Response:
```json
{
  "artifactId": "my-org/my-repo:path/to/artifact.json:v1.0.0",
  "mimeType": "application/json",
  "filePath": "/absolute/path/to/downloads/my-org_my-repo/v1.0.0/path/to/artifact.json"
}
```

**Note:** The service automatically downloads the file content to a local directory. The `filePath` in the response indicates where the file was saved.

#### Example with cURL

```bash
curl -X POST http://localhost:8000/api/v1/artifacts \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: my-correlation-id" \
  -d '{
    "repository": "my-org/my-repo",
    "artifactPath": "config/app.json",
    "versionSelector": "main"
  }'
```

## Testing

The project follows Test-Driven Development (TDD) principles. All features have corresponding tests.

### Run Tests

```powershell
# Run all unit tests (integration tests skipped by default)
pytest

# Run with coverage
pytest --cov=artifact_retrieval_service --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Integration Tests

Integration tests verify the service against a real GitLab instance. They are **skipped by default** to avoid requiring GitLab credentials for regular development.

**To run integration tests:**

```powershell
# Set required environment variables
$env:GITLAB_ACCESS_TOKEN="your-gitlab-token"
$env:GITLAB_TEST_REPOSITORY="your-org/your-repo"

# Run integration tests
pytest -v -m integration

# Or run the integration test file directly
pytest tests/test_integration.py -v
```

See `tests/README_INTEGRATION.md` for detailed integration test documentation.

### Test Coverage

Coverage reports are generated in:
- Terminal: displayed after test run
- HTML: `htmlcov/index.html`
- XML: `coverage.xml` (for CI/CD)

## Code Quality

### Formatting and Linting

```powershell
# Format code with black
black artifact_retrieval_service tests

# Sort imports with isort
isort artifact_retrieval_service tests

# Lint with flake8
flake8 artifact_retrieval_service tests --max-line-length=100 --extend-ignore=E203

# Type checking with mypy (optional)
mypy artifact_retrieval_service
```

### Pre-commit Hooks

Pre-commit hooks automatically run:
- `black` (code formatting)
- `isort` (import sorting)
- `flake8` (linting)
- File checks (trailing whitespace, end of file, YAML/JSON/TOML validation)

## CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:

1. **Lint Job**: Runs `black`, `isort`, `flake8`, and `mypy`
2. **Test Job**: Runs pytest with coverage reporting
3. **Build Job**: Builds Docker image (runs after lint and test pass)

### GitHub Actions Secrets

For production deployments, configure these secrets in GitHub:
- `GITLAB_ACCESS_TOKEN`: GitLab access token for CI/CD operations

## Project Structure

```
artifact-retrieval-service-v1/
├── artifact_retrieval_service/    # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── models.py                  # Data models (ArtifactDescriptor, TraceableArtifact)
│   ├── gitlab_client.py           # GitLab client implementation
│   ├── validation.py              # Request validation logic
│   ├── mapping.py                 # Request/response mapping
│   ├── config.py                  # Configuration management
│   └── logging_config.py          # Structured logging setup
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_gitlab_client.py
│   ├── test_validation.py
│   ├── test_mapping.py
│   └── test_api.py
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD pipeline
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                 # Project configuration (black, isort, pytest, mypy)
├── Dockerfile                     # Docker image definition
├── .dockerignore                  # Docker ignore patterns
├── .gitignore                     # Git ignore patterns
└── README.md                      # This file
```

## Secret Management

### Development

Use `.env` files (not committed to git) for local development.

### Production

**Recommended approaches:**

1. **Environment Variables**: Set via container orchestration (Kubernetes secrets, Docker secrets)
2. **Secrets Manager**: Use AWS Secrets Manager, HashiCorp Vault, or similar
3. **CI/CD Variables**: Store in GitHub Secrets, GitLab CI/CD variables, etc.

**Never:**
- Commit secrets to version control
- Hard-code secrets in source code
- Log secrets in application logs

## Observability

### Logging

The service uses structured JSON logging with the following fields:
- `correlationId`: Request correlation ID (from `X-Correlation-ID` header or auto-generated)
- `artifactId`: Artifact ID (set after successful retrieval)
- `timestamp`: ISO format timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Metrics (Future Implementation)

OpenTelemetry/Prometheus metrics are prepared in code comments. To enable:

1. Install OpenTelemetry packages
2. Uncomment metrics code in `main.py`
3. Configure Prometheus exporter
4. Expose `/metrics` endpoint

Example metrics (commented in code):
- `artifact_requests_total`: Counter of artifact requests by repository and status
- `artifact_request_duration_seconds`: Histogram of request duration by repository

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated and dependencies are installed
2. **GitLab Authentication**: Verify `GITLAB_ACCESS_TOKEN` is set correctly
3. **Port Already in Use**: Change port with `--port 8001` or kill the process using port 8000
4. **Test Failures**: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Debug Mode

Enable debug logging:

```powershell
# Set in .env file
LOG_LEVEL=DEBUG

# Or via environment variable
$env:LOG_LEVEL="DEBUG"
uvicorn artifact_retrieval_service.main:app --reload
```

## Contributing

1. Create a feature branch
2. Write tests first (TDD)
3. Implement the feature
4. Ensure all tests pass
5. Run formatters and linters
6. Submit a pull request

## License

[Specify your license here]

## Support

For issues and questions, please open an issue in the repository.

