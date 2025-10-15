# Content Management API

A FastAPI backend application with PostgreSQL and Redis integration.

## Features

- ✅ FastAPI with automatic API documentation (Swagger UI and ReDoc)
- ✅ PostgreSQL database with SQLModel ORM
- ✅ Redis caching with 10-minute TTL
- ✅ Alembic database migrations
- ✅ Comprehensive input validation
- ✅ RESTful API endpoints
- ✅ Service layer architecture
- ✅ Relationship management between Users and Content
- ✅ Indexing for fast queries

## Prerequisites

- Python 3.9+
- PostgreSQL
- Redis

## Installation

1. Clone the repository:
```bash
cd demo-git-action
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Update the `.env` file with your database credentials:
```
DB_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
```

## Database Setup

1. Create the database:
```bash
createdb dbname  # or use your PostgreSQL client
```

2. Run migrations:
```bash
alembic upgrade head
```

If you need to create a new migration after modifying models:
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Running the Application

Start the FastAPI server:
```bash
cd src
python main.py
```

Or use uvicorn directly:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Root
- `GET /` - Health check (returns "Up and running")

### Users
- `POST /api/v1/signup` - Create a new user account
- `GET /api/v1/users` - Get all users with their content
- `GET /api/v1/users/{id}` - Get a specific user with their content
- `PUT /api/v1/users/{id}` - Update user information (name, email, phone)

### Content
- `POST /api/v1/post-content` - Create new content (with image file path)
- `GET /api/v1/content` - Get all content with user information
- `GET /api/v1/content/{id}` - Get specific content with user information
- `PUT /api/v1/content/{id}` - Update content (image and/or text)
- `GET /api/v1/content` - Get all content with user information
- `GET /api/v1/content/{id}` - Get specific content by ID

## Validation Rules

### Signup
- **Name**: Must contain at least one alphabet character, cannot be only numbers
- **Email**: Valid email format
- **Phone Number**: Must start with `+234` and have 8-11 digits after the prefix
- **Country**: 2-100 characters
- **State**: 2-100 characters

### Post Content
- **Title**: 3-200 characters
- **Image**: Optional - accepts either:
  - File path (e.g., `/Users/macpro/myimage.png`) - for `/post-content` endpoint
  - File upload - for `/post-content-upload` endpoint
  - Supported formats: .jpg, .jpeg, .png, .gif, .webp, .bmp
- **Content**: Minimum 10 characters
- **User ID**: Valid user ID (must exist)

## Redis Caching Strategy

- **User Signup**: Saved directly to PostgreSQL (no Redis caching)
- **User Retrieval**: NOT cached - always fetched from PostgreSQL
- **Content**: Cached with 10-minute TTL
  - If content is not in Redis, it's fetched from DB and cached
  - If content is not accessed within 10 minutes, it expires from cache
- **All Content List**: Cached and invalidated when new content is added

## Testing

Run the tests:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ -v --cov=src
```

## Project Structure

```
demo-git-action/
├── alembic/                 # Database migrations
│   ├── versions/           # Migration scripts
│   ├── env.py             # Alembic environment
│   └── script.py.mako     # Migration template
├── src/                    # Main application code
│   ├── models/            # SQLModel database models
│   │   ├── user.py
│   │   └── content.py
│   ├── routes/            # API route handlers
│   │   ├── users.py
│   │   └── content.py
│   ├── services/          # Business logic layer
│   │   ├── user_service.py
│   │   └── content_service.py
│   ├── database.py        # Database configuration
│   ├── redis_config.py    # Redis configuration
│   ├── schemas.py         # Pydantic validation schemas
│   └── main.py           # FastAPI application
├── tests/                 # Test files
│   └── test_signup.py
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Database Schema

### Users Table
- `id`: Primary key
- `name`: User's full name (indexed)
- `email`: Unique email address (indexed)
- `phone_number`: Unique phone number (indexed)
- `country`: Country name
- `state`: State/region name
- `created_at`: Timestamp

### Contents Table
- `id`: Primary key
- `title`: Content title (indexed)
- `image`: Optional image URL
- `content`: Content text
- `user_id`: Foreign key to users table (indexed)
- `created_at`: Timestamp

**Relationship**: One User can have many Contents (One-to-Many)

## License

MIT
