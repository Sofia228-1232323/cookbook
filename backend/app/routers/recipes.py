from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import json
import os
import uuid
from shutil import copyfileobj

from ..database import get_db
from ..models import Recipe, User, Category, Comment, Like
from ..schemas import RecipeCreate, RecipeResponse, RecipeUpdate, CommentResponse
from .auth import get_current_user
from ..config import settings

router = APIRouter(prefix="/recipes", tags=["recipes"])

def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file and return the filename"""
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(settings.upload_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        copyfileobj(file.file, buffer)
    
    return unique_filename

@router.get("/", response_model=List[RecipeResponse])
def read_recipes(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Recipe).options(
        joinedload(Recipe.author),
        joinedload(Recipe.categories),
        joinedload(Recipe.comments),
        joinedload(Recipe.likes)
    )
    
    if category_id:
        query = query.filter(Recipe.categories.any(Category.id == category_id))
    
    if search:
        query = query.filter(Recipe.title.contains(search))
    
    recipes = query.offset(skip).limit(limit).all()
    return [RecipeResponse.from_orm(recipe) for recipe in recipes]

@router.get("/{recipe_id}", response_model=RecipeResponse)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).options(
        joinedload(Recipe.author),
        joinedload(Recipe.categories),
        joinedload(Recipe.comments),
        joinedload(Recipe.likes)
    ).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RecipeResponse.from_orm(recipe)

@router.get("/{recipe_id}/comments", response_model=List[CommentResponse])
def read_recipe_comments(recipe_id: int, db: Session = Depends(get_db)):
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Get comments with author information
    comments = db.query(Comment).options(
        joinedload(Comment.author)
    ).filter(Comment.recipe_id == recipe_id).all()
    
    return comments

@router.post("/{recipe_id}/like")
def like_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Like or unlike a recipe"""
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
        # Unlike the recipe
        db.delete(existing_like)
        db.commit()
        return {"message": "Recipe unliked successfully", "liked": False}
    else:
        # Like the recipe
        like = Like(user_id=current_user.id, recipe_id=recipe_id)
        db.add(like)
        db.commit()
        return {"message": "Recipe liked successfully", "liked": True}

@router.get("/{recipe_id}/is-liked")
def check_if_liked(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Check if current user liked this recipe"""
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.recipe_id == recipe_id
    ).first()
    
    return {"recipe_id": recipe_id, "is_liked": like is not None}

@router.delete("/{recipe_id}/like")
def unlike_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Unlike a recipe"""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Find the like
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.recipe_id == recipe_id
    ).first()
    
    if like is None:
        # If like doesn't exist, it's already "unliked", so return success
        return {"message": "Recipe was not liked", "liked": False}
    
    # Remove the like
    db.delete(like)
    db.commit()
    
    return {"message": "Recipe unliked successfully", "liked": False}

@router.post("/", response_model=RecipeResponse)
def create_recipe(
    title: str = Form(...),
    description: str = Form(...),
    ingredients: str = Form(...),
    steps: str = Form(...),
    prep_time: Optional[int] = Form(None),
    cook_time: Optional[int] = Form(None),
    servings: Optional[int] = Form(None),
    difficulty: Optional[str] = Form(None),
    category_ids: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Parse ingredients and steps
    try:
        ingredients_list = json.loads(ingredients)
        steps_list = json.loads(steps)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in ingredients or steps")
    
    db_recipe = Recipe(
        title=title,
        description=description,
        ingredients=json.dumps(ingredients_list),
        steps=json.dumps(steps_list),
        prep_time=prep_time,
        cook_time=cook_time,
        servings=servings,
        difficulty=difficulty,
        author_id=current_user.id
    )
    
    # Handle image upload
    if image:
        try:
            filename = save_uploaded_file(image)
            db_recipe.image_url = f"/uploads/{filename}"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error saving image: {str(e)}")
    
    # Add categories if provided
    if category_ids:
        try:
            category_id_list = json.loads(category_ids)
            categories = db.query(Category).filter(Category.id.in_(category_id_list)).all()
            db_recipe.categories = categories
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in category_ids")
    
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    
    # Reload with relationships
    db_recipe = db.query(Recipe).options(
        joinedload(Recipe.author),
        joinedload(Recipe.categories),
        joinedload(Recipe.comments),
        joinedload(Recipe.likes)
    ).filter(Recipe.id == db_recipe.id).first()
    
    return RecipeResponse.from_orm(db_recipe)

@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    title: str = Form(...),
    description: str = Form(...),
    ingredients: str = Form(...),
    steps: str = Form(...),
    prep_time: Optional[int] = Form(None),
    cook_time: Optional[int] = Form(None),
    servings: Optional[int] = Form(None),
    difficulty: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_recipe = db.query(Recipe).options(
        joinedload(Recipe.author),
        joinedload(Recipe.categories),
        joinedload(Recipe.comments),
        joinedload(Recipe.likes)
    ).filter(Recipe.id == recipe_id).first()
    
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Check if user is the author
    if db_recipe.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Parse ingredients and steps
    try:
        ingredients_list = json.loads(ingredients)
        steps_list = json.loads(steps)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in ingredients or steps")
    
    # Update fields
    db_recipe.title = title
    db_recipe.description = description
    db_recipe.ingredients = json.dumps(ingredients_list)
    db_recipe.steps = json.dumps(steps_list)
    
    if prep_time is not None:
        db_recipe.prep_time = prep_time
    if cook_time is not None:
        db_recipe.cook_time = cook_time
    if servings is not None:
        db_recipe.servings = servings
    if difficulty is not None:
        db_recipe.difficulty = difficulty
    
    # Handle image upload
    if image:
        try:
            filename = save_uploaded_file(image)
            db_recipe.image_url = f"/uploads/{filename}"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error saving image: {str(e)}")
    
    # Update categories if provided
    if category_id is not None:
        category = db.query(Category).filter(Category.id == category_id).first()
        if category:
            db_recipe.categories = [category]
    
    db.commit()
    db.refresh(db_recipe)
    return RecipeResponse.from_orm(db_recipe)

@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Check if user is the author
    if recipe.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(recipe)
    db.commit()
    return {"message": "Recipe deleted successfully"}
