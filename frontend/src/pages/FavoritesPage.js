import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../config/api';
import RecipeCard from '../components/RecipeCard';
import { Heart, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

const FavoritesPage = () => {
  const { user, isAuthenticated } = useAuth();
  const [favoriteRecipes, setFavoriteRecipes] = useState([]);
  const [loading, setLoading] = useState(true);

  console.log('FavoritesPage component rendered, user:', user);

  useEffect(() => {
    const fetchFavoriteRecipes = async () => {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        console.log('❤️ Fetching favorite recipes for user:', user.id);
        
        // Получаем все рецепты и фильтруем по лайкам
        console.log('🌐 Making API request to /recipes');
        const response = await api.get('/recipes');
        console.log('✅ All recipes API response:', response.data);
        
        // API возвращает массив напрямую
        const allRecipes = Array.isArray(response.data) ? response.data : [];
        console.log('📋 All recipes:', allRecipes);
        
        // Получаем избранные рецепты из localStorage
        const likedRecipes = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
        const favorites = allRecipes.filter(recipe => likedRecipes.includes(recipe.id));
        console.log('❤️ Favorite recipes:', favorites);
        console.log('📊 Favorite recipes count:', favorites.length);
        
        setFavoriteRecipes(favorites);
      } catch (error) {
        console.error('❌ Error fetching favorite recipes:', error);
        console.error('❌ Error details:', error.response?.data || error.message);
        setFavoriteRecipes([]);
        toast.error('Ошибка загрузки избранных рецептов');
      } finally {
        setLoading(false);
      }
    };

    fetchFavoriteRecipes();
  }, [isAuthenticated, user]);

  const handleRemoveFromFavorites = async (recipeId) => {
    try {
      await api.delete(`/recipes/${recipeId}/like`);
      
      // Обновляем localStorage
      const likedRecipes = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
      const updatedLikedRecipes = likedRecipes.filter(id => id !== recipeId);
      localStorage.setItem('likedRecipes', JSON.stringify(updatedLikedRecipes));
      
      setFavoriteRecipes(prev => prev.filter(recipe => recipe.id !== recipeId));
      toast.success('Рецепт убран из избранного');
    } catch (error) {
      console.error('Error removing from favorites:', error);
      toast.error('Ошибка при удалении из избранного');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <Heart className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-gray-500 dark:text-gray-400 text-lg">
          Войдите в систему, чтобы просматривать избранные рецепты
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <Heart className="mx-auto h-12 w-12 text-red-500 mb-4" />
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Избранные рецепты
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          Рецепты, которые вам понравились
        </p>
      </div>

      {/* Results */}
      {favoriteRecipes.length === 0 ? (
        <div className="text-center py-12">
          <Heart className="mx-auto h-16 w-16 text-gray-300 mb-4" />
          <p className="text-gray-500 dark:text-gray-400 text-lg">
            У вас пока нет избранных рецептов
          </p>
          <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">
            Ставьте лайки рецептам, чтобы они появились здесь
          </p>
        </div>
      ) : (
        <>
          {/* Recipes Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {favoriteRecipes.map(recipe => (
              <div key={recipe.id} className="relative">
                <RecipeCard recipe={recipe} />
                <button
                  onClick={() => handleRemoveFromFavorites(recipe.id)}
                  className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors duration-200"
                  title="Убрать из избранного"
                >
                  <Heart className="h-4 w-4 fill-current" />
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default FavoritesPage;
