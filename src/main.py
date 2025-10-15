from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.users import router as users_router
from src.routes.content import router as content_router
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database tables
    from src.database import init_db
    print("Initializing database...")
    # Note: For production, use Alembic migrations instead
    # init_db()  # Uncomment if you want to auto-create tables
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Content Management API",
    description="FastAPI backend with PostgreSQL and Redis",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def read_root():
    """Root endpoint - health check"""
    return {"message": "Up and running"}


# Include routers
app.include_router(users_router)
app.include_router(content_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
