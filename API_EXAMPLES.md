# API Usage Examples

This document provides examples of how to use the API endpoints.

## Base URL
```
http://localhost:8000
```

## 1. Health Check

**Endpoint:** `GET /`

**Example:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Up and running"
}
```

## 2. User Signup

**Endpoint:** `POST /api/v1/signup`

**Valid Request:**
```bash
curl -X POST http://localhost:8000/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone_number": "+2348012345678",
    "country": "Nigeria",
    "state": "Lagos"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone_number": "+2348012345678",
  "country": "Nigeria",
  "state": "Lagos",
  "created_at": "2025-10-15T12:00:00"
}
```

**Invalid Request (Name with only numbers):**
```bash
curl -X POST http://localhost:8000/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "12345678",
    "email": "test@example.com",
    "phone_number": "+2348012345678",
    "country": "Nigeria",
    "state": "Lagos"
  }'
```

**Response (422 Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "Name cannot be only numbers",
      "type": "value_error"
    }
  ]
}
```

**Invalid Request (Phone number too short):**
```bash
curl -X POST http://localhost:8000/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone_number": "+2341234567",
    "country": "Nigeria",
    "state": "Lagos"
  }'
```

## 3. Post Content

**Endpoint:** `POST /api/v1/post-content`

### Method 1: With Image File Path

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/post-content \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Blog Post",
    "image": "/Users/macpro/Documents/myimage.png",
    "content": "This is the content of my first blog post. It contains interesting information.",
    "user_id": 1
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "My First Blog Post",
  "image": "/Users/macpro/Documents/myimage.png",
  "content": "This is the content of my first blog post. It contains interesting information.",
  "user_id": 1,
  "created_at": "2025-10-15T12:05:00"
}
```

### Method 2: With File Upload

**Endpoint:** `POST /api/v1/post-content-upload`

**Request (Form Data):**
```bash
curl -X POST http://localhost:8000/api/v1/post-content-upload \
  -F "title=My First Blog Post" \
  -F "content=This is the content of my first blog post." \
  -F "user_id=1" \
  -F "image=@/Users/macpro/Documents/myimage.png"
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "My First Blog Post",
  "image": "/absolute/path/to/uploads/20251015_120500_myimage.png",
  "content": "This is the content of my first blog post.",
  "user_id": 1,
  "created_at": "2025-10-15T12:05:00"
}
```

**Supported Image Formats:**
- .jpg / .jpeg
- .png
- .gif
- .webp
- .bmp

**Request (Without image):**
```bash
curl -X POST http://localhost:8000/api/v1/post-content \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Text Only Post",
    "content": "This post has no image attached.",
    "user_id": 1
  }'
```

## 4. Get All Content with Users

**Endpoint:** `GET /api/v1/content`

**Request:**
```bash
curl http://localhost:8000/api/v1/content
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "My First Blog Post",
    "image": "https://example.com/image.jpg",
    "content": "This is the content of my first blog post.",
    "user_id": 1,
    "created_at": "2025-10-15T12:05:00",
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone_number": "+2348012345678",
      "country": "Nigeria",
      "state": "Lagos"
    }
  }
]
```

## 5. Get Content by ID

**Endpoint:** `GET /api/v1/content/{id}`

**Request:**
```bash
curl http://localhost:8000/api/v1/content/1
```

**Response:**
```json
{
  "id": 1,
  "title": "My First Blog Post",
  "image": "https://example.com/image.jpg",
  "content": "This is the content of my first blog post.",
  "user_id": 1,
  "created_at": "2025-10-15T12:05:00",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone_number": "+2348012345678",
    "country": "Nigeria",
    "state": "Lagos"
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Content with id 999 not found"
}
```

## 6. Get All Users with Content

**Endpoint:** `GET /api/v1/users`

**Request:**
```bash
curl http://localhost:8000/api/v1/users
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone_number": "+2348012345678",
    "country": "Nigeria",
    "state": "Lagos",
    "created_at": "2025-10-15T12:00:00",
    "contents": [
      {
        "id": 1,
        "title": "My First Blog Post",
        "image": "https://example.com/image.jpg",
        "content": "This is the content of my first blog post.",
        "user_id": 1,
        "created_at": "2025-10-15T12:05:00"
      },
      {
        "id": 2,
        "title": "Text Only Post",
        "image": null,
        "content": "This post has no image attached.",
        "user_id": 1,
        "created_at": "2025-10-15T12:10:00"
      }
    ]
  }
]
```

## 7. Get User by ID with Content

**Endpoint:** `GET /api/v1/users/{id}`

**Request:**
```bash
curl http://localhost:8000/api/v1/users/1
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone_number": "+2348012345678",
  "country": "Nigeria",
  "state": "Lagos",
  "created_at": "2025-10-15T12:00:00",
  "contents": [
    {
      "id": 1,
      "title": "My First Blog Post",
      "image": "https://example.com/image.jpg",
      "content": "This is the content of my first blog post.",
      "user_id": 1,
      "created_at": "2025-10-15T12:05:00"
    }
  ]
}
```

## 8. Update User

**Endpoint:** `PUT /api/v1/users/{user_id}`

**Description:** Update user information (partial update supported)

**Update Name Only:**
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated"
  }'
```

