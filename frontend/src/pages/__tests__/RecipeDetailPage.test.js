import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RecipeDetailPage from '../RecipeDetailPage';
import { ThemeProvider } from '../../context/ThemeContext';

// Mock all dependencies
jest.mock('axios');
jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'testuser', email: 'test@example.com' },
    token: 'mock-token',
    logout: jest.fn(),
    loading: false,
    isAuthenticated: true
  })
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ id: '1' })
}));

const MockedRecipeDetailPage = () => (
  <BrowserRouter>
    <ThemeProvider>
      <RecipeDetailPage />
    </ThemeProvider>
  </BrowserRouter>
);

describe('RecipeDetailPage Component', () => {
  test('renders recipe detail page', () => {
    render(<MockedRecipeDetailPage />);
    
    expect(screen.getByText(/загрузка/i)).toBeInTheDocument();
  });
});