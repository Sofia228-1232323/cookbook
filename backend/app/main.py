from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .routers import auth, users, recipes, comments, likes, categories
from .config import settings

app = FastAPI(
    title="Cookbook API",
    description="API для платформы обмена кулинарными рецептами",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://localhost",       # Production frontend (port 80)
        "http://127.0.0.1",       # Production frontend (port 80)
        "http://192.168.0.14:3000",  # Network IP
        "http://192.168.0.14:3001",  # Current frontend port
        "http://192.168.0.14:8000",  # Backend IP
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs(settings.upload_dir, exist_ok=True)

# Static files for uploaded images
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recipes.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(categories.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Cookbook API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
