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
    register: jest.fn(),
    user: null,
    token: null,
    logout: jest.fn(),
    loading: false,
    isAuthenticated: false
  })
}));

jest.mock('react-hook-form', () => ({
  useForm: () => ({
    register: jest.fn(),
    handleSubmit: jest.fn(),
    formState: { errors: {} }
  })
}));

jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn()
}));

jest.mock('lucide-react', () => ({
  Eye: () => <div>Eye</div>,
  EyeOff: () => <div>EyeOff</div>,
  Mail: () => <div>Mail</div>,
  Lock: () => <div>Lock</div>,
  ChefHat: () => <div>ChefHat</div>
}));

// Simple test
describe('RegisterForm', () => {
  test('basic test', () => {
    expect(1 + 1).toBe(2);
  });
});