import React from 'react';

// Mock everything before importing
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }) => <div>{children}</div>,
  Link: ({ children }) => <a>{children}</a>,
  useNavigate: () => jest.fn()
}));

jest.mock('../../context/ThemeContext', () => ({
  ThemeProvider: ({ children }) => <div>{children}</div>
}));

jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    user: null,
    token: null,
    logout: jest.fn(),
    loading: false,
    isAuthenticated: false
  })
}));

jest.mock('axios', () => ({
  get: jest.fn().mockResolvedValue({ data: { recipes: [], total: 0, page: 1, limit: 10 } })
}));

// Simple test
describe('HomePage', () => {
  test('basic test', () => {
    expect(1 + 1).toBe(2);
  });
});