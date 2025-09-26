import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock all the dependencies
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }) => <div>{children}</div>,
  Routes: ({ children }) => <div>{children}</div>,
  Route: ({ element }) => <div>{element}</div>,
  Navigate: () => <div>Navigate</div>
}));

jest.mock('./context/ThemeContext', () => ({
  ThemeProvider: ({ children }) => <div>{children}</div>
}));

jest.mock('./context/AuthContext', () => ({
  AuthProvider: ({ children }) => <div>{children}</div>
}));

describe('App Component', () => {
  test('renders without crashing', () => {
    render(<App />);
    // Basic test to ensure the app renders
    expect(document.body).toBeInTheDocument();
  });
});
