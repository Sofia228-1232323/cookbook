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
    register: jest.fn().mockResolvedValue({ success: true }),
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

// Import after mocks
import RegisterForm from '../RegisterForm';

describe('RegisterForm Component', () => {
  test('renders without crashing', () => {
    render(<RegisterForm />);
    // If we get here without throwing, the test passes
    expect(true).toBe(true);
  });
});