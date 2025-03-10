# Optimized Dockerfile for Google Cloud Run deployment

# Use multi-stage build for better security and smaller image size
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade google-genai

# Stage 2: Runtime image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Create a non-root user to run the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Create secrets directory with proper permissions
RUN mkdir -p /app/secrets && chown -R appuser:appuser /app

# Copy the application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# This container will listen on port 8080
EXPOSE 8080

# Run gunicorn with optimized settings for Cloud Run
# - workers: Set to auto-detect CPU cores (2*cores+1) or adjust based on memory
# - timeout: Adjust based on your application needs
CMD exec gunicorn --bind :$PORT --workers 2 --threads 8 --timeout 120 main:app
