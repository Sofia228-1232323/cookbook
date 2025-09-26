import pytest
from fastapi import status
from app.models import Comment, Recipe, User

class TestCommentBusinessLogic:
    """Тесты для бизнес-логики комментариев."""
    
    def test_comment_creation(self, db_session, test_user, test_recipe):
        """Тест создания комментария."""
        comment_data = {
            "content": "Great recipe!",
            "author_id": test_user.id,
            "recipe_id": test_recipe.id
        }
        
        comment = Comment(**comment_data)
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        
        assert comment.id is not None
        assert comment.content == "Great recipe!"
        assert comment.author_id == test_user.id
        assert comment.recipe_id == test_recipe.id
    
    def test_comment_content_validation(self, db_session, test_user, test_recipe):
        """Тест валидации содержимого комментария."""
        # Пустой комментарий
        comment = Comment(
            content="",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        
        # Комментарий должен быть создан, но содержимое пустое
        assert comment.content == ""
    
    def test_comment_author_relationship(self, db_session, test_user, test_recipe):
        """Тест связи комментария с автором."""
        comment = Comment(
            content="Test comment",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        
        # Проверяем связь с автором
        assert comment.author_id == test_user.id
        # Проверяем обратную связь
        assert comment in test_user.comments
    
    def test_comment_recipe_relationship(self, db_session, test_user, test_recipe):
        """Тест связи комментария с рецептом."""
        comment = Comment(
            content="Test comment",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        
        # Проверяем связь с рецептом
        assert comment.recipe_id == test_recipe.id
        # Проверяем обратную связь
        assert comment in test_recipe.comments

class TestCommentAPI:
    """Тесты для API комментариев."""
    
    def test_create_comment_success(self, client, auth_headers, test_recipe):
        """Тест успешного создания комментария."""
        comment_data = {
            "content": "This is a great recipe!"
        }
        
        response = client.post(f"/recipes/{test_recipe.id}/comments", json=comment_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "This is a great recipe!"
        assert "id" in data
        assert "author" in data
        assert data["author"]["email"] == "test@example.com"
    
    def test_create_comment_unauthorized(self, client, test_recipe):
        """Тест создания комментария без авторизации."""
        comment_data = {
            "content": "This is a great recipe!"
        }
        
        response = client.post(f"/recipes/{test_recipe.id}/comments", json=comment_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_comment_nonexistent_recipe(self, client, auth_headers):
        """Тест создания комментария к несуществующему рецепту."""
        comment_data = {
            "content": "This is a great recipe!"
        }
        
        response = client.post("/recipes/99999/comments", json=comment_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_comment_empty_content(self, client, auth_headers, test_recipe):
        """Тест создания комментария с пустым содержимым."""
        comment_data = {
            "content": ""
        }
        
        response = client.post(f"/recipes/{test_recipe.id}/comments", json=comment_data, headers=auth_headers)
        
        # Пустой комментарий должен быть отклонен
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_recipe_comments(self, client, test_recipe, test_user):
        """Тест получения комментариев к рецепту."""
        # Создаем комментарий напрямую в базе
        from app.models import Comment
        comment = Comment(
            content="Test comment",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        from app.database import get_db
        db = next(get_db())
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        response = client.get(f"/recipes/{test_recipe.id}/comments")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["content"] == "Test comment"
        assert "author" in data[0]
        assert data[0]["author"]["email"] == "test@example.com"
    
    def test_get_comments_nonexistent_recipe(self, client):
        """Тест получения комментариев несуществующего рецепта."""
        response = client.get("/recipes/99999/comments")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_comment_success(self, client, auth_headers, test_recipe, test_user):
        """Тест успешного удаления комментария."""
        # Создаем комментарий
        from app.models import Comment
        comment = Comment(
            content="Test comment to delete",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        from app.database import get_db
        db = next(get_db())
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        response = client.delete(f"/comments/{comment.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Comment deleted successfully"
    
    def test_delete_comment_unauthorized(self, client, test_recipe, test_user):
        """Тест удаления комментария без авторизации."""
        # Создаем комментарий
        from app.models import Comment
        comment = Comment(
            content="Test comment to delete",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        from app.database import get_db
        db = next(get_db())
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        response = client.delete(f"/comments/{comment.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_nonexistent_comment(self, client, auth_headers):
        """Тест удаления несуществующего комментария."""
        response = client.delete("/comments/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_comment_success(self, client, auth_headers, test_recipe, test_user):
        """Тест успешного обновления комментария."""
        # Создаем комментарий
        from app.models import Comment
        comment = Comment(
            content="Original comment",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        from app.database import get_db
        db = next(get_db())
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        update_data = {
            "content": "Updated comment content"
        }
        
        response = client.put(f"/comments/{comment.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == "Updated comment content"
    
    def test_update_comment_unauthorized(self, client, test_recipe, test_user):
        """Тест обновления комментария без авторизации."""
        # Создаем комментарий
        from app.models import Comment
        comment = Comment(
            content="Original comment",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        from app.database import get_db
        db = next(get_db())
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        update_data = {
            "content": "Updated comment content"
        }
        
        response = client.put(f"/comments/{comment.id}", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
