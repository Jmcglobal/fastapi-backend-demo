# Setup and Deployment Guide

This guide will help you set up and run the FastAPI Content Management application.

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.9+**
   ```bash
   python3 --version
   ```

2. **PostgreSQL**
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

3. **Redis**
   ```bash
   # macOS
   brew install redis
   brew services start redis
   
   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis
   ```

## Quick Start

### 1. Setup Environment

Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```env
DB_URL=postgresql://username:password@localhost:5432/content_db
REDIS_URL=redis://localhost:6379/0
```

### 3. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE content_db;

# Create user (if needed)
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE content_db TO myuser;

# Exit
\q
```

### 4. Run Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Start the Application

```bash
chmod +x run.sh
./run.sh
```

Or manually:
```bash
cd src
python main.py
```

Or using uvicorn:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access the Application

- **API**: http://localhost:8000
- **Swagger Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_signup.py -v
```

### Run Tests with Coverage

```bash
pytest tests/ -v --cov=src --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Database Migrations

### Create a New Migration

After modifying models:
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

### View Migration History

```bash
alembic history
```

### Check Current Migration

```bash
alembic current
```

## Troubleshooting

### Issue: Cannot connect to PostgreSQL

**Solution:**
1. Check if PostgreSQL is running:
   ```bash
   # macOS
   brew services list
   
   # Linux
   sudo systemctl status postgresql
   ```

2. Verify connection details in `.env` file

3. Test connection:
   ```bash
   psql -h localhost -U username -d content_db
   ```

### Issue: Cannot connect to Redis

**Solution:**
1. Check if Redis is running:
   ```bash
   # macOS
   brew services list
   
   # Linux
   sudo systemctl status redis
   ```

2. Test Redis connection:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

### Issue: Import errors

**Solution:**
1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Issue: Alembic migration errors

**Solution:**
1. Check database connection in `.env`

2. Ensure models are imported in `alembic/env.py`

3. Drop and recreate database (development only):
   ```bash
   dropdb content_db
   createdb content_db
   alembic upgrade head
   ```

## Development Workflow

### 1. Adding a New Model

1. Create/modify model in `src/models/`
2. Import model in `alembic/env.py`
3. Create migration:
   ```bash
   alembic revision --autogenerate -m "Add new model"
   ```
4. Review the generated migration in `alembic/versions/`
5. Apply migration:
   ```bash
   alembic upgrade head
   ```

### 2. Adding a New Route

1. Create route handler in `src/routes/`
2. Add service logic in `src/services/`
3. Create schemas in `src/schemas.py`
4. Register router in `src/main.py`:
   ```python
   from src.routes.new_route import router as new_router
   app.include_router(new_router)
   ```

### 3. Adding Tests

1. Create test file in `tests/` (e.g., `test_new_feature.py`)
2. Write test cases
3. Run tests:
   ```bash
   pytest tests/test_new_feature.py -v
   ```

## Production Deployment

### Using Gunicorn (Recommended)

1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```

2. Run with Gunicorn:
   ```bash
   gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

### Using Docker

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. Create `docker-compose.yml`:
   ```yaml
   version: '3.8'
   
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DB_URL=postgresql://user:pass@db:5432/content_db
         - REDIS_URL=redis://redis:6379/0
       depends_on:
         - db
         - redis
     
     db:
       image: postgres:15
       environment:
         - POSTGRES_DB=content_db
         - POSTGRES_USER=user
         - POSTGRES_PASSWORD=pass
       volumes:
         - postgres_data:/var/lib/postgresql/data
     
     redis:
       image: redis:7-alpine
       volumes:
         - redis_data:/data
   
   volumes:
     postgres_data:
     redis_data:
   ```

3. Run:
   ```bash
   docker-compose up -d
   ```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |

## API Rate Limiting (Optional)

To add rate limiting, install:
```bash
pip install slowapi
```

Add to `src/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
@limiter.limit("5/minute")
def read_root(request: Request):
    return {"message": "Up and running"}
```

## Monitoring and Logging

Add logging to `src/main.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

## Security Best Practices

1. **Use environment variables** for sensitive data
2. **Enable CORS** only for trusted origins in production
3. **Use HTTPS** in production
4. **Implement authentication** (JWT, OAuth2)
5. **Validate all inputs** (already implemented)
6. **Use parameterized queries** (SQLModel handles this)
7. **Keep dependencies updated**: `pip list --outdated`

## Performance Optimization

1. **Database Indexing**: Already implemented on frequently queried fields
2. **Redis Caching**: Already implemented with 10-minute TTL
3. **Connection Pooling**: Configure in production:
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=0
   )
   ```

## Support

For issues or questions:
1. Check the [README.md](README.md)
2. Review [API_EXAMPLES.md](API_EXAMPLES.md)
3. Check application logs
4. Review test cases in `tests/`
