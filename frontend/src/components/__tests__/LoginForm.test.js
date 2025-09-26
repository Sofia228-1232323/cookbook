import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginForm from '../LoginForm';
import { ThemeProvider } from '../../context/ThemeContext';

// Mock all dependencies
jest.mock('axios');
jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    login: jest.fn().mockResolvedValue({ success: true }),
    user: null,
    token: null,
    logout: jest.fn(),
    loading: false,
    isAuthenticated: false
  })
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn()
}));

const MockedLoginForm = () => (
  <BrowserRouter>
    <ThemeProvider>
      <LoginForm />
    </ThemeProvider>
  </BrowserRouter>
);

describe('LoginForm Component', () => {
  test('renders login form', () => {
    render(<MockedLoginForm />);
    
    expect(screen.getByText(/вход в аккаунт/i)).toBeInTheDocument();
  });
});