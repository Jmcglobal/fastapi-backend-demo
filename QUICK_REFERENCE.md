# Quick Reference Guide

## 🚀 Quick Start Commands

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Configure .env
# Edit with your PostgreSQL and Redis URLs

# 3. Create database
createdb content_db

# 4. Run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 5. Start server
cd src && python main.py

# 6. Run tests
pytest tests/ -v
```

## 📋 Environment Variables

```env
DB_URL=postgresql://username:password@localhost:5432/content_db
REDIS_URL=redis://localhost:6379/0
```

## 🔗 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/v1/signup` | Create user account |
| POST | `/api/v1/post-content` | Create content |
| GET | `/api/v1/content` | Get all content with users |
| GET | `/api/v1/content/{id}` | Get content by ID |
| GET | `/api/v1/users` | Get all users with content |
| GET | `/api/v1/users/{id}` | Get user by ID with content |

## 📦 Request/Response Examples

### Signup
```bash
curl -X POST http://localhost:8000/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+2348012345678",
    "country": "Nigeria",
    "state": "Lagos"
  }'
```

### Create Content
```bash
curl -X POST http://localhost:8000/api/v1/post-content \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Post",
    "content": "Content goes here",
    "user_id": 1
  }'
```

### Get All Content
```bash
curl http://localhost:8000/api/v1/content
```

## ✅ Validation Rules

### Name
- ✅ Must contain at least one alphabet character
- ❌ Cannot be only numbers (e.g., "12345678")
- ✅ Can contain numbers if it also has letters (e.g., "John123")
- 📏 Length: 2-100 characters

### Phone Number
- ✅ Must start with `+234`
- ✅ Must have 8-11 digits after `+234`
- ❌ Cannot have less than 8 digits: `+2341234567`
- ❌ Cannot have more than 11 digits: `+234123456789012`
- ✅ Valid: `+2348012345678` (8 digits)
- ✅ Valid: `+23412345678901` (11 digits)

### Email
- ✅ Must be valid email format
- ✅ Must be unique (not already registered)

## 🗄️ Database Schema

### Users Table
```sql
- id (PK, auto-increment)
- name (varchar, indexed)
- email (varchar, unique, indexed)
- phone_number (varchar, unique, indexed)
- country (varchar)
- state (varchar)
- created_at (timestamp)
```

### Contents Table
```sql
- id (PK, auto-increment)
- title (varchar, indexed)
- image (varchar, nullable)
- content (text)
- user_id (FK → users.id, indexed)
- created_at (timestamp)
```

## 🔄 Redis Caching Strategy

| Operation | Redis Behavior |
|-----------|----------------|
| **User Signup** | ❌ NOT cached - save directly to DB |
| **Get Users** | ❌ NOT cached - always from DB |
| **Get User by ID** | ❌ NOT cached - always from DB |
| **Create Content** | ❌ NOT cached - save to DB, invalidate content cache |
| **Get Content** | ✅ Cached for 10 minutes |
| **Get Content by ID** | ✅ Cached for 10 minutes |

### Cache Keys
- `content:{id}` - Individual content (10min TTL)
- `all_contents` - All contents list (10min TTL)
- `content_with_user:all` - Contents with users (10min TTL)

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_signup.py -v
```

### Run with Coverage
```bash
pytest tests/ -v --cov=src
```

### Test Cases Included
- ✅ Valid signup
- ✅ Name validation (rejects only numbers)
- ✅ Phone validation (format, length, prefix)
- ✅ Email validation
- ✅ Duplicate prevention
- ✅ Boundary conditions (8-11 digits)

## 🔧 Alembic Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View history
alembic history

# Check current version
alembic current
```

## 📚 Documentation URLs

After starting the server (http://localhost:8000):

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## 🐛 Troubleshooting

### PostgreSQL not connecting?
```bash
# Check if PostgreSQL is running
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# Test connection
psql -h localhost -U username -d content_db
```

### Redis not connecting?
```bash
# Check if Redis is running
brew services list  # macOS
sudo systemctl status redis  # Linux

# Test connection
redis-cli ping  # Should return: PONG
```

### Import errors?
```bash
# Ensure virtual environment is active
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Migration errors?
```bash
# Reset database (development only)
dropdb content_db
createdb content_db
alembic upgrade head
```

## 📁 Project Structure

```
demo-git-action/
├── src/
│   ├── models/              # Database models
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── database.py          # DB configuration
│   ├── redis_config.py      # Redis setup
│   ├── schemas.py           # Validation schemas
│   └── main.py             # FastAPI app
├── tests/                   # Test files
├── alembic/                # Migrations
├── requirements.txt        # Dependencies
├── .env                    # Environment vars
└── README.md              # Main documentation
```

## 🔐 Security Checklist

- ✅ Input validation via Pydantic schemas
- ✅ SQL injection prevention (SQLModel)
- ✅ Unique constraints on email/phone
- ✅ Environment variables for secrets
- ✅ CORS configuration
- ⚠️ Add authentication (JWT/OAuth2) for production
- ⚠️ Add rate limiting for production
- ⚠️ Use HTTPS in production

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```bash
docker-compose up -d
```

## 📊 Performance Tips

1. **Database**
   - Indexes already on key columns ✅
   - Use connection pooling in production
   - Consider read replicas for scaling

2. **Redis**
   - Content cached for 10 minutes ✅
   - Users NOT cached (always fresh) ✅
   - Tune TTL based on usage patterns

3. **API**
   - Enable GZIP compression
   - Add pagination for large lists
   - Consider GraphQL for flexible queries

## 📞 Support & Documentation

- **README.md** - Project overview
- **API_EXAMPLES.md** - Detailed API examples
- **SETUP_GUIDE.md** - Comprehensive setup guide
- **ARCHITECTURE.md** - System architecture details
- **This file** - Quick reference

## 🎯 Next Steps

1. ✅ Setup complete
2. ✅ Tests passing
3. ⬜ Add authentication
4. ⬜ Add pagination
5. ⬜ Deploy to production
6. ⬜ Add monitoring
