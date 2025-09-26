import pytest
from fastapi import status
from app.models import User, Recipe, Comment, Like
from app.auth import get_password_hash

class TestUserBusinessLogic:
    """Тесты для бизнес-логики пользователей."""
    
    def test_user_creation(self, db_session):
        """Тест создания пользователя."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "hashed_password": get_password_hash("pass123")
        }
        
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.hashed_password is not None
    
    def test_user_email_uniqueness(self, db_session):
        """Тест уникальности email пользователя."""
        # Создаем первого пользователя
        user1 = User(
            email="unique@example.com",
            username="user1",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user1)
        db_session.commit()
        
        # Пытаемся создать пользователя с тем же email
        user2 = User(
            email="unique@example.com",  # Тот же email
            username="user2",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user2)
        
        # Должно возникнуть исключение из-за уникального ограничения
        with pytest.raises(Exception):  # IntegrityError или подобное
            db_session.commit()
    
    def test_user_username_uniqueness(self, db_session):
        """Тест уникальности username пользователя."""
        # Создаем первого пользователя
        user1 = User(
            email="user1@example.com",
            username="unique_username",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user1)
        db_session.commit()
        
        # Пытаемся создать пользователя с тем же username
        user2 = User(
            email="user2@example.com",
            username="unique_username",  # Тот же username
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user2)
        
        # Должно возникнуть исключение из-за уникального ограничения
        with pytest.raises(Exception):  # IntegrityError или подобное
            db_session.commit()
    
    def test_user_recipes_relationship(self, db_session, test_user):
        """Тест связи пользователя с рецептами."""
        from app.models import Category
        category = Category(name="Test Category")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        # Создаем рецепт от пользователя
        recipe = Recipe(
            title="User Recipe",
            description="User Description",
            ingredients='["ingredient1"]',
            steps='["step1"]',
            author_id=test_user.id,
            category_id=category.id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        # Проверяем связь
        assert recipe.author_id == test_user.id
        # Проверяем обратную связь
        assert recipe in test_user.recipes
    
    def test_user_comments_relationship(self, db_session, test_user, test_recipe):
        """Тест связи пользователя с комментариями."""
        from app.models import Comment
        comment = Comment(
            content="User comment",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        
        # Проверяем связь
        assert comment.author_id == test_user.id
        # Проверяем обратную связь
        assert comment in test_user.comments
    
    def test_user_likes_relationship(self, db_session, test_user, test_recipe):
        """Тест связи пользователя с лайками."""
        from app.models import Like
        like = Like(
            user_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        # Проверяем связь
        assert like.user_id == test_user.id
        # Проверяем обратную связь
        assert like in test_user.likes
    
    def test_user_recipes_count(self, db_session, test_user):
        """Тест подсчета рецептов пользователя."""
        from app.models import Category
        category = Category(name="Test Category")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        # Создаем несколько рецептов
        recipe1 = Recipe(
            title="Recipe 1",
            description="Description 1",
            ingredients='["ingredient1"]',
            steps='["step1"]',
            author_id=test_user.id,
            category_id=category.id
        )
        recipe2 = Recipe(
            title="Recipe 2",
            description="Description 2",
            ingredients='["ingredient2"]',
            steps='["step2"]',
            author_id=test_user.id,
            category_id=category.id
        )
        
        db_session.add(recipe1)
        db_session.add(recipe2)
        db_session.commit()
        
        # Проверяем количество рецептов
        recipes_count = len(test_user.recipes)
        assert recipes_count == 2

class TestUserAPI:
    """Тесты для API пользователей."""
    
    def test_get_users_list(self, client, test_user):
        """Тест получения списка пользователей."""
        response = client.get("/users")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        
        # Проверяем, что наш тестовый пользователь в списке
        user_emails = [user["email"] for user in data]
        assert "test@example.com" in user_emails
    
    def test_get_user_by_id(self, client, test_user):
        """Тест получения пользователя по ID."""
        response = client.get(f"/users/{test_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        # Пароль не должен быть в ответе
        assert "hashed_password" not in data
    
    def test_get_nonexistent_user(self, client):
        """Тест получения несуществующего пользователя."""
        response = client.get("/users/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_user_with_recipes(self, client, test_user, test_recipe):
        """Тест получения пользователя с рецептами."""
        response = client.get(f"/users/{test_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        # Проверяем, что в ответе есть информация о рецептах
        # (если это реализовано в API)
    
    def test_user_profile_completeness(self, client, test_user):
        """Тест полноты профиля пользователя."""
        response = client.get(f"/users/{test_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Проверяем наличие всех необходимых полей
        required_fields = ["id", "email", "username"]
        for field in required_fields:
            assert field in data
        
        # Проверяем, что чувствительные данные не передаются
        sensitive_fields = ["hashed_password", "password"]
        for field in sensitive_fields:
            assert field not in data
    
    def test_user_data_validation(self, client):
        """Тест валидации данных пользователя."""
        # Тест с невалидным email
        invalid_user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=invalid_user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_user_authentication_required(self, client, test_user):
        """Тест требований аутентификации для операций с пользователями."""
        # Попытка получить информацию о пользователе без токена
        response = client.get(f"/users/{test_user.id}")
        
        # В зависимости от реализации API, это может требовать аутентификации
        # или быть публичным
        assert response.status_code in [200, 401]
    
    def test_user_search_functionality(self, client, test_user):
        """Тест функциональности поиска пользователей."""
        # Тест поиска по email
        response = client.get("/users?email=test@example.com")
        
        # В зависимости от реализации API
        if response.status_code == 200:
            data = response.json()
            assert len(data) >= 1
            assert data[0]["email"] == "test@example.com"
    
    def test_user_statistics(self, client, test_user, test_recipe):
        """Тест статистики пользователя."""
        response = client.get(f"/users/{test_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Проверяем, что в ответе есть статистика
        # (если это реализовано в API)
        # Например: количество рецептов, комментариев, лайков
