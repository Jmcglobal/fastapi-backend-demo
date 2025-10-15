from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class SignupSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., pattern=r"^\+234\d{8,11}$")
    country: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        # Check that name contains at least one alphabet character
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Name must contain at least one alphabet character")
        
        # Check that name is not just numbers
        if v.strip().replace(" ", "").isdigit():
            raise ValueError("Name cannot be only numbers")
        
        return v.strip()
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        # Ensure it starts with +234
        if not v.startswith("+234"):
            raise ValueError("Phone number must start with +234")
        
        # Extract digits after +234
        digits = v[4:]
        
        # Check length (8-11 digits after +234)
        if len(digits) < 8 or len(digits) > 11:
            raise ValueError("Phone number must have between 8 and 11 digits after +234")
        
        # Ensure only digits after +234
        if not digits.isdigit():
            raise ValueError("Phone number must contain only digits after +234")
        
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str
    country: str
    state: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class UserBasicResponse(BaseModel):
    """User response without created_at - used in content listings"""
    id: int
    name: str
    email: str
    phone_number: str
    country: str
    state: str
    
    model_config = {"from_attributes": True}


class PostContentSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    image: Optional[str] = Field(
        None, 
        description="Optional image file path (e.g., /Users/macpro/myimage.png). The file path and name will be saved as the image URL."
    )
    content: str = Field(..., min_length=10)
    user_id: int = Field(..., gt=0)


class UpdateContentSchema(BaseModel):
    """Schema for updating content - image and content body"""
    image: Optional[str] = Field(
        None,
        description="Optional image file path (e.g., /Users/macpro/myimage.png)"
    )
    content: Optional[str] = Field(None, min_length=10, description="Content body text")


class UpdateUserSchema(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=r"^\+234\d{8,11}$")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Check that name contains at least one alphabet character
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Name must contain at least one alphabet character")
        
        # Check that name is not just numbers
        if v.strip().replace(" ", "").isdigit():
            raise ValueError("Name cannot be only numbers")
        
        return v.strip()
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Ensure it starts with +234
        if not v.startswith("+234"):
            raise ValueError("Phone number must start with +234")
        
        # Extract digits after +234
        digits = v[4:]
        
        # Check length (8-11 digits after +234)
        if len(digits) < 8 or len(digits) > 11:
            raise ValueError("Phone number must have between 8 and 11 digits after +234")
        
        # Ensure only digits after +234
        if not digits.isdigit():
            raise ValueError("Phone number must contain only digits after +234")
        
        return v


class ContentResponse(BaseModel):
    id: int
    title: str
    image: Optional[str]
    content: str
    user_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ContentWithUserResponse(BaseModel):
    id: int
    title: str
    image: Optional[str]
    content: str
    user_id: int
    created_at: datetime
    user: UserBasicResponse  # Changed to UserBasicResponse (no created_at)
    
    model_config = {"from_attributes": True}


class UserWithContentsResponse(BaseModel):
    id: int
    name: str
    email: str
    phone_number: str
    country: str
    state: str
    created_at: datetime
    contents: list[ContentResponse]
    
    model_config = {"from_attributes": True}
