from sqlmodel import Session, select
from src.models.content import Content
from src.models.user import User
from src.schemas import PostContentSchema, UpdateContentSchema
from src.redis_config import set_cache, get_cache, delete_pattern
from typing import Optional, List, Dict, Any


class ContentService:
    @staticmethod
    def create_content(session: Session, content_data: PostContentSchema) -> Content:
        """Create new content"""
        content = Content(
            title=content_data.title,
            image=content_data.image,
            content=content_data.content,
            user_id=content_data.user_id
        )
        
        session.add(content)
        session.commit()
        session.refresh(content)
        
        # Invalidate all contents cache since we added new content
        delete_pattern("all_contents")
        delete_pattern("content_with_user:*")
        
        return content
    
    @staticmethod
    def get_content_by_id(session: Session, content_id: int) -> Optional[Content]:
        """
        Get content by ID with caching.
        If not in cache, fetch from DB and cache with 10 minutes TTL.
        """
        # Try to get from cache first
        cache_key = f"content:{content_id}"
        cached_content = get_cache(cache_key)
        
        if cached_content:
            # Return cached content
            return Content(**cached_content)
        
        # If not in cache, get from database
        statement = select(Content).where(Content.id == content_id)
        content = session.exec(statement).first()
        
        if content:
            # Cache the content with 10 minutes TTL
            content_dict = {
                "id": content.id,
                "title": content.title,
                "image": content.image,
                "content": content.content,
                "user_id": content.user_id,
                "created_at": content.created_at.isoformat()
            }
            set_cache(cache_key, content_dict, ttl=600)
        
        return content
    
    @staticmethod
    def get_all_contents(session: Session) -> List[Content]:
        """
        Get all contents with caching.
        If not in cache, fetch from DB and cache with 10 minutes TTL.
        """
        # Try to get from cache first
        cache_key = "all_contents"
        cached_contents = get_cache(cache_key)
        
        if cached_contents:
            return [Content(**c) for c in cached_contents]
        
        # If not in cache, get from database
        statement = select(Content)
        contents = session.exec(statement).all()
        contents_list = list(contents)
        
        if contents_list:
            # Cache the contents with 10 minutes TTL
            contents_dict = [
                {
                    "id": c.id,
                    "title": c.title,
                    "image": c.image,
                    "content": c.content,
                    "user_id": c.user_id,
                    "created_at": c.created_at.isoformat()
                }
                for c in contents_list
            ]
            set_cache(cache_key, contents_dict, ttl=600)
        
        return contents_list
    
    @staticmethod
    def get_contents_with_users(session: Session) -> List[Dict[str, Any]]:
        """
        Get all contents with their associated users.
        Uses Redis caching with 10 minutes TTL.
        """
        cache_key = "content_with_user:all"
        cached_data = get_cache(cache_key)
        
        if cached_data:
            # Return cached data directly
            return cached_data
        
        # Get from database with joined user data
        statement = select(Content).join(User)
        contents = session.exec(statement).all()
        contents_list = list(contents)
        
        if contents_list:
            # Prepare data for caching
            contents_with_users = []
            for content in contents_list:
                # Refresh to ensure user relationship is loaded
                session.refresh(content)
                content_dict = {
                    "id": content.id,
                    "title": content.title,
                    "image": content.image,
                    "content": content.content,
                    "user_id": content.user_id,
                    "created_at": content.created_at.isoformat(),
                    "user": {
                        "id": content.user.id,
                        "name": content.user.name,
                        "email": content.user.email,
                        "phone_number": content.user.phone_number,
                        "country": content.user.country,
                        "state": content.user.state
                        # Excluded: created_at from user object
                    }
                }
                contents_with_users.append(content_dict)
            
            set_cache(cache_key, contents_with_users, ttl=600)
            return contents_with_users
        
        return []
    
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
        
        # Save changes
        session.add(content)
        session.commit()
        session.refresh(content)
        
        # Invalidate caches
        delete_pattern(f"content:{content_id}")
        delete_pattern("all_contents")
        delete_pattern("content_with_user:*")
        
        return content
