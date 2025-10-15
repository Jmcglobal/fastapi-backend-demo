# Image Upload Feature - Documentation

## Overview

The content creation endpoints now support two methods for handling images:
1. **Image File Path** - Provide a local file path to an existing image
2. **File Upload** - Upload an image file directly via form-data

---

## 📋 Endpoints

### 1. POST /api/v1/post-content (JSON with File Path)

**Method:** POST  
**Content-Type:** application/json  
**Body Format:** JSON

#### Description
Create content by providing an image file path. The file path must exist on the server/local system.

#### Request Body
```json
{
  "title": "My Post Title",
  "image": "/Users/macpro/Documents/myimage.png",
  "content": "This is my content...",
  "user_id": 1
}
```

#### Image Field
- **Type**: String (optional)
- **Description**: Full file path to an image on your computer
- **Example**: `/Users/macpro/Documents/myimage.png`
- **Validation**: 
  - File must exist at the specified path
  - Must be a valid file (not a directory)
  - Must have allowed extension: .jpg, .jpeg, .png, .gif, .webp, .bmp

#### Example Request
```bash
curl -X POST http://localhost:8000/api/v1/post-content \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Blog Post",
    "image": "/Users/macpro/Downloads/sunset.jpg",
    "content": "Beautiful sunset photo from my trip.",
    "user_id": 1
  }'
```

#### Response (201 Created)
```json
{
  "id": 1,
  "title": "My Blog Post",
  "image": "/Users/macpro/Downloads/sunset.jpg",
  "content": "Beautiful sunset photo from my trip.",
  "user_id": 1,
  "created_at": "2025-10-15T12:30:00"
}
```

---

### 2. POST /api/v1/post-content-upload (Form Data with File Upload)

**Method:** POST  
**Content-Type:** multipart/form-data  
**Body Format:** Form Data

#### Description
Create content by uploading an image file. The file will be saved to the `uploads/` directory with a timestamped filename.

#### Form Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Content title (3-200 characters) |
| content | string | Yes | Content body (min 10 characters) |
| user_id | integer | Yes | ID of user creating content |
| image | file | No | Image file to upload |

#### Supported Image Formats
- ✅ .jpg / .jpeg
- ✅ .png
- ✅ .gif
- ✅ .webp
- ✅ .bmp

#### Example Request (curl)
```bash
curl -X POST http://localhost:8000/api/v1/post-content-upload \
  -F "title=My Uploaded Post" \
  -F "content=This post includes an uploaded image." \
  -F "user_id=1" \
  -F "image=@/Users/macpro/Downloads/photo.png"
```

#### Example Request (Python)
```python
import requests

url = "http://localhost:8000/api/v1/post-content-upload"

# Prepare data
data = {
    "title": "My Uploaded Post",
    "content": "This post includes an uploaded image.",
    "user_id": 1
}

# Prepare file
files = {
    "image": open("/Users/macpro/Downloads/photo.png", "rb")
}

response = requests.post(url, data=data, files=files)
print(response.json())
```

#### Example Request (JavaScript/Fetch)
```javascript
const formData = new FormData();
formData.append("title", "My Uploaded Post");
formData.append("content", "This post includes an uploaded image.");
formData.append("user_id", "1");

// Get file from input element
const fileInput = document.querySelector('input[type="file"]');
formData.append("image", fileInput.files[0]);

fetch("http://localhost:8000/api/v1/post-content-upload", {
  method: "POST",
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Response (201 Created)
```json
{
  "id": 2,
  "title": "My Uploaded Post",
  "image": "/absolute/path/to/uploads/20251015_123045_photo.png",
  "content": "This post includes an uploaded image.",
  "user_id": 1,
  "created_at": "2025-10-15T12:30:45"
}
```

**Note**: The uploaded file is saved with a timestamped filename to prevent conflicts.

---

## 🎯 Use Cases

### Use Case 1: Image Already on Server/Computer
Use `POST /api/v1/post-content` with file path
```json
{
  "title": "Existing Image",
  "image": "/Users/macpro/Pictures/vacation.jpg",
  "content": "Using an existing image on my computer",
  "user_id": 1
}
```

### Use Case 2: Upload New Image
Use `POST /api/v1/post-content-upload` with file upload
```bash
curl -X POST http://localhost:8000/api/v1/post-content-upload \
  -F "title=New Upload" \
  -F "content=Uploading a new image" \
  -F "user_id=1" \
  -F "image=@/path/to/new/image.png"