**Update Email and Phone:**
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.updated@example.com",
    "phone_number": "+234809876543"
  }'
```

**Update All Fields:**
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe Updated",
    "email": "john.new@example.com",
    "phone_number": "+234801111111"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe Updated",
  "email": "john.new@example.com",
  "phone_number": "+234801111111",
  "country": "Nigeria",
  "state": "Lagos",
  "created_at": "2025-10-15T12:00:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "User with id 999 not found"
}
```

**Response (400 Bad Request - Email Exists):**
```json
{
  "detail": "Email already exists"
}
```

## 9. Update Content

**Endpoint:** `PUT /api/v1/content/{content_id}`

**Description:** Update content image and/or text (partial update supported)

**Update Image Only:**
```bash
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{
    "image": "/path/to/new/image.jpg"
  }'
```

**Update Content Text Only:**
```bash
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is the updated content text"
  }'
```

**Update Both:**
```bash
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{
    "image": "/path/to/new/image.jpg",
    "content": "This is the updated content text"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "content": "This is the updated content text",
  "image": "/path/to/new/image.jpg",
  "created_at": "2025-10-15T12:05:00"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Content with id 999 not found"
}
```

## Testing Phone Number Validation

### Valid Phone Numbers
- `+2348012345678` (8 digits)
- `+234801234567890` (11 digits)
- `+23480123456789` (10 digits)

### Invalid Phone Numbers
- `+2341234567` (only 7 digits - too short)
- `+234123456789012` (12 digits - too long)
- `+2358012345678` (wrong country code)
- `080123456789` (missing + and country code)
- `+234801234ABC8` (contains letters)

## Testing Name Validation

### Valid Names
- `John Doe`
- `Jane Smith`
- `Ahmed Ali 123` (can contain numbers if also has letters)
- `O'Brien`
- `Mary-Jane`

### Invalid Names
- `12345678901` (only numbers)
- `123 456` (no alphabet characters)
- `A` (too short, minimum 2 characters)

## Python Example Using `requests`

```python
import requests

BASE_URL = "http://localhost:8000"

# Signup
signup_data = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone_number": "+2348012345678",
    "country": "Nigeria",
    "state": "Lagos"
}
response = requests.post(f"{BASE_URL}/api/v1/signup", json=signup_data)
print(f"Signup: {response.status_code}")
user = response.json()
print(user)

# Post content
content_data = {
    "title": "My First Post",
    "content": "This is my first post content.",
    "user_id": user["id"]
}
response = requests.post(f"{BASE_URL}/api/v1/post-content", json=content_data)
print(f"Post Content: {response.status_code}")
content = response.json()
print(content)

# Get all content
response = requests.get(f"{BASE_URL}/api/v1/content")
print(f"Get All Content: {response.status_code}")
all_content = response.json()
print(all_content)

# Get content by ID
response = requests.get(f"{BASE_URL}/api/v1/content/{content['id']}")
print(f"Get Content by ID: {response.status_code}")
single_content = response.json()
print(single_content)

# Get all users
response = requests.get(f"{BASE_URL}/api/v1/users")
print(f"Get All Users: {response.status_code}")
all_users = response.json()
print(all_users)

# Get user by ID
response = requests.get(f"{BASE_URL}/api/v1/users/{user['id']}")
print(f"Get User by ID: {response.status_code}")
single_user = response.json()
print(single_user)

# Update user
update_user_data = {
    "name": "John Updated",
    "email": "john.updated@example.com"
}
response = requests.put(f"{BASE_URL}/api/v1/users/{user['id']}", json=update_user_data)
print(f"Update User: {response.status_code}")
updated_user = response.json()
print(updated_user)

# Update content
update_content_data = {
    "content": "This is updated content text",
    "image": "/path/to/new/image.jpg"
}
response = requests.put(f"{BASE_URL}/api/v1/content/{content['id']}", json=update_content_data)
print(f"Update Content: {response.status_code}")
updated_content = response.json()
print(updated_content)
```
