# Update Endpoints Documentation

This document describes the update endpoints added to the API for modifying existing users and content.

## Overview

Two new PUT endpoints have been added:
1. **PUT /api/v1/users/{user_id}** - Update user information
2. **PUT /api/v1/content/{content_id}** - Update content

Both endpoints support partial updates (only provide the fields you want to change).

---

## User Update Endpoint

### Endpoint
```
PUT /api/v1/users/{user_id}
```

### Description
Update an existing user's information. Only the fields provided in the request will be updated.

### Request Body Schema
```json
{
  "name": "string (optional)",
  "email": "email@example.com (optional)",
  "phone_number": "+234xxxxxxxxxx (optional)"
}
```

### Validation Rules
- **name**: Must contain at least one alphabetic character (not just numbers)
- **email**: Must be a valid email format
- **phone_number**: Must start with +234 and have 8-11 additional digits

### Uniqueness Checks
- Email must be unique across all users
- Phone number must be unique across all users

### Example Requests

#### Update only name
```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated"
  }'
```

#### Update email and phone
```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "phone_number": "+234801234567"
  }'
```

#### Update all fields
```bash
curl -X PUT "http://localhost:8000/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe Updated",
    "email": "john.updated@example.com",
    "phone_number": "+234809876543"
  }'
```

### Response (200 OK)
```json
{
  "id": 1,
  "name": "John Doe Updated",
  "email": "john.updated@example.com",
  "phone_number": "+234809876543",
  "country": "Nigeria",
  "state": "Lagos",
  "created_at": "2024-01-15T10:30:00"
}
```

### Error Responses

#### 404 - User Not Found
```json
{
  "detail": "User with id 999 not found"
}
```

#### 400 - Email Already Exists
```json
{
  "detail": "Email already exists"
}
```

#### 400 - Phone Already Exists
```json
{
  "detail": "Phone number already exists"
}
```

#### 422 - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "Name must contain at least one alphabetic character",
      "type": "value_error"
    }
  ]
}
```

---

## Content Update Endpoint

### Endpoint
```
PUT /api/v1/content/{content_id}
```

### Description
Update an existing content item. Can update the image path and/or content text.

### Request Body Schema
```json
{
  "image": "string (optional)",
  "content": "string (optional)"
}
```

### Cache Invalidation
When content is updated, the following caches are invalidated:
- Specific content cache: `content:{content_id}`
- All contents list cache: `all_contents`
- Content with user cache: `content_with_user:*`

### Example Requests

#### Update only image
```bash
curl -X PUT "http://localhost:8000/api/v1/content/1" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "/path/to/new/image.jpg"
  }'
```

#### Update only content text
```bash
curl -X PUT "http://localhost:8000/api/v1/content/1" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is the updated content text"
  }'
```

#### Update both image and content
```bash
curl -X PUT "http://localhost:8000/api/v1/content/1" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "/path/to/new/image.jpg",
    "content": "This is the updated content text"
  }'
```

### Response (200 OK)
```json
{
  "id": 1,
  "user_id": 1,
  "content": "This is the updated content text",
  "image": "/path/to/new/image.jpg",
  "created_at": "2024-01-15T10:30:00"
}
```

### Error Responses

#### 404 - Content Not Found
```json
{
  "detail": "Content with id 999 not found"
}
```

---

## Implementation Details

### Service Layer

#### UserService.update_user()
- Fetches the user by ID
- Validates email/phone uniqueness if being changed
- Updates only the provided fields
- Commits changes to database
- Returns updated user

```python
@staticmethod
def update_user(session: Session, user_id: int, user_data: UpdateUserSchema) -> User:
    """
    Update existing user information.
    Checks for uniqueness of email and phone_number if being updated.
    """
    # Get existing user
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    
    if not user:
        return None
    
    # Check email uniqueness if being updated
    if user_data.email is not None and user_data.email != user.email:
        existing_email = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        if existing_email:
            raise ValueError("Email already exists")
    
    # Update and save...
```

#### ContentService.update_content()
- Fetches content by ID
- Updates provided fields (image, content)
- Invalidates related Redis caches
- Returns updated content

```python
@staticmethod
def update_content(session: Session, content_id: int, content_data: UpdateContentSchema) -> Content:
    """
    Update existing content.
    Invalidates cache after update.
    """
    # Get existing content
    statement = select(Content).where(Content.id == content_id)
    content = session.exec(statement).first()
    
    if not content:
        return None
    
    # Update fields if provided
    if content_data.image is not None:
        content.image = content_data.image
    
    if content_data.content is not None:
        content.content = content_data.content
    
    # Save and invalidate caches...
```

### Schemas

#### UpdateUserSchema
```python
class UpdateUserSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    @field_validator('name')
    def validate_name(cls, v):
        if v is not None and not any(c.isalpha() for c in v):
            raise ValueError('Name must contain at least one alphabetic character')
        return v

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            if not v.startswith('+234'):
                raise ValueError('Phone number must start with +234')
            digits_after_code = v[4:]
            if not digits_after_code.isdigit() or len(digits_after_code) < 8 or len(digits_after_code) > 11:
                raise ValueError('Phone number must have 8-11 digits after +234')
        return v
```

#### UpdateContentSchema
```python
class UpdateContentSchema(BaseModel):
    image: Optional[str] = None
    content: Optional[str] = None
```

---

## Testing the Endpoints

### Using Python Requests
```python
import requests

# Update user
response = requests.put(
    "http://localhost:8000/api/v1/users/1",
    json={
        "name": "Updated Name",
        "email": "new@email.com"
    }
)
print(response.json())

# Update content
response = requests.put(
    "http://localhost:8000/api/v1/content/1",
    json={
        "content": "New content text"
    }
)
print(response.json())
```

### Using HTTPie
```bash
# Update user
http PUT localhost:8000/api/v1/users/1 name="Updated Name" email="new@email.com"

# Update content
http PUT localhost:8000/api/v1/content/1 content="New content text"
```

---

## Notes

1. **Partial Updates**: Both endpoints support partial updates - you don't need to provide all fields, only the ones you want to change.

2. **Validation**: All validation rules from the create endpoints still apply to updates.

3. **Cache Management**: Content updates automatically invalidate related caches. User updates don't use caching (by design).

4. **Atomic Operations**: Each update is atomic - either all changes succeed or none do.

5. **Error Handling**: Proper error messages are returned for not found, validation errors, and uniqueness violations.

6. **Response Format**: Update endpoints return the same response format as the GET endpoints for the respective resources.
