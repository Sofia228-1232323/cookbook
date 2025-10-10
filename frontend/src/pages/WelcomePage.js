import React from 'react';
import { Link } from 'react-router-dom';

const WelcomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-orange-600">🍳 Cookbook</h1>
            </div>
            <div className="flex space-x-4">
              <Link 
                to="/login" 
                className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
              >
                Войти
              </Link>
              <Link 
                to="/register" 
                className="border border-orange-600 text-orange-600 px-4 py-2 rounded-lg hover:bg-orange-50 transition-colors"
              >
                Регистрация
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Добро пожаловать в мир кулинарии!
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Откройте для себя тысячи рецептов, делитесь своими кулинарными шедеврами 
            и находите вдохновение для новых блюд
          </p>
          <Link 
            to="/register" 
            className="inline-block bg-orange-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-orange-700 transition-colors shadow-lg"
          >
            Начать готовить
          </Link>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-xl font-semibold mb-2">Коллекция рецептов</h3>
            <p className="text-gray-600">
              Тысячи проверенных рецептов от домашних поваров со всего мира
            </p>
          </div>
          
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="text-4xl mb-4">👥</div>
            <h3 className="text-xl font-semibold mb-2">Сообщество</h3>
            <p className="text-gray-600">
              Общайтесь с единомышленниками, делитесь опытом и получайте советы
            </p>
          </div>
          
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <div className="text-4xl mb-4">⭐</div>
            <h3 className="text-xl font-semibold mb-2">Избранное</h3>
            <p className="text-gray-600">
              Сохраняйте понравившиеся рецепты и создавайте свою коллекцию
            </p>
          </div>
        </div>

        {/* Popular Recipes Preview */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h3 className="text-2xl font-bold text-center mb-8">Популярные рецепты</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl mb-2">🍲</div>
              <h4 className="font-semibold mb-1">Борщ украинский</h4>
              <p className="text-sm text-gray-600">Классический украинский борщ</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🍳</div>
              <h4 className="font-semibold mb-1">Омлет с сыром</h4>
              <p className="text-sm text-gray-600">Нежный омлет с сыром</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🍰</div>
              <h4 className="font-semibold mb-1">Шоколадный торт</h4>
              <p className="text-sm text-gray-600">Нежный шоколадный торт</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2024 Cookbook. Все права защищены.</p>
        </div>
      </footer>
    </div>
  );
};

export default WelcomePage;
