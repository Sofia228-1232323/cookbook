import pytest
from fastapi import status
from app.models import User, Recipe, Category, Comment, Like
from app.auth import get_password_hash, verify_password

class TestUserBusinessLogic:
    """Тесты для бизнес-логики пользователей."""
    
    def test_user_registration_validation(self, db_session):
        """Тест валидации регистрации пользователя."""
        # Валидные данные
        valid_user = User(
            email="valid@example.com",
            username="validuser",
            hashed_password=get_password_hash("validpassword123")
        )
        db_session.add(valid_user)
        db_session.commit()
        db_session.refresh(valid_user)
        
        assert valid_user.id is not None
        assert valid_user.email == "valid@example.com"
        assert valid_user.username == "validuser"
        assert verify_password("validpassword123", valid_user.hashed_password)
    
    def test_user_email_uniqueness_constraint(self, db_session):
        """Тест ограничения уникальности email."""
        user1 = User(
            email="unique@example.com",
            username="user1",
            hashed_password="$2b$12$test_hash_here"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Попытка создать пользователя с тем же email
        user2 = User(
            email="unique@example.com",
            username="user2",
            hashed_password="$2b$12$test_hash_here"
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_user_username_uniqueness_constraint(self, db_session):
        """Тест ограничения уникальности username."""
        user1 = User(
            email="user1@example.com",
            username="unique_username",
            hashed_password="$2b$12$test_hash_here"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Попытка создать пользователя с тем же username
        user2 = User(
            email="user2@example.com",
            username="unique_username",
            hashed_password="$2b$12$test_hash_here"
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_user_password_security(self, db_session):
        """Тест безопасности паролей."""
        password = "securepassword123"
        hashed = get_password_hash(password)
        
        # Хеш должен отличаться от оригинального пароля
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt format
        
        # Проверка пароля должна работать
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

class TestRecipeBusinessLogic:
    """Тесты для бизнес-логики рецептов."""
    
    def test_recipe_creation_with_validation(self, db_session, test_user, test_category):
        """Тест создания рецепта с валидацией."""
        recipe = Recipe(
            title="Valid Recipe",
            description="Valid Description",
            ingredients='["ingredient1", "ingredient2"]',
            steps='["step1", "step2"]',
            author_id=test_user.id,
            category_id=test_category.id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        assert recipe.id is not None
        assert recipe.title == "Valid Recipe"
        assert recipe.author_id == test_user.id
        assert recipe.category_id == test_category.id
    
    def test_recipe_ingredients_parsing(self, db_session, test_user, test_category):
        """Тест парсинга ингредиентов рецепта."""
        recipe = Recipe(
            title="Test Recipe",
            description="Test Description",
            ingredients='["ingredient1", "ingredient2", "ingredient3"]',
            steps='["step1"]',
            author_id=test_user.id,
            category_id=test_category.id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        ingredients = recipe.ingredients_list
        assert len(ingredients) == 3
        assert "ingredient1" in ingredients
        assert "ingredient2" in ingredients
        assert "ingredient3" in ingredients
    
    def test_recipe_steps_parsing(self, db_session, test_user, test_category):
        """Тест парсинга шагов приготовления."""
        recipe = Recipe(
            title="Test Recipe",
            description="Test Description",
            ingredients='["ingredient1"]',
            steps='["step1", "step2", "step3", "step4"]',
            author_id=test_user.id,
            category_id=test_category.id
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        steps = recipe.steps_list
        assert len(steps) == 4
        assert "step1" in steps
        assert "step2" in steps
        assert "step3" in steps
        assert "step4" in steps
    
    def test_recipe_likes_count_calculation(self, db_session, test_user, test_category):
        """Тест подсчета лайков рецепта."""
        # Создаем рецепт
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
        
        # Создаем дополнительных пользователей для лайков
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password="$2b$12$test_hash_here"
        )
        user3 = User(
            email="user3@example.com",
            username="user3",
            hashed_password="$2b$12$test_hash_here"
        )
        db_session.add(user2)
        db_session.add(user3)
        db_session.commit()
        
        # Создаем лайки
        like1 = Like(user_id=test_user.id, recipe_id=recipe.id)
        like2 = Like(user_id=user2.id, recipe_id=recipe.id)
        like3 = Like(user_id=user3.id, recipe_id=recipe.id)
        
        db_session.add(like1)
        db_session.add(like2)
        db_session.add(like3)
        db_session.commit()
        
        # Проверяем подсчет лайков
        assert recipe.likes_count == 3
    
    def test_recipe_comments_count_calculation(self, db_session, test_user, test_category):
        """Тест подсчета комментариев рецепта."""
        # Создаем рецепт
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
        
        # Создаем комментарии
        comment1 = Comment(
            content="Great recipe!",
            author_id=test_user.id,
            recipe_id=recipe.id
        )
        comment2 = Comment(
            content="Delicious!",
            author_id=test_user.id,
            recipe_id=recipe.id
        )
        comment3 = Comment(
            content="Will try again!",
            author_id=test_user.id,
            recipe_id=recipe.id
        )
        
        db_session.add(comment1)
        db_session.add(comment2)
        db_session.add(comment3)
        db_session.commit()
        
        # Проверяем подсчет комментариев
        assert recipe.comments_count == 3

class TestCategoryBusinessLogic:
    """Тесты для бизнес-логики категорий."""
    
    def test_category_creation_with_validation(self, db_session):
        """Тест создания категории с валидацией."""
        category = Category(name="Valid Category")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        assert category.id is not None
        assert category.name == "Valid Category"
    
    def test_category_name_uniqueness_constraint(self, db_session):
        """Тест ограничения уникальности названия категории."""
        category1 = Category(name="Unique Category")
        db_session.add(category1)
        db_session.commit()
        
        # Попытка создать категорию с тем же названием
        category2 = Category(name="Unique Category")
        db_session.add(category2)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_category_recipe_relationship(self, db_session, test_user):
        """Тест связи категории с рецептами."""
        category = Category(name="Test Category")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        # Создаем рецепты в категории
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
        
        # Проверяем связь
        assert len(category.recipes) == 2
        assert recipe1 in category.recipes
        assert recipe2 in category.recipes

class TestCommentBusinessLogic:
    """Тесты для бизнес-логики комментариев."""
    
    def test_comment_creation_with_validation(self, db_session, test_user, test_recipe):
        """Тест создания комментария с валидацией."""
        comment = Comment(
            content="Valid comment content",
            author_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        
        assert comment.id is not None
        assert comment.content == "Valid comment content"
        assert comment.author_id == test_user.id
        assert comment.recipe_id == test_recipe.id
    
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
        assert comment in test_recipe.comments

class TestLikeBusinessLogic:
    """Тесты для бизнес-логики лайков."""
    
    def test_like_creation_with_validation(self, db_session, test_user, test_recipe):
        """Тест создания лайка с валидацией."""
        like = Like(
            user_id=test_user.id,
            recipe_id=test_recipe.id
        )
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
        assert like in test_recipe.likes
    
    def test_like_uniqueness_constraint(self, db_session, test_user, test_recipe):
        """Тест ограничения уникальности лайка."""
        like1 = Like(
            user_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(like1)
        db_session.commit()
        
        # Попытка создать дублирующий лайк
        like2 = Like(
            user_id=test_user.id,
            recipe_id=test_recipe.id
        )
        db_session.add(like2)
        
        with pytest.raises(Exception):
            db_session.commit()

class TestDataIntegrity:
    """Тесты для целостности данных."""
    
    def test_cascade_delete_recipe_comments(self, db_session, test_user, test_category):
        """Тест каскадного удаления комментариев при удалении рецепта."""
        # Создаем рецепт
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
        
        # Создаем комментарии
        comment1 = Comment(
            content="Comment 1",
            author_id=test_user.id,
            recipe_id=recipe.id
        )
        comment2 = Comment(
            content="Comment 2",
            author_id=test_user.id,
            recipe_id=recipe.id
        )
        db_session.add(comment1)
        db_session.add(comment2)
        db_session.commit()
        
        # Удаляем рецепт
        db_session.delete(recipe)
        db_session.commit()
        
        # Проверяем, что комментарии тоже удалены
        remaining_comments = db_session.query(Comment).filter(
            Comment.recipe_id == recipe.id
        ).count()
        assert remaining_comments == 0
    
    def test_cascade_delete_recipe_likes(self, db_session, test_user, test_category):
        """Тест каскадного удаления лайков при удалении рецепта."""
        # Создаем рецепт
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
        
        # Создаем лайки
        like1 = Like(
            user_id=test_user.id,
            recipe_id=recipe.id
        )
        db_session.add(like1)
        db_session.commit()
        
        # Удаляем рецепт
        db_session.delete(recipe)
        db_session.commit()
        
        # Проверяем, что лайки тоже удалены
        remaining_likes = db_session.query(Like).filter(
            Like.recipe_id == recipe.id
        ).count()
        assert remaining_likes == 0
