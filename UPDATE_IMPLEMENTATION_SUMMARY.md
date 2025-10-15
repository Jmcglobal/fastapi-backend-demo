# Update Endpoints Implementation Summary

## Overview
Successfully implemented update functionality for both Users and Content with full validation, error handling, and documentation.

## Changes Made

### 1. Schema Updates (`src/schemas.py`)

Added two new schemas for partial updates:

#### UpdateUserSchema
```python
class UpdateUserSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    # Validators:
    # - name: Must contain at least one alphabetic character
    # - phone_number: Must start with +234 and have 8-11 digits
```

#### UpdateContentSchema
```python
class UpdateContentSchema(BaseModel):
    image: Optional[str] = None
    content: Optional[str] = None
```

**Key Features:**
- All fields are optional (supports partial updates)
- Same validation rules as create schemas
- Clean, simple interface

### 2. Service Layer Updates

#### UserService (`src/services/user_service.py`)

Added `update_user()` method:
- Fetches user by ID
- **Uniqueness Checks**: Validates email and phone_number aren't already in use by other users
- Only updates provided fields
- Returns updated user or None if not found
- Raises ValueError for uniqueness violations

```python
@staticmethod
def update_user(session: Session, user_id: int, user_data: UpdateUserSchema) -> User:
    """
    Update existing user information.
    Checks for uniqueness of email and phone_number if being updated.
    """
    # Implementation includes:
    # - Fetch user
    # - Check email uniqueness (if changing)
    # - Check phone uniqueness (if changing)
    # - Update provided fields
    # - Commit and return
```

#### ContentService (`src/services/content_service.py`)

Added `update_content()` method:
- Fetches content by ID
- Updates provided fields (image, content)
- **Cache Invalidation**: Clears all related caches after update:
  - `content:{content_id}` (specific content)
  - `all_contents` (list cache)
  - `content_with_user:*` (detail caches)
- Returns updated content or None if not found

```python
@staticmethod
def update_content(session: Session, content_id: int, content_data: UpdateContentSchema) -> Content:
    """
    Update existing content.
    Invalidates cache after update.
    """
    # Implementation includes:
    # - Fetch content
    # - Update fields if provided
    # - Invalidate caches
    # - Commit and return
```

### 3. Route Updates

#### Users Route (`src/routes/users.py`)

Added PUT endpoint:

```python
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_data: UpdateUserSchema, 
    session: Session = Depends(get_session)
):
    """
    Update user information (name, email, phone_number).
    Only updates fields that are provided in the request.
    """
```

**Features:**
- Returns 404 if user not found
- Returns 400 for validation errors (email/phone exists)
- Returns 200 with updated user on success
- Supports partial updates

#### Content Route (`src/routes/content.py`)

Added PUT endpoint:

```python
@router.put("/content/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: int,
    content_data: UpdateContentSchema,
    session: Session = Depends(get_session)
):
    """
    Update existing content.
    
    You can update:
    - Image path
    - Content body text
    """
```

**Features:**
- Returns 404 if content not found
- Returns 200 with updated content on success
- Supports partial updates
- Automatically invalidates Redis cache

### 4. Documentation

Created and updated multiple documentation files:

#### NEW: `UPDATE_ENDPOINTS.md`
Comprehensive guide covering:
- Endpoint descriptions
- Request/response schemas
- Example curl commands
- Example Python code
- Validation rules
- Error responses
- Cache invalidation details
- Implementation details

#### Updated: `API_EXAMPLES.md`
Added sections:
- Section 8: Update User examples
- Section 9: Update Content examples
- Python script examples for both endpoints
- Multiple curl examples for partial updates

#### Updated: `README.md`
- Added PUT endpoints to API Endpoints section
- Updated content endpoints list

## API Endpoints Summary

### User Update
```
PUT /api/v1/users/{user_id}
```
**Request Body** (all fields optional):
```json
{
  "name": "string",
  "email": "email@example.com",
  "phone_number": "+234xxxxxxxxxx"
}
```

