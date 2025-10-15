# 🐳 Docker Deployment

Quick reference for deploying the FastAPI application using Docker.

## Quick Start

```bash
# Option 1: Using the quick start script
chmod +x docker-start.sh
./docker-start.sh

# Option 2: Using docker-compose directly
docker-compose up -d --build
```

Access the application at:
- **API**: http://localhost:8000
- **Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## What's Included

### Services
- **FastAPI App** - Python 3.12, runs on port 8000
- **PostgreSQL** - Database, port 5432
- **Redis** - Cache, port 6379

### Security Features
- ✅ Non-root user (UID: 1000, GID: 1000)
- ✅ No home directory
- ✅ Proper file permissions
- ✅ Minimal base image
- ✅ Health checks enabled

## File Structure

```
📁 Docker Files
├── Dockerfile              # Main container definition
├── docker-compose.yml      # Multi-service orchestration
├── .dockerignore          # Excludes unnecessary files
├── entrypoint.sh          # Startup script (auto-migrations)
├── docker-start.sh        # Quick start helper
├── .env.docker            # Environment template
├── DOCKER_GUIDE.md        # Comprehensive guide
└── DOCKER_SUMMARY.md      # Implementation details
```

## Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild app
docker-compose up -d --build app

# Run migrations
docker-compose exec app alembic upgrade head

# Access shell
docker-compose exec app bash

# Check status
docker-compose ps
```

## Environment Variables

Configure in `docker-compose.yml`:
```yaml
environment:
  - DB_URL=postgresql://admin:admin1234@postgres:5432/fastapi
  - REDIS_URL=redis://redis:6379/0
```

## Troubleshooting

### Services won't start
```bash
docker-compose logs app
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d --build
```

### Permission issues
```bash
docker-compose exec --user root app chown -R appuser:appgroup /app
```

## Documentation

- **DOCKER_GUIDE.md** - Complete usage guide with examples
- **DOCKER_SUMMARY.md** - Implementation details and architecture

## Technical Details

- **Base Image**: `python:3.12-slim`
- **Working Directory**: `/app/src`
- **Application User**: `appuser` (UID: 1000)
- **Application Group**: `appgroup` (GID: 1000)
- **Migrations**: Run automatically on startup via `entrypoint.sh`

---

For detailed information, see [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
