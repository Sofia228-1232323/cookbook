import json
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, User, Category, Recipe, Comment, Like
from .auth import get_password_hash

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def seed_data():
    """Create seed data for testing"""
    db = SessionLocal()
    
    try:
        # Create categories
        categories_data = [
            {"name": "Завтрак", "description": "Рецепты для утреннего приема пищи"},
            {"name": "Обед", "description": "Основные блюда для обеда"},
            {"name": "Ужин", "description": "Блюда для вечернего приема пищи"},
            {"name": "Десерты", "description": "Сладкие блюда и выпечка"},
            {"name": "Напитки", "description": "Различные напитки"},
            {"name": "Закуски", "description": "Легкие закуски и аперитивы"},
            {"name": "Супы", "description": "Первые блюда"},
            {"name": "Салаты", "description": "Свежие салаты и закуски"},
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.add(category)
            categories.append(category)
        
        db.commit()
        
        # Create users
        users_data = [
            {
                "email": "chef@example.com",
                "username": "chef_master",
                "password": "password123"
            },
            {
                "email": "baker@example.com", 
                "username": "sweet_baker",
                "password": "password123"
            },
            {
                "email": "homecook@example.com",
                "username": "home_cook",
                "password": "password123"
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"])
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        
        # Create recipes
        recipes_data = [
            {
                "title": "Классический борщ",
                "description": "Традиционный украинский борщ с говядиной и свеклой",
                "ingredients": [
                    "500г говядины на кости",
                    "2 средние свеклы",
                    "300г капусты",
                    "3 картофелины",
                    "2 моркови",
                    "1 луковица",
                    "3 зубчика чеснока",
                    "2 ст.л. томатной пасты",
                    "Соль, перец по вкусу",
                    "Укроп и петрушка"
                ],
                "steps": [
                    "Отварить мясо в 3л воды 1.5 часа",
                    "Натереть свеклу на терке и обжарить с томатной пастой",
                    "Добавить нарезанные овощи в бульон",
                    "Варить 20 минут, добавить свеклу",
                    "Приправить солью и перцем",
                    "Подавать со сметаной и зеленью"
                ],
                "prep_time": 30,
                "cook_time": 120,
                "servings": 6,
                "difficulty": "medium",
                "author_id": users[0].id,
                "category_ids": [categories[6].id]  # Супы
            },
            {
                "title": "Шоколадный торт",
                "description": "Нежный шоколадный торт с кремом",
                "ingredients": [
                    "200г муки",
                    "200г сахара",
                    "200г сливочного масла",
                    "4 яйца",
                    "100г какао-порошка",
                    "1 ч.л. разрыхлителя",
                    "200г сметаны",
                    "100г сахарной пудры"
                ],
                "steps": [
                    "Взбить масло с сахаром до пышности",
                    "Добавить яйца по одному",
                    "Смешать муку, какао и разрыхлитель",
                    "Добавить сухие ингредиенты к тесту",
                    "Выпекать в форме 25-30 минут при 180°C",
                    "Взбить сметану с сахарной пудрой для крема",
                    "Собрать торт, промазав кремом"
                ],
                "prep_time": 45,
                "cook_time": 30,
                "servings": 8,
                "difficulty": "medium",
                "author_id": users[1].id,
                "category_ids": [categories[3].id]  # Десерты
            },
            {
                "title": "Омлет с сыром",
                "description": "Простой и вкусный омлет для завтрака",
                "ingredients": [
                    "4 яйца",
                    "100г твердого сыра",
                    "2 ст.л. молока",
                    "Соль, перец по вкусу",
                    "2 ст.л. сливочного масла",
                    "Зелень для подачи"
                ],
                "steps": [
                    "Взбить яйца с молоком, солью и перцем",
                    "Натереть сыр на терке",
                    "Разогреть сковороду с маслом",
                    "Вылить яйца, добавить сыр",
                    "Готовить на среднем огне 3-4 минуты",
                    "Сложить пополам и подавать с зеленью"
                ],
                "prep_time": 10,
                "cook_time": 5,
                "servings": 2,
                "difficulty": "easy",
                "author_id": users[2].id,
                "category_ids": [categories[0].id]  # Завтрак
            }
        ]
        
        for recipe_data in recipes_data:
            category_ids = recipe_data.pop("category_ids")
            recipe = Recipe(
                title=recipe_data["title"],
                description=recipe_data["description"],
                ingredients=json.dumps(recipe_data["ingredients"]),
                steps=json.dumps(recipe_data["steps"]),
                prep_time=recipe_data["prep_time"],
                cook_time=recipe_data["cook_time"],
                servings=recipe_data["servings"],
                difficulty=recipe_data["difficulty"],
                author_id=recipe_data["author_id"]
            )
            db.add(recipe)
            db.commit()
            db.refresh(recipe)
            
            # Add categories to recipe
            recipe_categories = [cat for cat in categories if cat.id in category_ids]
            recipe.categories = recipe_categories
            db.commit()
        
        # Create some comments
        comments_data = [
            {
                "content": "Отличный рецепт! Получился очень вкусный борщ.",
                "author_id": users[1].id,
                "recipe_id": 1
            },
            {
                "content": "Спасибо за рецепт торта! Семья в восторге.",
                "author_id": users[2].id,
                "recipe_id": 2
            },
            {
                "content": "Простой и быстрый завтрак. Рекомендую!",
                "author_id": users[0].id,
                "recipe_id": 3
            }
        ]
        
        for comment_data in comments_data:
            comment = Comment(**comment_data)
            db.add(comment)
        
        db.commit()
        
        # Create some likes
        likes_data = [
            {"user_id": users[1].id, "recipe_id": 1},
            {"user_id": users[2].id, "recipe_id": 1},
            {"user_id": users[0].id, "recipe_id": 2},
            {"user_id": users[2].id, "recipe_id": 2},
            {"user_id": users[0].id, "recipe_id": 3},
            {"user_id": users[1].id, "recipe_id": 3},
        ]
        
        for like_data in likes_data:
            like = Like(**like_data)
            db.add(like)
        
        db.commit()
        
        print("Seed data created successfully!")
        
    except Exception as e:
        print(f"Error creating seed data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    seed_data()


