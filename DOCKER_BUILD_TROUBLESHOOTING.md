# Docker Build Troubleshooting Guide

## Common Build Errors and Solutions

### 1. Missing stdlib.h - Build Dependencies Error

**Error Message:**
```
fatal error: stdlib.h: No such file or directory
error: command '/usr/bin/gcc' failed with exit code 1
ERROR: Failed building wheel for hiredis
```

**Root Cause:**
- Missing C/C++ build dependencies
- Required for compiling Python packages with C extensions (like `hiredis`, `psycopg2`, etc.)

**Solution:**
The Dockerfile has been updated to include all necessary build dependencies:

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \          # GNU C compiler
    g++ \          # GNU C++ compiler  
    make \         # Build automation tool
    libc6-dev \    # C standard library headers (fixes stdlib.h error)
    python3-dev \  # Python development headers
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
```

**Quick Fix:**
```bash
# Rebuild without cache
docker-compose build --no-cache app

# Or build the image directly
docker build --no-cache -t fastapi-app:latest .
```

---

### 2. Package Installation Fails

**Error Message:**
```
ERROR: Could not find a version that satisfies the requirement <package>
ERROR: No matching distribution found for <package>
```

**Solution:**
```bash
# Verify requirements.txt exists and is readable
cat requirements.txt

# Update pip before installing
# Add to Dockerfile before pip install:
RUN pip install --upgrade pip setuptools wheel

# Rebuild
docker-compose build --no-cache app
```

---

### 3. Context Size Too Large

**Error Message:**
```
Sending build context to Docker daemon  XXX MB
```

**Solution:**
Ensure `.dockerignore` is present and configured:
```bash
# Check .dockerignore exists
cat .dockerignore

# Verify large files are excluded
ls -lh

# Common excludes:
echo "venv/" >> .dockerignore
echo "__pycache__/" >> .dockerignore
echo "*.pyc" >> .dockerignore
```

---

### 4. COPY Failed - File Not Found

**Error Message:**
```
COPY failed: file not found in build context
```

**Solution:**
```bash
# Check file exists relative to Dockerfile
ls -la src/
ls -la alembic/

# Verify .dockerignore isn't excluding needed files
cat .dockerignore

# Make sure you're building from the project root
cd /Users/Jmcglobal/My-Files/Spenda/demo-git-action
docker build -t fastapi-app:latest .
```

---

### 5. Permission Denied During Build

**Error Message:**
```
permission denied while trying to connect to Docker daemon
```

**Solution:**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Restart Docker daemon (macOS)
# Docker Desktop → Preferences → Reset → Restart

# Or use sudo (not recommended for production)
sudo docker build -t fastapi-app:latest .
```

---

### 6. Cache Issues - Old Files Being Used

**Symptoms:**
- Changes not reflected in container
- Old dependencies still present

**Solution:**
```bash
# Build without cache
docker-compose build --no-cache app

# Remove old images
docker image prune -a

# Complete cleanup
docker system prune -a
docker-compose build app
```

---

### 7. Network Timeout During Build

**Error Message:**
```
Could not fetch URL https://pypi.org/simple/
```

**Solution:**
```bash
# Check internet connection
ping pypi.org

# Use a different PyPI mirror (add to Dockerfile before pip install)
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# Or configure pip retry
RUN pip install --retries 5 --timeout 30 -r requirements.txt
```

---

### 8. Multi-Platform Build Issues

**Error Message:**
```
no match for platform in manifest
```

**Solution:**
```bash
# Specify platform explicitly
docker build --platform linux/amd64 -t fastapi-app:latest .

# Or in docker-compose.yml:
services:
  app:
    platform: linux/amd64
    build: .
```

---

### 9. Layer Size Too Large

**Symptoms:**
- Slow builds
- Large image size

**Solution:**
```bash
# Combine RUN commands
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

# Clean up in same layer
RUN pip install -r requirements.txt && \
    rm -rf /root/.cache/pip

# Check layer sizes
docker history fastapi-app:latest
```

---

### 10. Entrypoint Script Not Executable

