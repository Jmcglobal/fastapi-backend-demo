from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class Content(SQLModel, table=True):
    __tablename__ = "contents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False)
    image: Optional[str] = Field(default=None, nullable=True)
    content: str = Field(nullable=False)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: Optional["User"] = Relationship(back_populates="contents")
