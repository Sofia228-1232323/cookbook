from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Association table for recipe categories/tags
recipe_categories = Table(
    'recipe_categories',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipes = relationship("Recipe", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)

    # Relationships
    recipes = relationship("Recipe", secondary=recipe_categories, back_populates="categories")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    ingredients = Column(Text, nullable=False)  # JSON string
    steps = Column(Text, nullable=False)  # JSON string
    image_url = Column(String)
    prep_time = Column(Integer)  # in minutes
    cook_time = Column(Integer)  # in minutes
    servings = Column(Integer)
    difficulty = Column(String)  # easy, medium, hard
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="recipes")
    categories = relationship("Category", secondary=recipe_categories, back_populates="recipes")
    comments = relationship("Comment", back_populates="recipe", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="recipe", cascade="all, delete-orphan")

    @property
    def ingredients_list(self):
        import json
        return json.loads(self.ingredients) if self.ingredients else []

    @property
    def steps_list(self):
        import json
        return json.loads(self.steps) if self.steps else []

    @property
    def likes_count(self):
        return len(self.likes) if hasattr(self, "likes") else 0

    @property
    def comments_count(self):
        return len(self.comments) if hasattr(self, "comments") else 0


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="comments")
    recipe = relationship("Recipe", back_populates="comments")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="likes")
    recipe = relationship("Recipe", back_populates="likes")