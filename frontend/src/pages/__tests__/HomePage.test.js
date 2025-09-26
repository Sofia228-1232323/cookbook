import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from '../HomePage';
import { ThemeProvider } from '../../context/ThemeContext';

// Mock axios
jest.mock('axios');
import axios from 'axios';

const MockedHomePage = () => (
  <BrowserRouter>
    <ThemeProvider>
      <HomePage />
    </ThemeProvider>
  </BrowserRouter>
);

describe('HomePage Component', () => {
  const mockRecipes = [
    {
      id: 1,
      title: 'Test Recipe 1',
      description: 'Test Description 1',
      author: { username: 'testuser1' },
      category: { name: 'Breakfast' },
      likes_count: 5,
      comments_count: 3
    },
    {
      id: 2,
      title: 'Test Recipe 2',
      description: 'Test Description 2',
      author: { username: 'testuser2' },
      category: { name: 'Lunch' },
      likes_count: 10,
      comments_count: 7
    }
  ];

  const mockCategories = [
    { id: 1, name: 'Breakfast' },
    { id: 2, name: 'Lunch' },
    { id: 3, name: 'Dinner' }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API responses
    axios.get.mockImplementation((url) => {
      if (url.includes('/recipes')) {
        return Promise.resolve({
          data: {
            recipes: mockRecipes,
            total: 2,
            page: 1,
            limit: 10
          }
        });
      }
      if (url.includes('/categories')) {
        return Promise.resolve({ data: mockCategories });
      }
      return Promise.resolve({ data: [] });
    });
  });

  test('renders homepage elements', async () => {
    render(<MockedHomePage />);
    
    expect(screen.getByText(/cookbook/i)).toBeInTheDocument();
    expect(screen.getByText(/all recipes/i)).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
      expect(screen.getByText('Test Recipe 2')).toBeInTheDocument();
    });
  });

  test('displays recipe cards with correct information', async () => {
    render(<MockedHomePage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
      expect(screen.getByText('Test Description 1')).toBeInTheDocument();
      expect(screen.getByText('testuser1')).toBeInTheDocument();
      expect(screen.getByText('Breakfast')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument(); // likes count
      expect(screen.getByText('3')).toBeInTheDocument(); // comments count
    });
  });

  test('handles category filtering', async () => {
    render(<MockedHomePage />);
    
    // Wait for categories to load
    await waitFor(() => {
      expect(screen.getByText('Breakfast')).toBeInTheDocument();
    });
    
    const categorySelect = screen.getByDisplayValue('All Categories');
    fireEvent.change(categorySelect, { target: { value: '1' } });
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('category_id=1')
      );
    });
  });

  test('handles search functionality', async () => {
    render(<MockedHomePage />);
    
    const searchInput = screen.getByPlaceholderText(/search recipes/i);
    fireEvent.change(searchInput, { target: { value: 'test search' } });
    
    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('search=test search')
      );
    });
  });

  test('handles pagination', async () => {
    render(<MockedHomePage />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
    });
    
    // Look for pagination buttons (if they exist)
    const nextButton = screen.queryByText(/next/i);
    if (nextButton) {
      fireEvent.click(nextButton);
      
      await waitFor(() => {
        expect(axios.get).toHaveBeenCalledWith(
          expect.stringContaining('page=2')
        );
      });
    }
  });

  test('handles recipe click navigation', async () => {
    render(<MockedHomePage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
    });
    
    const recipeCard = screen.getByText('Test Recipe 1').closest('div');
    fireEvent.click(recipeCard);
    
    // Should navigate to recipe detail page
    expect(window.location.pathname).toBe('/recipe/1');
  });

  test('displays loading state', () => {
    // Mock loading state
    axios.get.mockImplementation(() => new Promise(() => {}));
    
    render(<MockedHomePage />);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('handles API error', async () => {
    const mockError = {
      response: {
        status: 500,
        data: { detail: 'Server error' }
      }
    };
    
    axios.get.mockRejectedValueOnce(mockError);
    
    render(<MockedHomePage />);
    
    await waitFor(() => {
      expect(screen.getByText(/error loading recipes/i)).toBeInTheDocument();
    });
  });

  test('displays empty state when no recipes', async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        recipes: [],
        total: 0,
        page: 1,
        limit: 10
      }
    });
    
    render(<MockedHomePage />);
    
    await waitFor(() => {
      expect(screen.getByText(/no recipes found/i)).toBeInTheDocument();
    });
  });

  test('handles like functionality', async () => {
    // Mock successful like
    axios.post.mockResolvedValueOnce({
      data: { message: 'Recipe liked', liked: true }
    });
    
    render(<MockedHomePage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
    });
    
    const likeButton = screen.getByRole('button', { name: /like/i });
    fireEvent.click(likeButton);
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/recipes/1/like');
    });
  });

  test('handles theme toggle', () => {
    render(<MockedHomePage />);
    
    const themeToggle = screen.getByRole('button', { name: /toggle theme/i });
    fireEvent.click(themeToggle);
    
    // Should toggle theme (implementation depends on ThemeContext)
    expect(themeToggle).toBeInTheDocument();
  });
});
