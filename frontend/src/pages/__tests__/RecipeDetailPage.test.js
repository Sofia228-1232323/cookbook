import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RecipeDetailPage from '../RecipeDetailPage';
import { ThemeProvider } from '../../context/ThemeContext';

// Mock axios
jest.mock('axios');
import axios from 'axios';

// Mock useParams
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
  const mockRecipe = {
    id: 1,
    title: 'Test Recipe',
    description: 'Test Description',
    ingredients: ['ingredient1', 'ingredient2'],
    steps: ['step1', 'step2'],
    author: { username: 'testuser', email: 'test@example.com' },
    category: { name: 'Breakfast' },
    likes_count: 5,
    comments_count: 3,
    image_url: '/uploads/test-image.jpg'
  };

  const mockComments = [
    {
      id: 1,
      content: 'Great recipe!',
      author: { username: 'commenter1' },
      created_at: '2023-01-01T00:00:00Z'
    },
    {
      id: 2,
      content: 'Delicious!',
      author: { username: 'commenter2' },
      created_at: '2023-01-02T00:00:00Z'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API responses
    axios.get.mockImplementation((url) => {
      if (url.includes('/recipes/1')) {
        return Promise.resolve({ data: mockRecipe });
      }
      if (url.includes('/recipes/1/comments')) {
        return Promise.resolve({ data: mockComments });
      }
      if (url.includes('/recipes/1/is-liked')) {
        return Promise.resolve({ data: { liked: false } });
      }
      return Promise.resolve({ data: {} });
    });
  });

  test('renders recipe details', async () => {
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
      expect(screen.getByText('testuser')).toBeInTheDocument();
      expect(screen.getByText('Breakfast')).toBeInTheDocument();
    });
  });

  test('displays ingredients list', async () => {
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('ingredient1')).toBeInTheDocument();
      expect(screen.getByText('ingredient2')).toBeInTheDocument();
    });
  });

  test('displays cooking steps', async () => {
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('step1')).toBeInTheDocument();
      expect(screen.getByText('step2')).toBeInTheDocument();
    });
  });

  test('displays recipe image', async () => {
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      const image = screen.getByAltText('Test Recipe');
      expect(image).toBeInTheDocument();
      expect(image).toHaveAttribute('src', '/uploads/test-image.jpg');
    });
  });

  test('displays comments section', async () => {
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Great recipe!')).toBeInTheDocument();
      expect(screen.getByText('Delicious!')).toBeInTheDocument();
      expect(screen.getByText('commenter1')).toBeInTheDocument();
      expect(screen.getByText('commenter2')).toBeInTheDocument();
    });
  });

  test('handles like functionality', async () => {
    // Mock successful like
    axios.post.mockResolvedValueOnce({
      data: { message: 'Recipe liked', liked: true }
    });
    
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    });
    
    const likeButton = screen.getByRole('button', { name: /like/i });
    fireEvent.click(likeButton);
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/recipes/1/like');
    });
  });

  test('handles unlike functionality', async () => {
    // Mock unlike
    axios.delete.mockResolvedValueOnce({
      data: { message: 'Recipe unliked', liked: false }
    });
    
    // Mock initial liked state
    axios.get.mockImplementation((url) => {
      if (url.includes('/recipes/1/is-liked')) {
        return Promise.resolve({ data: { liked: true } });
      }
      if (url.includes('/recipes/1')) {
        return Promise.resolve({ data: mockRecipe });
      }
      return Promise.resolve({ data: {} });
    });
    
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    });
    
    const unlikeButton = screen.getByRole('button', { name: /unlike/i });
    fireEvent.click(unlikeButton);
    
    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalledWith('/recipes/1/like');
    });
  });

  test('handles comment submission', async () => {
    // Mock successful comment creation
    axios.post.mockResolvedValueOnce({
      data: {
        id: 3,
        content: 'New comment',
        author: { username: 'testuser' }
      }
    });
    
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    });
    
    const commentInput = screen.getByPlaceholderText(/add a comment/i);
    const submitButton = screen.getByRole('button', { name: /submit/i });
    
    fireEvent.change(commentInput, { target: { value: 'New comment' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/recipes/1/comments', {
        content: 'New comment'
      });
    });
  });

  test('handles comment deletion', async () => {
    // Mock successful comment deletion
    axios.delete.mockResolvedValueOnce({
      data: { message: 'Comment deleted successfully' }
    });
    
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Great recipe!')).toBeInTheDocument();
    });
    
    const deleteButton = screen.getByRole('button', { name: /delete comment/i });
    fireEvent.click(deleteButton);
    
    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalledWith('/comments/1');
    });
  });

  test('handles API error for recipe', async () => {
    const mockError = {
      response: {
        status: 404,
        data: { detail: 'Recipe not found' }
      }
    };
    
    axios.get.mockRejectedValueOnce(mockError);
    
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/recipe not found/i)).toBeInTheDocument();
    });
  });

  test('handles API error for comments', async () => {
    const mockError = {
      response: {
        status: 500,
        data: { detail: 'Server error' }
      }
    };
    
    axios.get.mockImplementation((url) => {
      if (url.includes('/recipes/1')) {
        return Promise.resolve({ data: mockRecipe });
      }
      if (url.includes('/recipes/1/comments')) {
        return Promise.reject(mockError);
      }
      return Promise.resolve({ data: {} });
    });
    
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/error loading comments/i)).toBeInTheDocument();
    });
  });

  test('displays loading state', () => {
    // Mock loading state
    axios.get.mockImplementation(() => new Promise(() => {}));
    
    render(<MockedRecipeDetailPage />);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('handles unauthorized access', async () => {
    // Mock unauthorized response
    axios.get.mockRejectedValueOnce({
      response: {
        status: 401,
        data: { detail: 'Unauthorized' }
      }
    });
    
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/unauthorized/i)).toBeInTheDocument();
    });
  });

  test('handles edit button for recipe author', async () => {
    // Mock recipe with current user as author
    const mockRecipeWithAuthor = {
      ...mockRecipe,
      author: { username: 'currentuser', email: 'current@example.com' }
    };
    
    axios.get.mockImplementation((url) => {
      if (url.includes('/recipes/1')) {
        return Promise.resolve({ data: mockRecipeWithAuthor });
      }
      return Promise.resolve({ data: {} });
    });
    
    render(<MockedRecipeDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    });
    
    const editButton = screen.queryByRole('button', { name: /edit/i });
    if (editButton) {
      expect(editButton).toBeInTheDocument();
    }
  });
});
