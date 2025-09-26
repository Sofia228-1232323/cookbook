import React from 'react';
import { render } from '@testing-library/react';

// Mock all dependencies
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }) => <div>{children}</div>,
  Link: ({ children, to }) => <a href={to}>{children}</a>,
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

// Import after mocks
import HomePage from '../HomePage';

describe('HomePage Component', () => {
  test('renders without crashing', () => {
    render(<HomePage />);
    // If we get here without throwing, the test passes
    expect(true).toBe(true);
  });
});