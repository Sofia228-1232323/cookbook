# Cookbook - Платформа для обмена кулинарными рецептами

Полноценное веб-приложение для обмена кулинарными рецептами с современным интерфейсом и REST API.

## 🏗️ Архитектура

- **Frontend**: React 18 + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + Alembic
- **База данных**: SQLite (разработка) / PostgreSQL (продакшн)
- **Аутентификация**: JWT токены
- **Документация API**: Swagger/OpenAPI

## 🚀 Быстрый старт

### С Docker (рекомендуется)

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd Cookbook
```

2. Запустите все сервисы:
```bash
docker-compose up --build
```

3. Откройте в браузере:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger документация: http://localhost:8000/docs

### Локальная разработка

#### Backend

1. Перейдите в директорию backend:
```bash
cd backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `env.example`:
```bash
cp env.example .env
```

5. Запустите миграции:
```bash
alembic upgrade head
```

6. Создайте тестовые данные:
```bash
python -m app.seed_data
```

7. Запустите сервер:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Перейдите в директорию frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите приложение:
```bash
npm start
```

## 📋 Функционал

### Пользователи
- ✅ Регистрация и авторизация
- ✅ JWT аутентификация
- ✅ Профиль пользователя

### Рецепты
- ✅ Создание рецептов с фото
- ✅ Просмотр списка рецептов
- ✅ Детальный просмотр рецепта
- ✅ Редактирование рецептов (только автор)
- ✅ Удаление рецептов (только автор)
- ✅ Поиск и фильтрация по категориям
- ✅ Пагинация

### Взаимодействие
- ✅ Лайки рецептов
- ✅ Комментарии к рецептам
- ✅ Удаление комментариев (только автор)

### UI/UX
- ✅ Адаптивный дизайн
- ✅ Темная/светлая тема
- ✅ Минималистичный интерфейс
- ✅ Уведомления (toast)

## 🔧 API Эндпоинты

### Аутентификация
- `POST /auth/register` - Регистрация
- `POST /auth/login` - Вход
- `GET /auth/me` - Информация о текущем пользователе

### Пользователи
- `GET /users/` - Список пользователей
- `GET /users/{id}` - Информация о пользователе

### Рецепты
- `GET /recipes` - Список рецептов (с пагинацией и фильтрацией)
- `GET /recipes/{id}` - Детальная информация о рецепте
- `POST /recipes` - Создание рецепта
- `PUT /recipes/{id}` - Редактирование рецепта
- `DELETE /recipes/{id}` - Удаление рецепта

### Комментарии
- `GET /recipes/{id}/comments` - Комментарии к рецепту
- `POST /recipes/{id}/comments` - Добавление комментария
- `DELETE /comments/{id}` - Удаление комментария

### Лайки
- `POST /recipes/{id}/like` - Поставить лайк
- `DELETE /recipes/{id}/like` - Убрать лайк

## 🗄️ База данных

### Модели
- **User** - Пользователи
- **Recipe** - Рецепты
- **Category** - Категории
- **Comment** - Комментарии
- **Like** - Лайки

### Миграции
```bash
# Создать новую миграцию
alembic revision --autogenerate -m "Description"

# Применить миграции
alembic upgrade head

# Откатить миграции
alembic downgrade -1
```

## 🧪 Тестовые данные

После запуска миграций выполните:
```bash
python -m app.seed_data
```

Создастся:
- 3 тестовых пользователя
- 8 категорий рецептов
- 3 примера рецептов
- Комментарии и лайки

### Тестовые аккаунты
- **Email**: chef@example.com, **Пароль**: password123
- **Email**: baker@example.com, **Пароль**: password123
- **Email**: homecook@example.com, **Пароль**: password123

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` в директории `backend`:

```env
DATABASE_URL=sqlite:///./cookbook.db
# Для PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost:5432/cookbook

SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=uploads
MAX_FILE_SIZE=5242880
```

## 📁 Структура проекта

```
Cookbook/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── seed_data.py
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── recipes.py
│   │       ├── comments.py
│   │       └── likes.py
│   ├── alembic/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Деплой

### Docker Compose (продакшн)

1. Обновите переменные окружения для продакшна
2. Запустите:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Вклад в проект

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 👥 Авторы

- **София** - [GitHub](https://github.com/Sofia228-1232323)



