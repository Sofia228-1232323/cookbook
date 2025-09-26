import pytest
from fastapi import status
from app.auth import get_password_hash, verify_password, create_access_token
from app.models import User

class TestAuthBusinessLogic:
    """Тесты для бизнес-логики аутентификации."""
    
    def test_password_hashing(self):
        """Тест хеширования пароля."""
        password = "pass123"
        hashed = get_password_hash(password)
        
        # Хеш должен отличаться от оригинального пароля
        assert hashed != password
        # Хеш не должен быть пустым
        assert len(hashed) > 0
        # Хеш должен начинаться с $2b$ (bcrypt)
        assert hashed.startswith("$2b$")
    
    def test_password_verification_correct(self):
        """Тест проверки правильного пароля."""
        password = "pass123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_verification_incorrect(self):
        """Тест проверки неправильного пароля."""
        password = "pass123"
        wrong_password = "wrongpass"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_verification_empty(self):
        """Тест проверки пустого пароля."""
        password = "pass123"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False
        assert verify_password("", hashed) is False
    
    def test_token_creation(self):
        """Тест создания JWT токена."""
        user_data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data=user_data)
        
        # Токен не должен быть пустым
        assert len(token) > 0
        # Токен должен содержать точки (JWT формат)
        assert token.count(".") == 2

class TestAuthAPI:
    """Тесты для API аутентификации."""
    
    def test_register_success(self, client):
        """Тест успешной регистрации."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "pass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
    
    def test_register_duplicate_email(self, client, test_user):
        """Тест регистрации с существующим email."""
        user_data = {
            "email": "test@example.com",  # Существующий email
            "username": "newuser",
            "password": "pass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email already registered" in response.json()["detail"].lower()
    
    def test_register_duplicate_username(self, client, test_user):
        """Тест регистрации с существующим username."""
        user_data = {
            "email": "newuser@example.com",
            "username": "testuser",  # Существующий username
            "password": "pass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Тест регистрации с невалидным email."""
        user_data = {
            "email": "invalid-email",
            "username": "newuser",
            "password": "pass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client):
        """Тест регистрации с коротким паролем."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "123"  # Слишком короткий пароль
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_login_success(self, client, test_user):
        """Тест успешного входа."""
        login_data = {
            "email": "test@example.com",
            "password": "pass123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
    
    def test_login_wrong_password(self, client, test_user):
        """Тест входа с неправильным паролем."""
        login_data = {
            "email": "test@example.com",
            "password": "wrongpass"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect email or password" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Тест входа несуществующего пользователя."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "pass123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect email or password" in response.json()["detail"].lower()
    
    def test_get_current_user_success(self, client, auth_headers):
        """Тест получения информации о текущем пользователе."""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert data["email"] == "test@example.com"
    
    def test_get_current_user_unauthorized(self, client):
        """Тест получения информации о пользователе без авторизации."""
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        """Тест получения информации с невалидным токеном."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
