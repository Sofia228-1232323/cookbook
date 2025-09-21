import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../config/api';
import { Link, useNavigate } from 'react-router-dom';
import { User, Mail, Calendar, Plus, Edit, Trash2, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

const ProfilePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [userRecipes, setUserRecipes] = useState([]);
  const [loading, setLoading] = useState(true);

  console.log('ProfilePage component rendered, user:', user);

  useEffect(() => {
    const fetchUserRecipes = async () => {
      if (!user) return;
      
      try {
        setLoading(true);
        console.log('👤 Fetching user recipes for user:', user.id);
        
        // Получаем все рецепты и фильтруем по автору
        console.log('🌐 Making API request to /recipes');
        
        // Тест с fetch через proxy
        try {
          const fetchResponse = await fetch('/recipes');
          const fetchData = await fetchResponse.json();
          console.log('✅ Fetch test successful:', fetchData);
        } catch (fetchError) {
          console.error('❌ Fetch test failed:', fetchError);
        }
        
        const response = await api.get('/recipes');
        console.log('✅ All recipes API response:', response.data);
        console.log('📊 Response data type:', typeof response.data);
        console.log('📊 Response is array:', Array.isArray(response.data));
        
        // API возвращает массив напрямую, а не объект с полем recipes
        const allRecipes = Array.isArray(response.data) ? response.data : (response.data.recipes || []);
        console.log('📋 All recipes:', allRecipes);
        
        // Фильтруем рецепты по автору
        const userRecipes = allRecipes.filter(recipe => recipe.author_id === user.id);
        console.log('👤 Filtered user recipes:', userRecipes);
        console.log('📊 User recipes count:', userRecipes.length);
        
        setUserRecipes(userRecipes);
      } catch (error) {
        console.error('❌ Error fetching user recipes:', error);
        console.error('❌ Error details:', error.response?.data || error.message);
        // Fallback to empty array if API fails
        setUserRecipes([]);
        toast.error('Ошибка загрузки рецептов');
      } finally {
        setLoading(false);
      }
    };

    fetchUserRecipes();
  }, [user]);

  const handleDeleteRecipe = async (recipeId) => {
    if (!window.confirm('Вы уверены, что хотите удалить этот рецепт?')) {
      return;
    }

    try {
      await api.delete(`/recipes/${recipeId}`);
      setUserRecipes(prev => prev.filter(recipe => recipe.id !== recipeId));
      toast.success('Рецепт удален');
    } catch (error) {
      console.error('Error deleting recipe:', error);
      toast.error('Ошибка при удалении рецепта');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400 text-lg">
          Пользователь не найден
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* User Info */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-6">
          <div className="w-20 h-20 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
            <User className="h-10 w-10 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {user.username}
            </h1>
            <div className="flex items-center space-x-4 mt-2 text-gray-600 dark:text-gray-300">
              <div className="flex items-center space-x-1">
                <Mail className="h-4 w-4" />
                <span>{user.email}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="h-4 w-4" />
                <span>На сайте с {formatDate(user.created_at)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* User Recipes */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Мои рецепты ({userRecipes.length})
          </h2>
          <Link
            to="/add-recipe"
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
          >
            <Plus className="h-5 w-5" />
            <span>Добавить рецепт</span>
          </Link>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : userRecipes.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-4">
              У вас пока нет рецептов
            </p>
            <Link
              to="/add-recipe"
              className="inline-flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
            >
              <Plus className="h-5 w-5" />
              <span>Создать первый рецепт</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {userRecipes.map(recipe => (
              <div key={recipe.id} className="bg-gray-50 dark:bg-gray-700 rounded-lg overflow-hidden">
                {recipe.image_url && (
                  <div className="aspect-w-16 aspect-h-9">
                    <img
                      src={`http://localhost:8000${recipe.image_url}`}
                      alt={recipe.title}
                      className="w-full h-32 object-cover"
                    />
                  </div>
                )}
                
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                    {recipe.title}
                  </h3>
                  
                  {recipe.description && (
                    <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-2">
                      {recipe.description}
                    </p>
                  )}

                  <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-3">
                    <span>{formatDate(recipe.created_at)}</span>
                    <div className="flex items-center space-x-3">
                      <span>❤️ {recipe.likes_count || 0}</span>
                      <span>💬 {recipe.comments_count || 0}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/recipe/${recipe.id}`}
                      className="flex-1 text-center px-3 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors text-sm"
                    >
                      Просмотреть
                    </Link>
                    <Link
                      to={`/edit-recipe/${recipe.id}`}
                      className="p-2 text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                      title="Редактировать"
                    >
                      <Edit className="h-4 w-4" />
                    </Link>
                    <button
                      onClick={() => handleDeleteRecipe(recipe.id)}
                      className="p-2 text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                      title="Удалить"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;
