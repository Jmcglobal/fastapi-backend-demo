from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.database import get_session
from src.schemas import PostContentSchema, ContentResponse, ContentWithUserResponse, UpdateContentSchema
from src.services.content_service import ContentService
from src.services.user_service import UserService
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1", tags=["content"])


@router.post("/post-content", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
def post_content(content_data: PostContentSchema, session: Session = Depends(get_session)):
    """
    Create new content.
    
    **Image Field**: Accepts an image file path (e.g., /Users/macpro/myimage.png).
    The file path and name will be saved as the image URL.
    
    **Note**: The image path validation is optional. If you want to just save the path
    without validation, the system will accept any string.
    
    **Example**:
    ```json
    {
      "title": "My Post",
      "image": "/Users/macpro/Documents/myimage.png",
      "content": "This is my content",
      "user_id": 1
    }
    ```
    
    Requires a valid user_id.
    """
    # Verify user exists
    user = UserService.get_user_by_id(session, content_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {content_data.user_id} not found"
        )
    
    # Create content (image path is saved as-is, no validation)
    content = ContentService.create_content(session, content_data)
    return content


@router.put("/content/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: int,
    content_data: UpdateContentSchema,
    session: Session = Depends(get_session)
):
    """
    Update existing content.
    
    You can update:
    - Image path (e.g., /Users/macpro/newimage.png)
    - Content body text
    
    **Example**:
    ```json
    {
      "image": "/Users/macpro/Documents/updated_image.png",
      "content": "This is my updated content"
    }
    ```
    """
    # Get existing content
    content = ContentService.get_content_by_id(session, content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content with id {content_id} not found"
        )
    
    # Update content
    updated_content = ContentService.update_content(session, content_id, content_data)
    return updated_content


@router.get("/content", response_model=List[ContentWithUserResponse])
def get_all_contents(session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    """
    Get all content with users who created them.
    Uses Redis caching with 10 minutes TTL.
    """
    contents = ContentService.get_contents_with_users(session)
    return contents


@router.get("/content/{content_id}", response_model=ContentWithUserResponse)
def get_content_by_id(content_id: int, session: Session = Depends(get_session)):
    """
    Get content by ID.
    Uses Redis caching with 10 minutes TTL.
    If content is not accessed within 10 minutes, it expires from cache.
    """
    content = ContentService.get_content_by_id(session, content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content with id {content_id} not found"
        )
    return content
