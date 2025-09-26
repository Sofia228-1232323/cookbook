import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RegisterForm from '../RegisterForm';
import { ThemeProvider } from '../../context/ThemeContext';

// Mock all dependencies
jest.mock('axios');
jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    register: jest.fn().mockResolvedValue({ success: true }),
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

const MockedRegisterForm = () => (
  <BrowserRouter>
    <ThemeProvider>
      <RegisterForm />
    </ThemeProvider>
  </BrowserRouter>
);

describe('RegisterForm Component', () => {
  test('renders register form', () => {
    render(<MockedRegisterForm />);
    
    expect(screen.getByText(/регистрация/i)).toBeInTheDocument();
  });
});