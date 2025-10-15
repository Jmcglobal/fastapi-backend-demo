# This file makes the routes directory a package
from src.routes.users import router as users_router
from src.routes.content import router as content_router

__all__ = ["users_router", "content_router"]
