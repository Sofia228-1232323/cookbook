from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Like, User, Recipe
from .auth import get_current_user

router = APIRouter(prefix="/likes", tags=["likes"])

@router.post("/recipe/{recipe_id}/like")
def like_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Check if user already liked this recipe
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.recipe_id == recipe_id
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=400, detail="Recipe already liked")
    
    # Create new like
    like = Like(user_id=current_user.id, recipe_id=recipe_id)
    db.add(like)
    db.commit()
    
    return {"message": "Recipe liked successfully"}

@router.delete("/recipe/{recipe_id}/like")
def unlike_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Find the like
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.recipe_id == recipe_id
    ).first()
    
    if like is None:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(like)
    db.commit()
    
    return {"message": "Recipe unliked successfully"}

@router.get("/recipe/{recipe_id}/count")
def get_likes_count(recipe_id: int, db: Session = Depends(get_db)):
    count = db.query(Like).filter(Like.recipe_id == recipe_id).count()
    return {"recipe_id": recipe_id, "likes_count": count}

@router.get("/recipe/{recipe_id}/is-liked")
def check_if_liked(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.recipe_id == recipe_id
    ).first()
    
    return {"recipe_id": recipe_id, "is_liked": like is not None}

