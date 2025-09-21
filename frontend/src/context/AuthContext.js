import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../config/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // Verify token and get user info
      api.get('/auth/me')
        .then(response => {
          setUser(response.data);
        })
        .catch(error => {
          console.error('Token verification failed:', error);
          logout();
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    try {
      console.log('🔐 Attempting login for:', email);
      
      // Проверим, доступен ли API
      try {
        const healthResponse = await api.get('/health');
        console.log('✅ API is accessible:', healthResponse.data);
      } catch (apiError) {
        console.error('❌ API is not accessible:', apiError);
        console.error('❌ API Error details:', apiError.response?.data || apiError.message);
        return { 
          success: false, 
          error: 'Не удается подключиться к серверу. Проверьте, что backend запущен.' 
        };
      }
      
      const response = await api.post('/auth/login', { email, password });
      console.log('✅ Login response received:', response.data);
      const { access_token } = response.data;
      
      setToken(access_token);
      localStorage.setItem('token', access_token);
      
      // Get user info
      console.log('👤 Getting user info...');
      const userResponse = await api.get('/auth/me');
      console.log('✅ User info received:', userResponse.data);
      setUser(userResponse.data);
      
      return { success: true };
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('❌ Error response:', error.response?.data);
      console.error('❌ Error message:', error.message);
      console.error('❌ Error stack:', error.stack);
      
      let errorMessage = 'Ошибка входа';
      if (error.code === 'ECONNREFUSED') {
        errorMessage = 'Не удается подключиться к серверу. Проверьте, что backend запущен.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const register = async (email, username, password) => {
    try {
      await api.post('/auth/register', { 
        email, 
        username, 
        password 
      });
      
      // Auto login after registration
      return await login(email, password);
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Ошибка регистрации' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
