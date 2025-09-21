import React, { useState, useEffect } from 'react';
import api from '../config/api';
import RecipeCard from '../components/RecipeCard';
import { Search, Filter, Loader } from 'lucide-react';

const HomePage = () => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categories, setCategories] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  console.log('HomePage component rendered');

  // Тест подключения к API
  useEffect(() => {
    const testConnection = async () => {
      try {
        console.log('🧪 Testing API connection...');
        console.log('🌐 API Base URL:', api.defaults.baseURL);
        
        // Тест 1: Прямой fetch через proxy
        try {
          const fetchResponse = await fetch('/health');
          const fetchData = await fetchResponse.json();
          console.log('✅ Direct fetch test successful:', fetchData);
        } catch (fetchError) {
          console.error('❌ Direct fetch test failed:', fetchError);
        }
        
        // Тест 2: Через axios
        try {
          const response = await api.get('/health');
          console.log('✅ Axios test successful:', response.data);
        } catch (axiosError) {
          console.error('❌ Axios test failed:', axiosError);
        }
      } catch (error) {
        console.error('❌ API connection test failed:', error);
      }
    };
    
    testConnection();
  }, []);

  // Load categories from API
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await api.get('/categories');
        setCategories(response.data);
      } catch (error) {
        console.error('Error fetching categories:', error);
        // Fallback to hardcoded categories if API fails
        setCategories([
          { id: 1, name: 'Завтрак' },
          { id: 2, name: 'Обед' },
          { id: 3, name: 'Ужин' },
          { id: 4, name: 'Десерты' },
          { id: 5, name: 'Напитки' },
          { id: 6, name: 'Закуски' },
          { id: 7, name: 'Супы' },
          { id: 8, name: 'Салаты' },
        ]);
      }
    };
    fetchCategories();
  }, []);

  // Load recipes
  useEffect(() => {
    const fetchRecipes = async () => {
      try {
        setLoading(true);
        console.log('Fetching recipes from API...');
        console.log('Current page:', page, 'searchTerm:', searchTerm, 'selectedCategory:', selectedCategory);
        
        const params = new URLSearchParams({
          page: page.toString(),
          limit: '10'
        });
        
        if (searchTerm) params.append('search', searchTerm);
        if (selectedCategory) params.append('category_id', selectedCategory);
        
        const url = `/recipes?${params}`;
        console.log('Requesting URL:', url);
        
        const response = await api.get(url);
        console.log('API Response:', response.data);
        console.log('Response data type:', typeof response.data);
        console.log('Response data is array:', Array.isArray(response.data));
        
        // API возвращает массив напрямую, а не объект с полем recipes
        const recipesData = Array.isArray(response.data) ? response.data : (response.data.recipes || []);
        console.log('Processed recipes data:', recipesData);
        console.log('Recipes count:', recipesData.length);
        
        if (page === 1) {
          setRecipes(recipesData);
          console.log('Set recipes for page 1:', recipesData);
        } else {
          setRecipes(prev => {
            const newRecipes = [...prev, ...recipesData];
            console.log('Added recipes to existing:', newRecipes);
            return newRecipes;
          });
        }
        
        setHasMore(response.data.has_more || false);
        console.log('Has more:', response.data.has_more || false);
      } catch (error) {
        console.error('Error fetching recipes:', error);
        // Fallback to empty array if API fails
        setRecipes([]);
        setHasMore(false);
      } finally {
        setLoading(false);
      }
    };

    fetchRecipes();
  }, [page, searchTerm, selectedCategory]);

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setPage(1);
  };

  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
    setPage(1);
  };

  const loadMore = () => {
    setPage(prev => prev + 1);
  };

  console.log('HomePage render - recipes:', recipes, 'loading:', loading);

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Добро пожаловать в Cookbook
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          Откройте для себя вкусные рецепты от талантливых поваров
        </p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Поиск рецептов..."
                value={searchTerm}
                onChange={handleSearch}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          {/* Category Filter */}
          <div className="md:w-64">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Filter className="h-5 w-5 text-gray-400" />
              </div>
              <select
                value={selectedCategory}
                onChange={handleCategoryChange}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Все категории</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      {loading && page === 1 ? (
        <div className="flex justify-center items-center py-12">
          <Loader className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : recipes.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 text-lg">
            Рецепты не найдены
          </p>
        </div>
      ) : (
        <>
          {/* Recipes Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recipes.map(recipe => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>

          {/* Load More Button */}
          {hasMore && (
            <div className="text-center">
              <button
                onClick={loadMore}
                disabled={loading}
                className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                {loading ? 'Загрузка...' : 'Загрузить еще'}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default HomePage;
