import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../config/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { 
  Clock, 
  Users, 
  Heart, 
  User, 
  Send,
  Trash2,
  Edit
} from 'lucide-react';

const RecipeDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [recipe, setRecipe] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState('');
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);

  useEffect(() => {
    const fetchRecipeData = async () => {
      try {
        setLoading(true);
        console.log('Fetching recipe:', id);
        
        // Fetch recipe and comments in parallel
        const [recipeResponse, commentsResponse] = await Promise.all([
          api.get(`/recipes/${id}`),
          api.get(`/recipes/${id}/comments`)
        ]);
        
        console.log('Recipe API response:', recipeResponse.data);
        console.log('Comments API response:', commentsResponse.data);
        
        const recipe = recipeResponse.data;
        const comments = Array.isArray(commentsResponse.data) ? commentsResponse.data : [];
        
        console.log('Recipe data:', recipe);
        console.log('Comments data:', comments);
        
        setRecipe(recipe);
        setComments(comments);
        setLikesCount(recipe.likes_count || 0);
        
        // Проверяем, лайкнут ли рецепт пользователем (используем localStorage)
        const likedRecipes = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
        setIsLiked(likedRecipes.includes(parseInt(id)));
      } catch (error) {
        console.error('Error fetching recipe data:', error);
        toast.error('Ошибка загрузки рецепта');
      } finally {
        setLoading(false);
      }
    };

    fetchRecipeData();
  }, [id]);

  const handleLike = async () => {
    if (!isAuthenticated) {
      toast.error('Войдите в аккаунт, чтобы поставить лайк');
      return;
    }

    try {
      if (isLiked) {
        // Убираем лайк
        await api.delete(`/recipes/${id}/like`);
        setIsLiked(false);
        setLikesCount(prev => prev - 1);
        
        // Обновляем localStorage
        const likedRecipes = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
        const updatedLikedRecipes = likedRecipes.filter(recipeId => recipeId !== parseInt(id));
        localStorage.setItem('likedRecipes', JSON.stringify(updatedLikedRecipes));
        
        toast.success('Лайк убран');
      } else {
        // Ставим лайк
        await api.post(`/recipes/${id}/like`);
        setIsLiked(true);
        setLikesCount(prev => prev + 1);
        
        // Обновляем localStorage
        const likedRecipes = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
        if (!likedRecipes.includes(parseInt(id))) {
          likedRecipes.push(parseInt(id));
          localStorage.setItem('likedRecipes', JSON.stringify(likedRecipes));
        }
        
        toast.success('Лайк поставлен');
      }
    } catch (error) {
      console.error('Like error:', error.response?.data);
      if (error.response?.data?.detail === 'Recipe already liked') {
        // Если рецепт уже лайкнут, просто обновляем состояние
        setIsLiked(true);
        
        // Обновляем localStorage
        const likedRecipes = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
        if (!likedRecipes.includes(parseInt(id))) {
          likedRecipes.push(parseInt(id));
          localStorage.setItem('likedRecipes', JSON.stringify(likedRecipes));
        }
        
        toast.success('Рецепт уже в избранном');
      } else if (error.response?.data?.detail === 'Recipe not liked') {
        // Если рецепт не лайкнут, просто обновляем состояние
        setIsLiked(false);
        
        // Обновляем localStorage
        const likedRecipes = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
        const updatedLikedRecipes = likedRecipes.filter(recipeId => recipeId !== parseInt(id));
        localStorage.setItem('likedRecipes', JSON.stringify(updatedLikedRecipes));
        
        toast.success('Рецепт убран из избранного');
      } else {
        toast.error('Ошибка при постановке лайка');
      }
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    try {
      const response = await api.post(`/recipes/${id}/comments`, {
        content: commentText
      });
      setComments(prev => [...prev, response.data]);
      setCommentText('');
      toast.success('Комментарий добавлен');
    } catch (error) {
      toast.error('Ошибка при добавлении комментария');
    }
  };

  const handleDeleteComment = async (commentId) => {
    try {
      await api.delete(`/comments/${commentId}`);
      setComments(prev => prev.filter(comment => comment.id !== commentId));
      toast.success('Комментарий удален');
    } catch (error) {
      toast.error('Ошибка при удалении комментария');
    }
  };

  const formatTime = (minutes) => {
    if (minutes < 60) {
      return `${minutes} мин`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}ч ${mins}мин` : `${hours}ч`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400 text-lg">
          Рецепт не найден
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
              {/* Recipe Header */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                {recipe.image_url ? (
                  <div className="aspect-w-16 aspect-h-9">
                    <img
                      src={recipe.image_url.startsWith('http') ? recipe.image_url : `http://localhost:8000${recipe.image_url}`}
                      alt={recipe.title}
                      className="w-full h-64 md:h-96 object-cover"
                    />
                  </div>
                ) : (
                  <div className="w-full h-64 md:h-96 bg-gradient-to-br from-orange-400 to-red-500 flex flex-col items-center justify-center">
                    <div className="text-white text-center px-8">
                      <div className="text-6xl mb-4">
                        {recipe.title.toLowerCase().includes('борщ') ? '🍲' : 
                         recipe.title.toLowerCase().includes('торт') ? '🍰' : 
                         recipe.title.toLowerCase().includes('омлет') ? '🍳' : '🍽️'}
                      </div>
                      <div className="text-3xl font-bold mb-2">
                        {recipe.title}
                      </div>
                      <div className="text-lg opacity-90">
                        Вкусный рецепт
                      </div>
                    </div>
                  </div>
                )}
        
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {recipe.title}
              </h1>
              <p className="text-gray-600 dark:text-gray-300">
                Автор: {recipe.author.username}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {/* Кнопка редактирования для автора */}
              {user && (user.id === recipe.author_id || user.is_admin) && (
                <button
                  onClick={() => navigate(`/edit-recipe/${id}`)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
                >
                  <Edit className="h-5 w-5" />
                  <span>Редактировать</span>
                </button>
              )}
              <button
                onClick={handleLike}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                  isLiked
                    ? 'bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-400'
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                <Heart className={`h-5 w-5 ${isLiked ? 'fill-current' : ''}`} />
                <span>{likesCount}</span>
              </button>
            </div>
          </div>

          {recipe.description && (
            <p className="text-gray-700 dark:text-gray-300 mb-6">
              {recipe.description}
            </p>
          )}

          {/* Meta info */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {recipe.prep_time && (
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
                <Clock className="h-5 w-5" />
                <span>Подготовка: {formatTime(recipe.prep_time)}</span>
              </div>
            )}
            {recipe.cook_time && (
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
                <Clock className="h-5 w-5" />
                <span>Готовка: {formatTime(recipe.cook_time)}</span>
              </div>
            )}
            {recipe.servings && (
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
                <Users className="h-5 w-5" />
                <span>{recipe.servings} порций</span>
              </div>
            )}
            {recipe.difficulty && (
              <div className="flex items-center space-x-2">
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
              </div>
            )}
          </div>

          {/* Categories */}
          {recipe.categories && recipe.categories.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {recipe.categories.map((category) => (
                <span
                  key={category.id}
                  className="px-3 py-1 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 text-sm rounded-full"
                >
                  {category.name}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Ingredients */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Ингредиенты
        </h2>
        <ul className="space-y-2">
          {recipe.ingredients && Array.isArray(recipe.ingredients) && recipe.ingredients.map((ingredient, index) => (
            <li key={index} className="flex items-start space-x-3">
              <span className="text-primary-600 dark:text-primary-400 mt-1">•</span>
              <span className="text-gray-700 dark:text-gray-300">{ingredient}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Steps */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Способ приготовления
        </h2>
        <ol className="space-y-4">
          {recipe.steps && Array.isArray(recipe.steps) && recipe.steps.map((step, index) => (
            <li key={index} className="flex items-start space-x-3">
              <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                {index + 1}
              </span>
              <span className="text-gray-700 dark:text-gray-300">{step}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Comments */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Комментарии ({comments.length})
        </h2>

        {/* Add comment form */}
        {isAuthenticated ? (
          <form onSubmit={handleCommentSubmit} className="mb-6">
            <div className="flex space-x-2">
              <textarea
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Напишите комментарий..."
                className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                rows="3"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors duration-200"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </form>
        ) : (
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            <a href="/login" className="text-primary-600 dark:text-primary-400 hover:underline">
              Войдите в аккаунт
            </a>, чтобы оставить комментарий
          </p>
        )}

        {/* Comments list */}
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="border-l-4 border-primary-200 dark:border-primary-800 pl-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <User className="h-4 w-4 text-gray-400" />
                    <span className="font-medium text-gray-900 dark:text-white">
                      {comment.author.username}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(comment.created_at).toLocaleDateString('ru-RU')}
                    </span>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">
                    {comment.content}
                  </p>
                </div>
                {isAuthenticated && user.id === comment.author_id && (
                  <button
                    onClick={() => handleDeleteComment(comment.id)}
                    className="ml-2 p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {comments.length === 0 && (
          <p className="text-gray-500 dark:text-gray-400 text-center py-8">
            Пока нет комментариев. Будьте первым!
          </p>
        )}
      </div>
    </div>
  );
};

export default RecipeDetailPage;
