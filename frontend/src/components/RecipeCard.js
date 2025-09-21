import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, Users, Heart, MessageCircle, User } from 'lucide-react';

const RecipeCard = ({ recipe }) => {
  const totalTime = (recipe.prep_time || 0) + (recipe.cook_time || 0);
  
  const formatTime = (minutes) => {
    if (minutes < 60) {
      return `${minutes} мин`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}ч ${mins}мин` : `${hours}ч`;
  };

  // Генерируем цветовую схему на основе ID рецепта
  const getGradientClass = (id) => {
    const gradients = [
      'from-orange-400 to-red-500 group-hover:from-orange-500 group-hover:to-red-600',
      'from-green-400 to-blue-500 group-hover:from-green-500 group-hover:to-blue-600',
      'from-purple-400 to-pink-500 group-hover:from-purple-500 group-hover:to-pink-600',
      'from-yellow-400 to-orange-500 group-hover:from-yellow-500 group-hover:to-orange-600',
      'from-blue-400 to-purple-500 group-hover:from-blue-500 group-hover:to-purple-600',
      'from-pink-400 to-red-500 group-hover:from-pink-500 group-hover:to-red-600',
      'from-indigo-400 to-blue-500 group-hover:from-indigo-500 group-hover:to-blue-600',
      'from-emerald-400 to-green-500 group-hover:from-emerald-500 group-hover:to-green-600'
    ];
    return gradients[id % gradients.length];
  };

  // Получаем эмодзи для рецепта на основе названия
  const getRecipeEmoji = (title) => {
    const titleLower = title.toLowerCase();
    if (titleLower.includes('борщ') || titleLower.includes('суп')) return '🍲';
    if (titleLower.includes('торт') || titleLower.includes('десерт') || titleLower.includes('тирамису')) return '🍰';
    if (titleLower.includes('омлет') || titleLower.includes('яичн')) return '🍳';
    if (titleLower.includes('паста') || titleLower.includes('макарон')) return '🍝';
    if (titleLower.includes('салат') || titleLower.includes('цезарь')) return '🥗';
    if (titleLower.includes('пицца')) return '🍕';
    if (titleLower.includes('бургер')) return '🍔';
    return '🍽️';
  };

  return (
    <Link to={`/recipe/${recipe.id}`} className="group">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden">
                {/* Image */}
                <div className="aspect-w-16 aspect-h-9 bg-gray-200 dark:bg-gray-700">
                  {recipe.image_url ? (
                    <img
                      src={recipe.image_url.startsWith('http') ? recipe.image_url : `http://localhost:8000${recipe.image_url}`}
                      alt={recipe.title}
                      className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
                    />
                  ) : (
                    <div className={`w-full h-48 flex flex-col items-center justify-center bg-gradient-to-br ${getGradientClass(recipe.id)} transition-all duration-200`}>
                      <div className="text-white text-center px-4">
                        <div className="text-4xl mb-3">
                          {getRecipeEmoji(recipe.title)}
                        </div>
                        <div className="text-xl font-bold mb-2">
                          {recipe.title.split(' ').slice(0, 2).join(' ')}
                        </div>
                        <div className="text-sm opacity-90">
                          Вкусный рецепт
                        </div>
                      </div>
                    </div>
                  )}
                </div>

        {/* Content */}
        <div className="p-4">
          {/* Title */}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
            {recipe.title}
          </h3>

          {/* Description */}
          {recipe.description && (
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-2">
              {recipe.description}
            </p>
          )}

          {/* Meta info */}
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-3">
            <div className="flex items-center space-x-4">
              {totalTime > 0 && (
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4" />
                  <span>{formatTime(totalTime)}</span>
                </div>
              )}
              {recipe.servings && (
                <div className="flex items-center space-x-1">
                  <Users className="h-4 w-4" />
                  <span>{recipe.servings} порций</span>
                </div>
              )}
            </div>
            {recipe.difficulty && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                recipe.difficulty === 'easy' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : recipe.difficulty === 'medium'
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}>
                {recipe.difficulty === 'easy' ? 'Легко' : 
                 recipe.difficulty === 'medium' ? 'Средне' : 'Сложно'}
              </span>
            )}
          </div>

          {/* Author and stats */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <User className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {recipe.author.username}
              </span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-1">
                <Heart className="h-4 w-4 text-red-500" />
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {recipe.likes_count || 0}
                </span>
              </div>
              <div className="flex items-center space-x-1">
                <MessageCircle className="h-4 w-4 text-blue-500" />
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {recipe.comments_count || 0}
                </span>
              </div>
            </div>
          </div>

          {/* Categories */}
          {recipe.categories && recipe.categories.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {recipe.categories.map((category) => (
                <span
                  key={category.id}
                  className="px-2 py-1 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 text-xs rounded-full"
                >
                  {category.name}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
};

export default RecipeCard;