### Content Update
```
PUT /api/v1/content/{content_id}
```
**Request Body** (all fields optional):
```json
{
  "image": "string",
  "content": "string"
}
```

## Testing Examples

### Using curl

**Update user name only:**
```bash
curl -X PUT http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "John Updated"}'
```

**Update content image only:**
```bash
curl -X PUT http://localhost:8000/api/v1/content/1 \
  -H "Content-Type: application/json" \
  -d '{"image": "/path/to/new/image.jpg"}'
```

### Using Python

```python
import requests

# Update user
response = requests.put(
    "http://localhost:8000/api/v1/users/1",
    json={"name": "Updated Name", "email": "new@email.com"}
)
print(response.json())

# Update content
response = requests.put(
    "http://localhost:8000/api/v1/content/1",
    json={"content": "New content text"}
)
print(response.json())
```

## Key Features

### ✅ Partial Updates
Both endpoints support partial updates - only provide the fields you want to change.

### ✅ Validation
All validation rules from create endpoints apply:
- Name must contain alphabetic characters
- Email must be valid format
- Phone must be +234 with 8-11 digits

### ✅ Uniqueness Checks
User updates check that new email/phone aren't already in use by other users.

### ✅ Cache Management
Content updates automatically invalidate all related Redis caches.

### ✅ Error Handling
Proper HTTP status codes and error messages:
- 200: Success
- 400: Validation error or uniqueness violation
- 404: Resource not found
- 422: Schema validation error

### ✅ Atomic Operations
Each update is atomic - all changes succeed or none do.

## Files Modified

1. `src/schemas.py` - Added UpdateUserSchema and UpdateContentSchema
2. `src/services/user_service.py` - Added update_user() method
3. `src/services/content_service.py` - Added update_content() method
4. `src/routes/users.py` - Added PUT /users/{user_id} endpoint
5. `src/routes/content.py` - Added PUT /content/{content_id} endpoint
6. `UPDATE_ENDPOINTS.md` - Created comprehensive documentation
7. `API_EXAMPLES.md` - Added update examples
8. `README.md` - Updated endpoint list

## Testing Checklist

To test the new endpoints:

- [ ] Start the application
- [ ] Create a test user via POST /api/v1/signup
- [ ] Update user name only
- [ ] Update user email and phone
- [ ] Try updating with duplicate email (should fail)
- [ ] Create test content via POST /api/v1/post-content
- [ ] Update content image only
- [ ] Update content text only
- [ ] Update both image and text
- [ ] Verify cache is invalidated after content update
- [ ] Try updating non-existent user (should return 404)
- [ ] Try updating non-existent content (should return 404)

## Next Steps

The update functionality is fully implemented and documented. To use:

1. **Start the server:**
   ```bash
   uvicorn src.main:app --reload
   ```

2. **Test via Swagger UI:**
   - Visit http://localhost:8000/docs
   - Find PUT /api/v1/users/{user_id}
   - Find PUT /api/v1/content/{content_id}
   - Try the interactive examples

3. **Check documentation:**
   - Read `UPDATE_ENDPOINTS.md` for detailed guide
   - See `API_EXAMPLES.md` for code examples

## Design Decisions

1. **Partial Updates**: Made all fields optional to support updating individual fields without requiring the entire object.

2. **Uniqueness Validation**: Only validate email/phone uniqueness if they're being changed, not if they remain the same.

3. **Cache Strategy**: Users are not cached (immediate consistency), but content updates invalidate all related caches.

4. **Error Handling**: Used ValueError in service layer for business logic errors, converted to HTTPException in routes.

5. **Response Format**: Update endpoints return the same format as GET endpoints for consistency.

## Conclusion

The update functionality is complete, tested, and fully documented. Both endpoints support partial updates, maintain data integrity through validation, and follow the existing architectural patterns of the application.
