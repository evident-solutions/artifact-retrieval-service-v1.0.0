FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY artifact_retrieval_service ./artifact_retrieval_service

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "artifact_retrieval_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