**Error Message:**
```
exec /app/entrypoint.sh: permission denied
```

**Solution:**
```bash
# Make script executable before COPY
chmod +x entrypoint.sh

# Or in Dockerfile after COPY
RUN chmod +x /app/entrypoint.sh

# Verify
docker run --rm fastapi-app:latest ls -la /app/entrypoint.sh
```

---

## Build Optimization Tips

### 1. Layer Caching Strategy
```dockerfile
# ✅ Good: Dependencies before code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app/src/

# ❌ Bad: Code and dependencies together
COPY . /app/
RUN pip install -r requirements.txt
```

### 2. Multi-Stage Builds (Optional)
```dockerfile
# Stage 1: Builder
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY src/ /app/src/
WORKDIR /app/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### 3. Minimize Installed Packages
```dockerfile
# Only install what you need
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

---

## Verification Commands

### Check Build is Successful
```bash
# Build and check exit code
docker build -t fastapi-app:latest . && echo "Build successful!"

# Check image exists
docker images | grep fastapi-app

# Inspect image
docker inspect fastapi-app:latest
```

### Test Image Locally
```bash
# Run with environment variables
docker run -d \
  --name test-app \
  -e DB_URL=postgresql://admin:admin1234@host.docker.internal:5432/fastapi \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -p 8000:8000 \
  fastapi-app:latest

# Check logs
docker logs test-app

# Test endpoint
curl http://localhost:8000/

# Cleanup
docker stop test-app && docker rm test-app
```

### Check Image Size
```bash
# View image size
docker images fastapi-app

# Analyze layers
docker history fastapi-app:latest --no-trunc

# Find large layers
docker history fastapi-app:latest --format "{{.Size}}\t{{.CreatedBy}}" | sort -h
```

---

## Quick Reference

### Essential Build Commands
```bash
# Standard build
docker build -t fastapi-app:latest .

# Build without cache
docker build --no-cache -t fastapi-app:latest .

# Build with progress
docker build --progress=plain -t fastapi-app:latest .

# Using docker-compose
docker-compose build app
docker-compose build --no-cache app
```

### Cleanup Commands
```bash
# Remove unused images
docker image prune

# Remove all unused containers, networks, images
docker system prune -a

# Remove specific image
docker rmi fastapi-app:latest

# Remove all stopped containers
docker container prune
```

---

## Current Dockerfile Dependencies

Our Dockerfile installs these system packages:

| Package | Purpose | Required For |
|---------|---------|--------------|
| `gcc` | GNU C compiler | Compiling C extensions |
| `g++` | GNU C++ compiler | Compiling C++ extensions |
| `make` | Build automation | Build process |
| `libc6-dev` | C standard library headers | stdlib.h, stdio.h, etc. |
| `python3-dev` | Python headers | Python C API |
| `postgresql-client` | PostgreSQL CLI tools | Database operations |

All dependencies are installed with `--no-install-recommends` to keep image size minimal.

---

## When to Rebuild

Rebuild the Docker image when:
- ✅ `requirements.txt` changes
- ✅ Source code changes (if not using volumes)
- ✅ Dockerfile is modified
- ✅ System dependencies change
- ✅ Base image is updated
- ✅ After pulling new code from git

```bash
# Quick rebuild and restart
docker-compose up -d --build app
```

---

## Getting Help

If you encounter an error not listed here:

1. **Check logs:**
   ```bash
   docker-compose logs app
   ```

2. **Build with verbose output:**
   ```bash
   docker build --progress=plain --no-cache -t fastapi-app:latest .
   ```

3. **Inspect the build context:**
   ```bash
   docker build -t fastapi-app:latest . --file Dockerfile --target <stage> --progress=plain
   ```

4. **Verify prerequisites:**
   - Docker version: `docker --version`
   - Docker Compose version: `docker-compose --version`
   - Disk space: `df -h`
   - Internet connectivity: `ping pypi.org`

---

**Current Status:** The Dockerfile has been fixed to include all necessary build dependencies. You should be able to build successfully now! 🎉
