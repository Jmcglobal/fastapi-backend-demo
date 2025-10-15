# System Architecture

## Overview

This document describes the architecture and data flow of the Content Management API.

## Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Cache**: Redis
- **ORM**: SQLModel
- **Migrations**: Alembic
- **Testing**: Pytest

## Architecture Layers

```
┌─────────────────────────────────────────────┐
│            FastAPI Application              │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Routes  │  │  Schemas │  │  Main.py │ │
│  └────┬─────┘  └──────────┘  └──────────┘ │
│       │                                     │
│  ┌────▼──────────────────────────────┐    │
│  │        Service Layer              │    │
│  │  (Business Logic & Caching)       │    │
│  └────┬─────────────────┬────────────┘    │
│       │                 │                   │
└───────┼─────────────────┼───────────────────┘
        │                 │
   ┌────▼────┐       ┌────▼────┐
   │  Redis  │       │ PostgreSQL│
   │  Cache  │       │ Database │
   └─────────┘       └──────────┘
```

## Data Flow

### 1. User Signup Flow

```
User Request (POST /api/v1/signup)
    │
    ▼
Schema Validation (SignupSchema)
    │
    ├─ Name validation (must contain alphabets)
    ├─ Email validation (EmailStr)
    ├─ Phone validation (+234, 8-11 digits)
    ├─ Country & State validation
    │
    ▼
Route Handler (users.py)
    │
    ├─ Check email uniqueness (DB query)
    ├─ Check phone uniqueness (DB query)
    │
    ▼
User Service (create_user)
    │
    └─ Save directly to PostgreSQL
        └─ INSERT INTO users table
        └─ COMMIT transaction
    │
    ▼
Return User Object (201 Created)
```

**Key Points:**
- Users are saved directly to PostgreSQL
- No Redis caching for user signup
- User retrieval is **NOT cached** - always fetched from DB
- Ensures data consistency and freshness

### 2. Content Creation Flow

```
User Request (POST /api/v1/post-content)
    │
    ▼
Schema Validation (PostContentSchema)
    │
    ├─ Title validation (3-200 chars)
    ├─ Content validation (min 10 chars)
    ├─ Image validation (optional)
    ├─ User ID validation (required)
    │
    ▼
Route Handler (content.py)
    │
    └─ Verify user exists (DB query)
    │
    ▼
Content Service (create_content)
    │
    ├─ INSERT INTO contents table
    ├─ COMMIT transaction
    │
    ├─ Invalidate Redis cache
    │   ├─ Delete: all_contents
    │   └─ Delete: content_with_user:*
    │
    ▼
Return Content Object (201 Created)
```

**Key Points:**
- Verifies user exists before creating content
- Invalidates related caches to ensure fresh data
- Foreign key constraint ensures referential integrity

### 3. Get All Content Flow

```
User Request (GET /api/v1/content)
    │
    ▼
Route Handler (content.py)
    │
    ▼
Content Service (get_contents_with_users)
    │
    ├─ Check Redis cache
    │   Key: content_with_user:all
    │
    ├─ IF CACHE HIT
    │   └─ Return cached data
    │
    ├─ IF CACHE MISS
    │   ├─ Query PostgreSQL (JOIN users)
    │   ├─ Transform to dict format
    │   ├─ Store in Redis (TTL: 10 minutes)
    │   └─ Return data
    │
    ▼
Return Content List with Users (200 OK)
```

**Key Points:**
- Redis cache checked first
- 10-minute TTL on cached content
- Cache automatically expires if not accessed
- Joins content with user data efficiently

### 4. Get Content by ID Flow

```
User Request (GET /api/v1/content/{id})
    │
    ▼
Route Handler (content.py)
    │
    ▼
Content Service (get_content_by_id)
    │
    ├─ Check Redis cache
    │   Key: content:{id}
    │
    ├─ IF CACHE HIT
    │   └─ Return cached content
    │
    ├─ IF CACHE MISS
    │   ├─ Query PostgreSQL
    │   ├─ Store in Redis (TTL: 10 minutes)
    │   └─ Return content
    │
    ├─ IF NOT FOUND
    │   └─ Raise 404 HTTPException
    │
    ▼
Return Content with User (200 OK)
```

**Key Points:**
- Individual content items are cached
- Each access resets the 10-minute TTL
- Content not accessed for 10 minutes expires from cache

### 5. Get All Users Flow

```
User Request (GET /api/v1/users)
    │
    ▼
Route Handler (users.py)
    │
    ▼
User Service (get_all_users)
    │
    └─ Query PostgreSQL (NO CACHE)
    │   └─ SELECT * FROM users
    │   └─ Include relationships (contents)
    │
    ▼
Return Users with Contents (200 OK)
```

