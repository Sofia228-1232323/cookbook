from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Comment, User, Recipe
from ..schemas import CommentCreate, CommentResponse, CommentUpdate
from .auth import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/recipe/{recipe_id}", response_model=List[CommentResponse])
def read_comments_by_recipe(recipe_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.recipe_id == recipe_id).all()
    return comments

@router.get("/{comment_id}", response_model=CommentResponse)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.post("/", response_model=CommentResponse)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == comment.recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db_comment = Comment(
        content=comment.content,
        author_id=current_user.id,
        recipe_id=comment.recipe_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int, 
    comment: CommentUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is the author
    if db_comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is the author
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}
