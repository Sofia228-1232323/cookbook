import pytest
from fastapi import status
from app.models import Like, Recipe, User
from app.auth import get_password_hash

class TestLikeBusinessLogic:
    """Тесты для бизнес-логики лайков."""
    
    def test_like_creation(self, db_session, test_user, test_recipe):
        """Тест создания лайка."""
        like_data = {
            "user_id": test_user.id,
            "recipe_id": test_recipe.id
        }
        
        like = Like(**like_data)
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        assert like.id is not None
        assert like.user_id == test_user.id
        assert like.recipe_id == test_recipe.id
    
    def test_like_user_relationship(self, db_session, test_user, test_recipe):
        """Тест связи лайка с пользователем."""
        like = Like(
            user_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        # Проверяем связь с пользователем
        assert like.user_id == test_user.id
        # Проверяем обратную связь
        assert like in test_user.likes
    
    def test_like_recipe_relationship(self, db_session, test_user, test_recipe):
        """Тест связи лайка с рецептом."""
        like = Like(
            user_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        # Проверяем связь с рецептом
        assert like.recipe_id == test_recipe.id
        # Проверяем обратную связь
        assert like in test_recipe.likes
    
    def test_duplicate_like_prevention(self, db_session, test_user, test_recipe):
        """Тест предотвращения дублирования лайков."""
        # Создаем первый лайк
        like1 = Like(
            user_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(like1)
        db_session.commit()
        
        # Пытаемся создать дублирующий лайк
        like2 = Like(
            user_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(like2)
        
        # Должно возникнуть исключение из-за уникального ограничения
        with pytest.raises(Exception):  # IntegrityError или подобное
            db_session.commit()
    
    def test_like_count_calculation(self, db_session, test_user, test_recipe):
        """Тест подсчета количества лайков."""
        # Создаем несколько лайков от разных пользователей
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password=get_password_hash("password123")
        )
        user3 = User(
            email="user3@example.com",
            username="user3",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user2)
        db_session.add(user3)
        db_session.commit()
        
        # Создаем лайки
        like1 = Like(user_id=test_user.id, recipe_id=test_recipe.id)
        like2 = Like(user_id=user2.id, recipe_id=test_recipe.id)
        like3 = Like(user_id=user3.id, recipe_id=test_recipe.id)
        
        db_session.add(like1)
        db_session.add(like2)
        db_session.add(like3)
        db_session.commit()
        
        # Проверяем подсчет лайков
        likes_count = db_session.query(Like).filter(Like.recipe_id == test_recipe.id).count()
        assert likes_count == 3

class TestLikeAPI:
    """Тесты для API лайков."""
    
    def test_like_recipe_success(self, client, auth_headers, test_recipe):
        """Тест успешного лайка рецепта."""
        response = client.post(f"/recipes/{test_recipe.id}/like", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "liked" in data
        assert data["liked"] is True
    
    def test_like_recipe_unauthorized(self, client, test_recipe):
        """Тест лайка рецепта без авторизации."""
        response = client.post(f"/recipes/{test_recipe.id}/like")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_like_nonexistent_recipe(self, client, auth_headers):
        """Тест лайка несуществующего рецепта."""
        response = client.post("/recipes/99999/like", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_unlike_recipe_success(self, client, auth_headers, test_recipe):
        """Тест успешного снятия лайка с рецепта."""
        # Сначала ставим лайк
        client.post(f"/recipes/{test_recipe.id}/like", headers=auth_headers)
        
        # Затем убираем лайк
        response = client.delete(f"/recipes/{test_recipe.id}/like", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "liked" in data
        assert data["liked"] is False
    
    def test_unlike_recipe_unauthorized(self, client, test_recipe):
        """Тест снятия лайка без авторизации."""
        response = client.delete(f"/recipes/{test_recipe.id}/like")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unlike_nonexistent_recipe(self, client, auth_headers):
        """Тест снятия лайка с несуществующего рецепта."""
        response = client.delete("/recipes/99999/like", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_unlike_not_liked_recipe(self, client, auth_headers, test_recipe):
        """Тест снятия лайка с рецепта, который не был лайкнут."""
        response = client.delete(f"/recipes/{test_recipe.id}/like", headers=auth_headers)
        
        # Должно вернуть успех, даже если лайка не было
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "liked" in data
        assert data["liked"] is False
    
    def test_check_like_status_liked(self, client, auth_headers, test_recipe):
        """Тест проверки статуса лайка (лайк поставлен)."""
        # Сначала ставим лайк
        client.post(f"/recipes/{test_recipe.id}/like", headers=auth_headers)
        
        # Проверяем статус
        response = client.get(f"/recipes/{test_recipe.id}/is-liked", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["liked"] is True
    
    def test_check_like_status_not_liked(self, client, auth_headers, test_recipe):
        """Тест проверки статуса лайка (лайк не поставлен)."""
        response = client.get(f"/recipes/{test_recipe.id}/is-liked", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["liked"] is False
    
    def test_check_like_status_unauthorized(self, client, test_recipe):
        """Тест проверки статуса лайка без авторизации."""
        response = client.get(f"/recipes/{test_recipe.id}/is-liked")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_check_like_status_nonexistent_recipe(self, client, auth_headers):
        """Тест проверки статуса лайка несуществующего рецепта."""
        response = client.get("/recipes/99999/is-liked", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_toggle_like_functionality(self, client, auth_headers, test_recipe):
        """Тест переключения лайка (поставить/убрать)."""
        # Проверяем, что изначально лайка нет
        response = client.get(f"/recipes/{test_recipe.id}/is-liked", headers=auth_headers)
        assert response.json()["liked"] is False
        
        # Ставим лайк
        response = client.post(f"/recipes/{test_recipe.id}/like", headers=auth_headers)
        assert response.json()["liked"] is True
        
        # Проверяем, что лайк поставлен
        response = client.get(f"/recipes/{test_recipe.id}/is-liked", headers=auth_headers)
        assert response.json()["liked"] is True
        
        # Убираем лайк
        response = client.delete(f"/recipes/{test_recipe.id}/like", headers=auth_headers)
        assert response.json()["liked"] is False
        
        # Проверяем, что лайк убран
        response = client.get(f"/recipes/{test_recipe.id}/is-liked", headers=auth_headers)
        assert response.json()["liked"] is False
