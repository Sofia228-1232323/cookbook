from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Category
from ..schemas import CategoryResponse, CategoryCreate

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryResponse])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

