import pytest
from fastapi import status
from app.models import Recipe, User, Category

class TestRecipeBusinessLogic:
    """Тесты для бизнес-логики рецептов."""
    
    def test_recipe_creation(self, db_session, test_user, test_category):
        """Тест создания рецепта."""
        recipe_data = {
            "title": "Test Recipe",
            "description": "Test Description",
            "ingredients": '["ingredient1", "ingredient2"]',
            "steps": '["step1", "step2"]',
            "author_id": test_user.id,
            "category_id": test_category.id
        }
        
        recipe = Recipe(**recipe_data)
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        assert recipe.id is not None
        assert recipe.title == "Test Recipe"
        assert recipe.author_id == test_user.id
        assert recipe.category_id == test_category.id
    
    def test_recipe_ingredients_parsing(self, db_session, test_user, test_category):
        """Тест парсинга ингредиентов."""
        recipe = Recipe(
            title="Test Recipe",
            description="Test Description",
            ingredients='["ingredient1", "ingredient2", "ingredient3"]',
            steps='["step1", "step2"]',
            author_id=test_user.id,
            category_id=test_category.id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        ingredients_list = recipe.ingredients_list
        assert len(ingredients_list) == 3
        assert "ingredient1" in ingredients_list
        assert "ingredient2" in ingredients_list
        assert "ingredient3" in ingredients_list
    
    def test_recipe_steps_parsing(self, db_session, test_user, test_category):
        """Тест парсинга шагов приготовления."""
        recipe = Recipe(
            title="Test Recipe",
            description="Test Description",
            ingredients='["ingredient1"]',
            steps='["step1", "step2", "step3"]',
            author_id=test_user.id,
            category_id=test_category.id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        steps_list = recipe.steps_list
        assert len(steps_list) == 3
        assert "step1" in steps_list
        assert "step2" in steps_list
        assert "step3" in steps_list
    
    def test_recipe_likes_count(self, db_session, test_user, test_category):
        """Тест подсчета лайков."""
        from app.models import Like
        
        recipe = Recipe(
            title="Test Recipe",
            description="Test Description",
            ingredients='["ingredient1"]',
            steps='["step1"]',
            author_id=test_user.id,
            category_id=test_category.id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        # Добавляем лайки
        like1 = Like(user_id=test_user.id, recipe_id=recipe.id)
        db_session.add(like1)
        db_session.commit()
        
        assert recipe.likes_count == 1
    
    def test_recipe_comments_count(self, db_session, test_user, test_category):
        """Тест подсчета комментариев."""
        from app.models import Comment
        
        recipe = Recipe(
            title="Test Recipe",
            description="Test Description",
            ingredients='["ingredient1"]',
            steps='["step1"]',
            author_id=test_user.id,
            category_id=test_category.id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        # Добавляем комментарии
        comment1 = Comment(content="Great recipe!", author_id=test_user.id, recipe_id=recipe.id)
        comment2 = Comment(content="Delicious!", author_id=test_user.id, recipe_id=recipe.id)
        db_session.add(comment1)
        db_session.add(comment2)
        db_session.commit()
        
        assert recipe.comments_count == 2

class TestRecipeAPI:
    """Тесты для API рецептов."""
    
    def test_create_recipe_success(self, client, auth_headers, test_category):
        """Тест успешного создания рецепта."""
        recipe_data = {
            "title": "New Recipe",
            "description": "Recipe Description",
            "ingredients": '["ingredient1", "ingredient2"]',
            "steps": '["step1", "step2"]',
            "category_ids": [test_category.id]
        }
        
        response = client.post("/recipes", json=recipe_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Recipe"
        assert data["description"] == "Recipe Description"
        assert "id" in data
        assert "author" in data
    
    def test_create_recipe_unauthorized(self, client, test_category):
        """Тест создания рецепта без авторизации."""
        recipe_data = {
            "title": "New Recipe",
            "description": "Recipe Description",
            "ingredients": '["ingredient1", "ingredient2"]',
            "steps": '["step1", "step2"]',
            "category_ids": [test_category.id]
        }
        
        response = client.post("/recipes", json=recipe_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_recipes_list(self, client, test_recipe):
        """Тест получения списка рецептов."""
        response = client.get("/recipes")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recipes" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert len(data["recipes"]) >= 1
    
    def test_get_recipes_with_pagination(self, client):
        """Тест пагинации списка рецептов."""
        response = client.get("/recipes?page=1&limit=5")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 5
    
    def test_get_recipes_with_category_filter(self, client, test_category):
        """Тест фильтрации рецептов по категории."""
        response = client.get(f"/recipes?category_id={test_category.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Все рецепты должны принадлежать указанной категории
        for recipe in data["recipes"]:
            assert recipe["category"]["id"] == test_category.id
    
    def test_get_recipe_by_id(self, client, test_recipe):
        """Тест получения рецепта по ID."""
        response = client.get(f"/recipes/{test_recipe.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_recipe.id
        assert data["title"] == test_recipe.title
        assert "author" in data
        assert "category" in data
    
    def test_get_nonexistent_recipe(self, client):
        """Тест получения несуществующего рецепта."""
        response = client.get("/recipes/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_recipe_success(self, client, auth_headers, test_recipe):
        """Тест успешного обновления рецепта."""
        update_data = {
            "title": "Updated Recipe",
            "description": "Updated Description",
            "ingredients": '["new ingredient"]',
            "steps": '["new step"]'
        }
        
        response = client.put(f"/recipes/{test_recipe.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Recipe"
        assert data["description"] == "Updated Description"
    
    def test_update_recipe_unauthorized(self, client, test_recipe):
        """Тест обновления рецепта без авторизации."""
        update_data = {
            "title": "Updated Recipe",
            "description": "Updated Description"
        }
        
        response = client.put(f"/recipes/{test_recipe.id}", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_recipe_success(self, client, auth_headers, test_recipe):
        """Тест успешного удаления рецепта."""
        response = client.delete(f"/recipes/{test_recipe.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Recipe deleted successfully"
    
    def test_delete_recipe_unauthorized(self, client, test_recipe):
        """Тест удаления рецепта без авторизации."""
        response = client.delete(f"/recipes/{test_recipe.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_like_recipe_success(self, client, auth_headers, test_recipe):
        """Тест успешного лайка рецепта."""
        response = client.post(f"/recipes/{test_recipe.id}/like", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "liked" in data
        assert data["liked"] is True
    
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
    
    def test_check_recipe_like_status(self, client, auth_headers, test_recipe):
        """Тест проверки статуса лайка рецепта."""
        response = client.get(f"/recipes/{test_recipe.id}/is-liked", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "liked" in data
        assert isinstance(data["liked"], bool)
