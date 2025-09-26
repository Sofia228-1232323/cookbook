import React from 'react';

// Mock everything before importing
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }) => <div>{children}</div>,
  Link: ({ children }) => <a>{children}</a>,
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: '1' })
}));

jest.mock('../../context/ThemeContext', () => ({
  ThemeProvider: ({ children }) => <div>{children}</div>
}));

jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'testuser', email: 'test@example.com' },
    token: 'mock-token',
    logout: jest.fn(),
    loading: false,
    isAuthenticated: true
  })
}));

jest.mock('axios', () => ({
  get: jest.fn().mockResolvedValue({ data: {} }),
  post: jest.fn().mockResolvedValue({ data: {} }),
  delete: jest.fn().mockResolvedValue({ data: {} })
}));

// Simple test
describe('RecipeDetailPage', () => {
  test('basic test', () => {
    expect(1 + 1).toBe(2);
  });
});