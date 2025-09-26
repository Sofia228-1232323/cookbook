import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from '../HomePage';
import { ThemeProvider } from '../../context/ThemeContext';

// Mock all dependencies
jest.mock('axios');
jest.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
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

const MockedHomePage = () => (
  <BrowserRouter>
    <ThemeProvider>
      <HomePage />
    </ThemeProvider>
  </BrowserRouter>
);

describe('HomePage Component', () => {
  test('renders homepage', () => {
    render(<MockedHomePage />);
    
    expect(screen.getByText(/cookbook/i)).toBeInTheDocument();
  });
});