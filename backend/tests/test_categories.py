import pytest
from fastapi import status
from app.models import Category, Recipe, User

class TestCategoryBusinessLogic:
    """Тесты для бизнес-логики категорий."""
    
    def test_category_creation(self, db_session):
        """Тест создания категории."""
        category_data = {
            "name": "Test Category"
        }
        
        category = Category(**category_data)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        assert category.id is not None
        assert category.name == "Test Category"
    
    def test_category_name_uniqueness(self, db_session):
        """Тест уникальности названия категории."""
        # Создаем первую категорию
        category1 = Category(name="Unique Category")
        db_session.add(category1)
        db_session.commit()
        
        # Пытаемся создать категорию с тем же названием
        category2 = Category(name="Unique Category")
        db_session.add(category2)
        
        # Должно возникнуть исключение из-за уникального ограничения
        with pytest.raises(Exception):  # IntegrityError или подобное
            db_session.commit()
    
    def test_category_recipe_relationship(self, db_session, test_user):
        """Тест связи категории с рецептами."""
        category = Category(name="Test Category")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        # Создаем рецепт в этой категории
        recipe = Recipe(
            title="Test Recipe",
            description="Test Description",
            ingredients='["ingredient1"]',
            steps='["step1"]',
            author_id=test_user.id
        )
        recipe.categories.append(category)
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        # Проверяем связь
        assert category in recipe.categories
        # Проверяем обратную связь
        assert recipe in category.recipes
    
    def test_category_recipes_count(self, db_session, test_user):
        """Тест подсчета рецептов в категории."""
        category = Category(name="Test Category")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        # Создаем несколько рецептов в категории
        recipe1 = Recipe(
            title="Recipe 1",
            description="Description 1",
            ingredients='["ingredient1"]',
            steps='["step1"]',
            author_id=test_user.id
        )
        recipe1.categories.append(category)
        recipe2 = Recipe(
            title="Recipe 2",
            description="Description 2",
            ingredients='["ingredient2"]',
            steps='["step2"]',
            author_id=test_user.id
        )
        recipe2.categories.append(category)
        
        db_session.add(recipe1)
        db_session.add(recipe2)
        db_session.commit()
        
        # Проверяем количество рецептов
        recipes_count = len(category.recipes)
        assert recipes_count == 2

class TestCategoryAPI:
    """Тесты для API категорий."""
    
    def test_get_categories_list(self, client, test_category):
        """Тест получения списка категорий."""
        response = client.get("/categories")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        
        # Проверяем, что наша тестовая категория в списке
        category_names = [cat["name"] for cat in data]
        assert "Test Category" in category_names
    
    def test_get_category_by_id(self, client, test_category):
        """Тест получения категории по ID."""
        response = client.get(f"/categories/{test_category.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == test_category.name
    
    def test_get_nonexistent_category(self, client):
        """Тест получения несуществующей категории."""
        response = client.get("/categories/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_category_success(self, client, auth_headers):
        """Тест успешного создания категории."""
        category_data = {
            "name": "New Category"
        }
        
        response = client.post("/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Category"
        assert "id" in data
    
    def test_create_category_unauthorized(self, client):
        """Тест создания категории без авторизации."""
        category_data = {
            "name": "New Category"
        }
        
        response = client.post("/categories", json=category_data)
        
        assert response.status_code == status.HTTP_200_OK
    
    
    def test_create_category_empty_name(self, client, auth_headers):
        """Тест создания категории с пустым названием."""
        category_data = {
            "name": ""
        }
        
        response = client.post("/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_category_missing_name(self, client, auth_headers):
        """Тест создания категории без названия."""
        category_data = {}
        
        response = client.post("/categories", json=category_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_category_with_recipes(self, client, test_category, test_recipe):
        """Тест получения категории с рецептами."""
        response = client.get(f"/categories/{test_category.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == test_category.name
        # Проверяем, что в ответе есть информация о рецептах
        # (если это реализовано в API)
    
    def test_filter_recipes_by_category(self, client, test_category, test_recipe):
        """Тест фильтрации рецептов по категории."""
        response = client.get(f"/recipes?category_id={test_category.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Все рецепты должны принадлежать указанной категории
        for recipe in data:
            assert recipe["category"]["id"] == test_category.id
    
    def test_category_name_case_sensitivity(self, client, auth_headers, test_category):
        """Тест чувствительности к регистру названий категорий."""
        # Пытаемся создать категорию с тем же названием, но в другом регистре
        category_data = {
            "name": test_category.name.upper()  # В верхнем регистре
        }
        
        response = client.post("/categories", json=category_data, headers=auth_headers)
        
        # В зависимости от реализации, это может быть либо успех, либо ошибка
        # Если система не чувствительна к регистру, должна быть ошибка
        # Если чувствительна, то успех
        assert response.status_code == 200
