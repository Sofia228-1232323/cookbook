import pytest
from fastapi import status
from app.models import User, Recipe, Category, Comment, Like
from app.auth import get_password_hash, verify_password
import json

class TestSimpleBusinessLogic:
    """Простые тесты бизнес-логики."""

    def test_password_hashing(self):
        """Тест хеширования пароля."""
        password = "testpassword"
        hashed_password = get_password_hash(password)
        assert hashed_password != password
        assert verify_password(password, hashed_password)

    def test_password_verification_failure(self):
        """Тест неудачной верификации пароля."""
        password = "testpassword"
        wrong_password = "wrongpassword"
        hashed_password = get_password_hash(password)
        assert not verify_password(wrong_password, hashed_password)

    def test_user_creation(self, db_session):
        """Тест создания пользователя."""
        user = User(
            email="test@example.com", 
            username="testuser", 
            hashed_password=get_password_hash("testpassword")
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        assert user.id is not None
        assert user.email == "test@example.com"

    def test_category_creation(self, db_session):
        """Тест создания категории."""
        category = Category(name="Test Category", description="Test Description")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        assert category.id is not None
        assert category.name == "Test Category"

    def test_recipe_creation(self, db_session, test_user, test_category):
        """Тест создания рецепта."""
        recipe = Recipe(
            title="Test Recipe",
            description="Test Description",
            ingredients='["ingredient1", "ingredient2"]',
            steps='["step1", "step2"]',
            author_id=test_user.id
        )
        recipe.categories.append(test_category)
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        assert recipe.id is not None
        assert recipe.title == "Test Recipe"

    def test_comment_creation(self, db_session, test_user, test_recipe):
        """Тест создания комментария."""
        comment = Comment(
            content="Test comment",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        assert comment.id is not None
        assert comment.content == "Test comment"

    def test_like_creation(self, db_session, test_user, test_recipe):
        """Тест создания лайка."""
        like = Like(
            user_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        assert like.id is not None
        assert like.user_id == test_user.id

class TestSimpleAPI:
    """Простые тесты API."""

    def test_register_success(self, client):
        """Тест успешной регистрации."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_200_OK

    def test_login_success(self, client, test_user):
        """Тест успешного входа."""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

    def test_get_categories(self, client, test_category):
        """Тест получения категорий."""
        response = client.get("/categories/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_recipes(self, client, test_recipe):
        """Тест получения рецептов."""
        response = client.get("/recipes/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_recipe_by_id(self, client, test_recipe):
        """Тест получения рецепта по ID."""
        response = client.get(f"/recipes/{test_recipe.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_recipe.id