**Key Points:**
- User data is **NOT cached**
- Always fetched from database for accuracy
- Includes relationship with user's content

### 6. Get User by ID Flow

```
User Request (GET /api/v1/users/{id})
    │
    ▼
Route Handler (users.py)
    │
    ▼
User Service (get_user_by_id)
    │
    └─ Query PostgreSQL (NO CACHE)
    │   └─ SELECT * FROM users WHERE id = ?
    │   └─ Include relationships (contents)
    │
    ├─ IF NOT FOUND
    │   └─ Raise 404 HTTPException
    │
    ▼
Return User with Contents (200 OK)
```

**Key Points:**
- User retrieval is **NOT cached**
- Ensures latest user data is always returned
- Includes all content created by the user

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    phone_number VARCHAR UNIQUE NOT NULL,
    country VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone_number);
```

### Contents Table

```sql
CREATE TABLE contents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    image VARCHAR,
    content TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX idx_contents_title ON contents(title);
CREATE INDEX idx_contents_user_id ON contents(user_id);
```

### Relationships

- **One-to-Many**: One User can have many Contents
- **Foreign Key**: contents.user_id → users.id
- **Cascade**: Defined in application layer

## Redis Cache Keys

| Key Pattern | Usage | TTL | Example |
|-------------|-------|-----|---------|
| `content:{id}` | Individual content cache | 10min | `content:123` |
| `all_contents` | All contents list | 10min | `all_contents` |
| `content_with_user:all` | Contents with user data | 10min | `content_with_user:all` |

## Caching Strategy Summary

| Resource | Create | Read | Update | Delete |
|----------|--------|------|--------|--------|
| **Users** | ❌ No cache (DB only) | ❌ No cache (DB only) | N/A | N/A |
| **Content** | ❌ DB only, invalidate cache | ✅ Redis (10min TTL) | N/A | N/A |

### Why Users are NOT Cached?

1. **Data Freshness**: User data should always be up-to-date
2. **Security**: Ensures latest user state is retrieved
3. **Simplicity**: No cache invalidation needed for user operations
4. **Low Volume**: User queries are typically less frequent than content queries
5. **Consistency**: Direct database operations ensure data integrity

### Why Content IS Cached?

1. **High Volume**: Content is read more frequently than users
2. **Performance**: Reduces database load for popular content
3. **Acceptable Staleness**: 10-minute TTL balances freshness and performance
4. **Read-Heavy**: Content is read much more than written

## Performance Optimizations

### Database Level
- **Indexes** on frequently queried columns
- **Foreign keys** for referential integrity
- **Connection pooling** (configurable in production)

### Application Level
- **Service layer** separates business logic
- **Dependency injection** for database sessions
- **Async-ready** architecture (can add async/await)

### Cache Level
- **TTL-based expiration** (10 minutes for content)
- **Pattern-based invalidation** on updates
- **Selective caching** (content only, not users)

## Error Handling

### Validation Errors (422)
- Schema validation failures
- Invalid phone number format
- Invalid email format
- Name validation failures

### Client Errors (400)
- Duplicate email
- Duplicate phone number

### Not Found (404)
- User not found
- Content not found

### Server Errors (500)
- Database connection failures
- Redis connection failures
- Unexpected errors

## Security Considerations

1. **Input Validation**: All inputs validated via Pydantic schemas
2. **SQL Injection**: Prevented by SQLModel parameterized queries
3. **Unique Constraints**: Email and phone number uniqueness enforced
4. **Environment Variables**: Sensitive data in .env file
5. **CORS**: Configurable per environment

## Scalability Considerations

### Horizontal Scaling
- Stateless application design
- Redis for shared cache across instances
- PostgreSQL connection pooling

### Database Scaling
- Read replicas for heavy read operations
- Indexes already in place
- Partitioning strategy for large datasets

### Cache Scaling
- Redis Cluster for distributed caching
- Cache warming strategies
- TTL tuning based on usage patterns

## Monitoring & Observability

### Recommended Metrics
- API response times
- Database query performance
- Redis cache hit/miss ratio
- Error rates by endpoint
- Active database connections

### Logging
- Request/response logging
- Error logging with stack traces
- Database query logging (development)
- Cache operations logging

## Future Enhancements

1. **Authentication & Authorization**
   - JWT tokens
   - Role-based access control
   - API key management

2. **Content Features**
   - Update content endpoint
   - Delete content endpoint
   - Content pagination
   - Content search/filtering

3. **User Features**
   - Update user profile
   - User authentication
   - Password management

4. **Performance**
   - GraphQL for flexible queries
   - Async database operations
   - CDN for image hosting
   - Full-text search (Elasticsearch)

5. **Operations**
   - Health check endpoints
   - Metrics endpoint (Prometheus)
   - Rate limiting
   - Request tracing
