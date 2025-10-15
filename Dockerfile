# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies (including build tools for Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libc6-dev \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and group without home directory
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid 1000 --no-create-home --shell /bin/bash appuser

# Copy application source code
COPY src/ /app/src/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/
COPY entrypoint.sh /app/

# Create necessary directories and set permissions
RUN mkdir -p /app/uploads && \
    chown -R appuser:appgroup /app && \
    chmod -R 755 /app && \
    chmod +x /app/entrypoint.sh

# Set working directory to /app/src
# WORKDIR /app/src

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run the application
# Option 1: Direct uvicorn (use this if migrations are run separately)
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Option 2: Using entrypoint script (runs migrations automatically)
ENTRYPOINT ["/app/entrypoint.sh"]
