# Docker Deployment Guide

This guide explains how to build and run the FastAPI application using Docker.

## Table of Contents
- [Overview](#overview)
- [Dockerfile Details](#dockerfile-details)
- [Building the Image](#building-the-image)
- [Running with Docker Compose](#running-with-docker-compose)
- [Manual Docker Run](#manual-docker-run)
- [Security Features](#security-features)
- [Troubleshooting](#troubleshooting)

## Overview

The application is containerized using Docker with the following components:
- **FastAPI Application** - Python 3.12 slim image
- **PostgreSQL** - Database (version 17)
- **Redis** - Caching layer (version 7)

## Dockerfile Details

### Base Image
```dockerfile
FROM python:3.12-slim
```
- Uses Python 3.12 slim variant for smaller image size
- Reduces attack surface and deployment time

### Security Features

#### 1. Non-Root User
```dockerfile
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid 1000 --no-create-home --shell /bin/bash appuser
```
- **User ID**: 1000
- **Group ID**: 1000
- **No home directory**: Security best practice
- Application runs as `appuser`, not root

#### 2. File Permissions
```dockerfile
RUN chown -R appuser:appgroup /app && \
    chmod -R 755 /app
```
- All files in `/app` owned by `appuser:appgroup`
- Proper permissions set for security

#### 3. Working Directory
- **Build context**: `/app`
- **Runtime workdir**: `/app/src`
- Clean separation of concerns

### Environment Variables
```dockerfile
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
```
- `PYTHONUNBUFFERED`: Ensures logs appear in real-time
- `PYTHONDONTWRITEBYTECODE`: Prevents .pyc file creation
- `PIP_NO_CACHE_DIR`: Reduces image size
- `PIP_DISABLE_PIP_VERSION_CHECK`: Faster pip operations

### System Dependencies
```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libc6-dev \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
```
- `gcc`, `g++`, `make`: Build toolchain for compiling Python packages
- `libc6-dev`: C standard library headers (required for hiredis)
- `python3-dev`: Python development headers
- `postgresql-client`: PostgreSQL command-line tools

**Note**: These build dependencies are required for packages like `hiredis` (Redis client) that need to compile C extensions.

### Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1
```
- Checks application health every 30 seconds
- Allows 5 seconds for startup
- Fails after 3 consecutive failures

## Building the Image

### Basic Build
```bash
docker build -t fastapi-app:latest .
```

### Build with Custom Tag
```bash
docker build -t fastapi-app:v1.0.0 .
```

### Build with No Cache
```bash
docker build --no-cache -t fastapi-app:latest .
```

### Check Image Size
```bash
docker images fastapi-app
```

Expected size: ~200-300MB (thanks to slim image and .dockerignore)

## Running with Docker Compose

### Start All Services
```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379
- FastAPI app on port 8000

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Check Service Status
```bash
docker-compose ps
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes
```bash
docker-compose down -v
```

### Rebuild Application
```bash
# Rebuild and restart
docker-compose up -d --build app

# Force rebuild
docker-compose build --no-cache app
docker-compose up -d app
```

### Run Database Migrations
```bash
# Access the container
docker-compose exec app bash

# Inside container, run migrations
cd /app
alembic upgrade head

# Exit
exit
```

Or run directly:
```bash
docker-compose exec app alembic upgrade head
```

## Manual Docker Run

### Create Network
```bash
docker network create fastapi-network
```

### Run PostgreSQL
```bash
docker run -d \
  --name postgres \
  --network fastapi-network \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin1234 \
  -e POSTGRES_DB=fastapi \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:17
```

### Run Redis
```bash
docker run -d \
  --name redis \
  --network fastapi-network \
  -p 6379:6379 \
  redis:7
```

### Run FastAPI Application
```bash
docker run -d \
  --name fastapi-app \
  --network fastapi-network \
  -e DB_URL=postgresql://admin:admin1234@postgres:5432/fastapi \
  -e REDIS_URL=redis://redis:6379/0 \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  fastapi-app:latest
```

## Environment Variables

The application requires these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_URL` | PostgreSQL connection string | `postgresql://admin:admin1234@postgres:5432/fastapi` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |

### Using .env File

Create a `.env` file:
```env
DB_URL=postgresql://admin:admin1234@postgres:5432/fastapi
REDIS_URL=redis://redis:6379/0
```

Update docker-compose.yml:
```yaml
app:
  env_file:
    - .env
```

## Security Features

### 1. Non-Root User Execution
✅ Application runs as user `appuser` (UID: 1000)  
✅ Group `appgroup` (GID: 1000)  
✅ No home directory created  
✅ Minimal permissions  

### 2. File Ownership
✅ All application files owned by `appuser:appgroup`  
✅ Proper permissions (755) set on directories  
✅ No world-writable files  

### 3. Minimal Image
✅ Uses slim Python image (smaller attack surface)  
✅ Only necessary system packages installed  
✅ Build cache cleaned after installation  
✅ .dockerignore prevents unnecessary files  

### 4. Layer Optimization
✅ Dependencies installed before code copy (better caching)  
✅ Multi-stage friendly structure  
✅ Minimal layers created  

## .dockerignore

The `.dockerignore` file excludes:
- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments (`venv/`, `env/`)
- IDE files (`.vscode/`, `.idea/`)
- Test files (`tests/`, `test_*.py`)
- Documentation (`.md` files except README)
- Git files (`.git/`, `.gitignore`)
- Environment files (`.env`)
- CI/CD files (`.github/`)
- Scripts (`*.sh`)
- Temporary files

This reduces image size and build context.

## Accessing the Application

Once running, access:

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## Troubleshooting

### Build Errors - Missing stdlib.h or Build Dependencies

**Error:**
```
fatal error: stdlib.h: No such file or directory
error: command '/usr/bin/gcc' failed with exit code 1
ERROR: Failed building wheel for hiredis
```

**Cause:** Missing C/C++ build dependencies needed for compiling Python packages like `hiredis`.

**Solution:** The Dockerfile includes all necessary build dependencies:
```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libc6-dev \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
```

If you still see this error, rebuild with no cache:
```bash
docker-compose build --no-cache app
```

### Container Won't Start

**Check logs:**
```bash
docker-compose logs app
```

**Common issues:**
- Database not ready → Wait for PostgreSQL to be healthy
- Redis not available → Check Redis container
- Port already in use → Change port mapping

### Database Connection Issues

**Check PostgreSQL is running:**
```bash
docker-compose ps postgres
```

**Test connection:**
```bash
docker-compose exec postgres psql -U admin -d fastapi
```

**Check environment variables:**
```bash
docker-compose exec app env | grep DB_URL
```

### Permission Errors

**Check file ownership:**
```bash
docker-compose exec app ls -la /app/src
```

**Should show:**
```
drwxr-xr-x appuser appgroup
```

**Fix permissions if needed:**
```bash
docker-compose exec --user root app chown -R appuser:appgroup /app
```

### Redis Connection Issues

**Test Redis:**
```bash
docker-compose exec redis redis-cli ping
```

**Should return:** `PONG`

**Check from app container:**
```bash
docker-compose exec app python -c "import redis; r = redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

### Image Size Too Large

**Analyze image layers:**
```bash
docker history fastapi-app:latest
```

**Check for large files:**
```bash
docker run --rm fastapi-app:latest du -sh /app/*
```

**Rebuild with no cache:**
```bash
docker-compose build --no-cache app
```

### Health Check Failing

**Check health status:**
```bash
docker inspect --format='{{.State.Health.Status}}' fastapi-app
```

**View health check logs:**
```bash
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' fastapi-app
```

**Test manually:**
```bash
docker-compose exec app curl http://localhost:8000/
```

## Production Recommendations

### 1. Use Specific Tags
```dockerfile
FROM python:3.12.0-slim
```
Don't use `latest` in production.

### 2. Add Resource Limits
```yaml
app:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 512M
      reservations:
        cpus: '0.5'
        memory: 256M
```

### 3. Use Secrets for Sensitive Data
```yaml
app:
  environment:
    - DB_URL_FILE=/run/secrets/db_url
  secrets:
    - db_url

secrets:
  db_url:
    external: true
```

### 4. Enable Read-Only Root Filesystem
```yaml
app:
  read_only: true
  tmpfs:
    - /tmp
```

### 5. Use Multi-Stage Build (Optional)
For even smaller images:
```dockerfile
FROM python:3.12-slim as builder
# Install dependencies
...

FROM python:3.12-slim
# Copy only installed packages from builder
...
```

### 6. Run Migrations on Startup
Create an entrypoint script:
```bash
#!/bin/bash
set -e

# Run migrations
cd /app
alembic upgrade head

# Start application
cd /app/src
exec uvicorn main:app --host 0.0.0.0 --port 8000
```

## Quick Commands Reference

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Stop all
docker-compose down

# Restart app only
docker-compose restart app

# Run migrations
docker-compose exec app alembic upgrade head

# Access shell
docker-compose exec app bash

# Check health
docker-compose ps

# Remove everything (including volumes)
docker-compose down -v
docker system prune -a
```

## Summary

✅ **Python 3.12** slim image  
✅ **Non-root user** (UID: 1000, GID: 1000)  
✅ **No home directory** for security  
✅ **Proper file ownership** (`appuser:appgroup`)  
✅ **Working directory** at `/app/src`  
✅ **Health checks** enabled  
✅ **Optimized layers** for fast builds  
✅ **Minimal image size** with .dockerignore  
✅ **Production-ready** security practices  

Your FastAPI application is now containerized with security best practices! 🐳