```

### Use Case 3: No Image
Either endpoint can be used without an image
```json
{
  "title": "Text Only Post",
  "content": "This post has no image",
  "user_id": 1
}
```

---

## ⚠️ Validation & Error Handling

### File Path Validation (POST /api/v1/post-content)

**Error: File Not Found**
```json
{
  "detail": "Image file not found at path: /Users/macpro/nonexistent.jpg"
}
```
Status: 400 Bad Request

**Error: Path is Not a File**
```json
{
  "detail": "Path is not a file: /Users/macpro/Documents"
}
```
Status: 400 Bad Request

**Error: Invalid Image Format**
```json
{
  "detail": "Invalid image format. Allowed: .jpg, .jpeg, .png, .gif, .webp, .bmp"
}
```
Status: 400 Bad Request

### File Upload Validation (POST /api/v1/post-content-upload)

**Error: Invalid File Format**
```json
{
  "detail": "Invalid image format. Allowed: .jpg, .jpeg, .png, .gif, .webp, .bmp"
}
```
Status: 400 Bad Request

**Error: Upload Failed**
```json
{
  "detail": "Failed to save image: [error details]"
}
```
Status: 500 Internal Server Error

### Common Validation

**Error: User Not Found**
```json
{
  "detail": "User with id 999 not found"
}
```
Status: 404 Not Found

---

## 📁 Upload Directory Structure

```
demo-git-action/
├── uploads/                    # Created automatically
│   ├── .gitkeep               # Keeps directory in git
│   ├── 20251015_120000_image1.png
│   ├── 20251015_120100_image2.jpg
│   └── ...
```

**File Naming Convention:**
```
{YYYYMMDD}_{HHMMSS}_{original_filename}
```

Example: `20251015_123045_sunset.jpg`

---

## 🔐 Security Considerations

### Implemented
✅ File extension validation  
✅ File type checking (is_file)  
✅ Path existence validation  
✅ Limited to specific image formats  

### Recommended for Production
⚠️ File size limits  
⚠️ Virus scanning  
⚠️ Image dimension validation  
⚠️ Content-type verification  
⚠️ Rate limiting on uploads  
⚠️ User upload quotas  

---

## 💡 Tips & Best Practices

### 1. Use Absolute Paths
```json
// ✅ Good
"image": "/Users/macpro/Documents/photo.jpg"

// ❌ Bad
"image": "~/Documents/photo.jpg"
"image": "../photos/image.jpg"
```

### 2. Check File Exists Before Sending
```python
import os

image_path = "/Users/macpro/photo.jpg"
if os.path.exists(image_path):
    # Send request
    pass
```

### 3. Handle Large Files
For large files, use the upload endpoint with streaming:
```python
with open("large_image.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post(url, data=data, files=files)
```

### 4. Test Both Endpoints
```bash
# Test with file path
curl -X POST http://localhost:8000/api/v1/post-content \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Testing path","user_id":1,"image":"/path/to/test.jpg"}'

# Test with upload
curl -X POST http://localhost:8000/api/v1/post-content-upload \
  -F "title=Test" \
  -F "content=Testing upload" \
  -F "user_id=1" \
  -F "image=@/path/to/test.jpg"
```

---

## 📊 Comparison Table

| Feature | POST /api/v1/post-content | POST /api/v1/post-content-upload |
|---------|--------------------------|----------------------------------|
| Content-Type | application/json | multipart/form-data |
| Image Input | File path string | File upload |
| File Storage | Uses existing file | Saves to uploads/ |
| File Validation | Path & format | Format only |
| Use Case | Reference existing files | Upload new files |
| File Naming | Original path | Timestamped |

---

## 🧪 Testing Examples

### Test 1: Valid File Path
```bash
# Create a test image
echo "test" > /tmp/test.jpg

# Post content
curl -X POST http://localhost:8000/api/v1/post-content \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Post",
    "image": "/tmp/test.jpg",
    "content": "Testing file path",
    "user_id": 1
  }'
```

### Test 2: File Upload
```bash
curl -X POST http://localhost:8000/api/v1/post-content-upload \
  -F "title=Upload Test" \
  -F "content=Testing file upload" \
  -F "user_id=1" \
  -F "image=@/tmp/test.jpg"
```

### Test 3: Without Image
```bash
curl -X POST http://localhost:8000/api/v1/post-content \
  -H "Content-Type: application/json" \
  -d '{
    "title": "No Image Post",
    "content": "This post has no image",
    "user_id": 1
  }'
```

---

## 📝 Summary

✅ Two methods for image handling:
  - File path (JSON endpoint)
  - File upload (Form-data endpoint)

✅ Validation for:
  - File existence
  - File format
  - File type

✅ Automatic file storage in `uploads/` directory

✅ Timestamped filenames to prevent conflicts

✅ Full documentation and examples provided

Choose the endpoint based on your use case:
- **File Path**: When image already exists on system
- **File Upload**: When uploading new images from client
