from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    ingredients: List[str]
    steps: List[str]
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None


class RecipeCreate(RecipeBase):
    category_ids: Optional[List[int]] = []


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    category_ids: Optional[List[int]] = None


class Recipe(RecipeBase):
    id: int
    image_url: Optional[str] = None
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: User
    categories: List[Category] = []
    likes_count: int = 0
    comments_count: int = 0

    class Config:
        from_attributes = True


class RecipeResponse(RecipeBase):
    id: int
    image_url: Optional[str] = None
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: User
    categories: List[Category] = []
    likes_count: int = 0
    comments_count: int = 0

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        # Create a copy of the object data
        data = obj.__dict__.copy()
        
        # Replace ingredients and steps with parsed lists
        data['ingredients'] = obj.ingredients_list
        data['steps'] = obj.steps_list
        data['likes_count'] = obj.likes_count
        data['comments_count'] = obj.comments_count
        
        # Ensure author is included
        if hasattr(obj, 'author') and obj.author:
            data['author'] = obj.author
        
        # Remove SQLAlchemy internal attributes
        data.pop('_sa_instance_state', None)
        
        return cls(**data)


class RecipeList(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    author_id: int
    author: User
    categories: List[Category] = []
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    recipe_id: int


class Comment(CommentBase):
    id: int
    author_id: int
    recipe_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: User

    class Config:
        from_attributes = True


class CommentResponse(CommentBase):
    id: int
    author_id: int
    recipe_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: User

    class Config:
        from_attributes = True


class CommentUpdate(CommentBase):
    pass


class LikeCreate(BaseModel):
    pass


class Like(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    created_at: datetime

    class Config:
        from_attributes = True

