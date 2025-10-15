# Quick Start Guide: Update Endpoints

## Overview
This guide shows you how to quickly start using the new update endpoints for Users and Content.

## Prerequisites
- Server must be running: `uvicorn src.main:app --reload`
- Database must be set up: `alembic upgrade head`
- At least one user and content item created

## Quick Examples

### 1. Update User Name

**Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'
```

**Response:**
```json
{
  "id": 1,
  "name": "New Name",
  "email": "user@example.com",
  "phone_number": "+234801234567",
  "country": "Nigeria",
  "state": "Lagos",
  "created_at": "2024-01-15T10:30:00"
}
```

### 2. Update User Email and Phone

**Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "phone_number": "+234809876543"
  }'
```

### 3. Update Content Image

**Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{"image": "/path/to/new/image.jpg"}'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "content": "Original content text",
  "image": "/path/to/new/image.jpg",
  "created_at": "2024-01-15T10:30:00"
}
```

### 4. Update Content Text

**Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated content text"}'
```

### 5. Update Both Content Fields

**Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{
    "image": "/path/to/new/image.jpg",
    "content": "Updated content text"
  }'
```

## Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Update user
response = requests.put(
    f"{BASE_URL}/api/v1/users/1",
    json={"name": "Updated Name"}
)
print(response.json())

# Update content
response = requests.put(
    f"{BASE_URL}/api/v1/content/1",
    json={
        "image": "/new/image.jpg",
        "content": "New text"
    }
)
print(response.json())
```

## Running the Test Suite

We've included a comprehensive test script:

```bash
# Make sure server is running first
uvicorn src.main:app --reload

# In another terminal, run the test
python test_update_endpoints.py
```

The test script will:
- ✅ Create a test user
- ✅ Update user name
- ✅ Update user email and phone
- ✅ Test validation
- ✅ Create test content
- ✅ Update content image
- ✅ Update content text
- ✅ Update both fields
- ✅ Test 404 responses

## Using Swagger UI

1. Open http://localhost:8000/docs
2. Scroll to "content" or "users" section
3. Find the PUT endpoints
4. Click "Try it out"
5. Fill in the ID and request body
6. Click "Execute"

## Common Use Cases

### Change User's Email
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email": "newemail@example.com"}'
```

### Change User's Phone Number
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+234801111111"}'
```

### Update Content's Image Path
```bash
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{"image": "/Users/user/newimage.png"}'
```

### Fix Typo in Content
```bash
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{"content": "Corrected text here"}'
```

## Error Handling

### User Not Found (404)
```bash
curl -X PUT http://localhost:8000/api/v1/users/99999 \
  -H "Content-Type: application/json" \
  -d '{"name": "Test"}'
```
Response:
```json
{
  "detail": "User with id 99999 not found"
}
```

### Email Already Exists (400)
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email": "existing@example.com"}'
```
Response:
```json
{
  "detail": "Email already exists"
}
```

### Invalid Name (422)
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "12345"}'
```
Response:
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "Name must contain at least one alphabetic character"
    }
  ]
}
```

## Validation Rules

### User Updates
- **name**: Must contain at least one letter (not just numbers)
- **email**: Must be valid email format and unique
- **phone_number**: Must start with +234 and have 8-11 additional digits, must be unique

### Content Updates
- **image**: Any string (file path)
- **content**: Any string (text content)

## Key Features

✅ **Partial Updates** - Only send the fields you want to change
✅ **Validation** - Same rules as create endpoints
✅ **Uniqueness** - Email and phone checked for duplicates
✅ **Cache Invalidation** - Content updates clear Redis cache automatically
✅ **Error Messages** - Clear, actionable error responses
✅ **Status Codes** - Proper HTTP codes (200, 400, 404, 422)

## Complete Workflow Example

```bash
# 1. Create a user
curl -X POST http://localhost:8000/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+234801234567",
    "country": "Nigeria",
    "state": "Lagos"
  }'

# 2. Create content for that user
curl -X POST http://localhost:8000/api/v1/post-content \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Post",
    "image": "/path/to/image.jpg",
    "content": "Original content",
    "user_id": 1
  }'

# 3. Update the user's name
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Updated"}'

# 4. Update the content text
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated content text"}'

# 5. Get the updated user with content
curl http://localhost:8000/api/v1/users/1

# 6. Get the updated content
curl http://localhost:8000/api/v1/content/1
```

## Troubleshooting

### Server Not Responding
```bash
# Check if server is running
curl http://localhost:8000/

# If not, start it:
uvicorn src.main:app --reload
```

### Database Not Set Up
```bash
# Run migrations
alembic upgrade head
```

### Redis Not Running
```bash
# Check Redis connection in .env
# Start Redis if needed:
redis-server

# Or use Docker:
docker-compose up -d redis
```

## Next Steps

- Read `UPDATE_ENDPOINTS.md` for detailed documentation
- Check `API_EXAMPLES.md` for more examples
- Run `test_update_endpoints.py` for automated testing
- Explore the Swagger UI at http://localhost:8000/docs

## Support

For more information:
- **Full Documentation**: See `UPDATE_ENDPOINTS.md`
- **API Examples**: See `API_EXAMPLES.md`
- **Implementation Details**: See `UPDATE_IMPLEMENTATION_SUMMARY.md`
- **Interactive Docs**: Visit http://localhost:8000/docs
