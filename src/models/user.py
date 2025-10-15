from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    phone_number: str = Field(unique=True, index=True, nullable=False)
    country: str = Field(nullable=False)
    state: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    contents: List["Content"] = Relationship(back_populates="user")
