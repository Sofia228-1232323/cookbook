import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../config/api';
import toast from 'react-hot-toast';
import { Plus, Minus, Save, ArrowLeft, Loader } from 'lucide-react';

const EditRecipePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Форма
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    ingredients: [''],
    steps: [''],
    category_id: 1
  });
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  console.log('EditRecipePage rendered for recipe ID:', id);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchRecipe = async () => {
      try {
        setLoading(true);
        console.log('Fetching recipe for editing:', id);
        
        const response = await api.get(`/recipes/${id}`);
        console.log('Recipe data:', response.data);
        
        const recipeData = response.data;
        
        // Проверяем, что пользователь является автором рецепта
        if (recipeData.author_id !== user.id && !user.is_admin) {
          toast.error('Вы можете редактировать только свои рецепты');
          navigate('/profile');
          return;
        }
        
        setRecipe(recipeData);
        
        // Заполняем форму данными рецепта
        setFormData({
          title: recipeData.title || '',
          description: recipeData.description || '',
          ingredients: Array.isArray(recipeData.ingredients) && recipeData.ingredients.length > 0 
            ? recipeData.ingredients 
            : [''],
          steps: Array.isArray(recipeData.steps) && recipeData.steps.length > 0 
            ? recipeData.steps 
            : [''],
          category_id: recipeData.category_id || 1
        });
        
        // Устанавливаем превью изображения, если есть
        if (recipeData.image_url) {
          setImagePreview(recipeData.image_url.startsWith('http') 
            ? recipeData.image_url 
            : `http://localhost:8000${recipeData.image_url}`);
        }
        
      } catch (error) {
        console.error('Error fetching recipe:', error);
        toast.error('Ошибка загрузки рецепта');
        navigate('/profile');
      } finally {
        setLoading(false);
      }
    };

    fetchRecipe();
  }, [id, user, isAuthenticated, navigate]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleIngredientChange = (index, value) => {
    const newIngredients = [...formData.ingredients];
    newIngredients[index] = value;
    setFormData(prev => ({
      ...prev,
      ingredients: newIngredients
    }));
  };

  const handleStepChange = (index, value) => {
    const newSteps = [...formData.steps];
    newSteps[index] = value;
    setFormData(prev => ({
      ...prev,
      steps: newSteps
    }));
  };

  const handleAddIngredient = () => {
    setFormData(prev => ({
      ...prev,
      ingredients: [...prev.ingredients, '']
    }));
  };

  const handleRemoveIngredient = (index) => {
    if (formData.ingredients.length > 1) {
      const newIngredients = formData.ingredients.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        ingredients: newIngredients
      }));
    }
  };

  const handleAddStep = () => {
    setFormData(prev => ({
      ...prev,
      steps: [...prev.steps, '']
    }));
  };

  const handleRemoveStep = (index) => {
    if (formData.steps.length > 1) {
      const newSteps = formData.steps.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        steps: newSteps
      }));
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.description.trim()) {
      toast.error('Заполните все обязательные поля');
      return;
    }

    const nonEmptyIngredients = formData.ingredients.filter(ing => ing.trim() !== '');
    const nonEmptySteps = formData.steps.filter(step => step.trim() !== '');
    
    if (nonEmptyIngredients.length === 0 || nonEmptySteps.length === 0) {
      toast.error('Добавьте хотя бы один ингредиент и один шаг приготовления');
      return;
    }

    try {
      setSaving(true);
      
      const formDataToSend = new FormData();
      formDataToSend.append('title', formData.title);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('ingredients', JSON.stringify(nonEmptyIngredients));
      formDataToSend.append('steps', JSON.stringify(nonEmptySteps));
      formDataToSend.append('category_id', formData.category_id);
      
      if (image) {
        formDataToSend.append('image', image);
      }

      console.log('Updating recipe:', id);
      const response = await api.put(`/recipes/${id}`, formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Recipe updated successfully:', response.data);
      toast.success('Рецепт успешно обновлен!');
      navigate(`/app/recipe/${id}`);
      
    } catch (error) {
      console.error('Error updating recipe:', error);
      toast.error('Ошибка при обновлении рецепта');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader className="animate-spin text-primary-600" size={48} />
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
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => navigate(`/app/recipe/${id}`)}
          className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
        >
          <ArrowLeft size={20} />
          <span>Назад к рецепту</span>
        </button>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Редактировать рецепт
        </h1>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 space-y-6">
        
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Название рецепта *
          </label>
          <input
            type="text"
            id="title"
            value={formData.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            placeholder="Введите название рецепта"
            required
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Описание *
          </label>
          <textarea
            id="description"
            rows="4"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            placeholder="Опишите ваш рецепт"
            required
          />
        </div>

        {/* Current Image Preview */}
        {imagePreview && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Текущее изображение
            </label>
            <img
              src={imagePreview}
              alt="Текущее изображение"
              className="w-full h-48 object-cover rounded-md"
            />
          </div>
        )}

        {/* New Image Upload */}
        <div>
          <label htmlFor="image" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Новое изображение (необязательно)
          </label>
          <input
            type="file"
            id="image"
            accept="image/*"
            onChange={handleImageChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
          />
        </div>

        {/* Ingredients */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Ингредиенты *
          </label>
          {formData.ingredients.map((ingredient, index) => (
            <div key={index} className="flex items-center space-x-2 mb-2">
              <input
                type="text"
                value={ingredient}
                onChange={(e) => handleIngredientChange(index, e.target.value)}
                className="flex-grow px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder={`Ингредиент ${index + 1}`}
              />
              <button
                type="button"
                onClick={() => handleRemoveIngredient(index)}
                disabled={formData.ingredients.length === 1}
                className="p-2 text-red-500 hover:text-red-700 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                <Minus size={20} />
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddIngredient}
            className="mt-2 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-200 flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>Добавить ингредиент</span>
          </button>
        </div>

        {/* Steps */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Шаги приготовления *
          </label>
          {formData.steps.map((step, index) => (
            <div key={index} className="flex items-start space-x-2 mb-2">
              <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium mt-1">
                {index + 1}
              </div>
              <textarea
                rows="2"
                value={step}
                onChange={(e) => handleStepChange(index, e.target.value)}
                className="flex-grow px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder={`Шаг ${index + 1}`}
              />
              <button
                type="button"
                onClick={() => handleRemoveStep(index)}
                disabled={formData.steps.length === 1}
                className="p-2 text-red-500 hover:text-red-700 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors mt-1"
              >
                <Minus size={20} />
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddStep}
            className="mt-2 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors duration-200 flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>Добавить шаг</span>
          </button>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate(`/app/recipe/${id}`)}
            className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {saving ? (
              <>
                <Loader className="animate-spin" size={20} />
                <span>Сохранение...</span>
              </>
            ) : (
              <>
                <Save size={20} />
                <span>Сохранить изменения</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditRecipePage;


