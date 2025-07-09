// Authentication Service for AegisAI

import { API_BASE_URL, API_ENDPOINTS } from '../config/api';

export interface User {
  username: string;
  role: string;
  permissions: string[];
}

export interface LoginCredentials {
  username?: string;
  password?: string;
  role?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

class AuthService {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage on initialization
    this.token = localStorage.getItem('auth_token');
  }

  async authenticateUser(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      // For demo mode, use role-based authentication
      if (credentials.role) {
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.DEMO_LOGIN}?role=${credentials.role}`);
        
        if (!response.ok) {
          throw new Error('Authentication failed');
        }
        
        const data = await response.json();
        
        // Store token
        this.token = data.token;
        localStorage.setItem('auth_token', data.token);
        
        return data;
      }
      
      // For production mode with username/password
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: credentials.username,
          password: credentials.password,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Invalid credentials');
      }
      
      const data = await response.json();
      
      // Store token
      this.token = data.token;
      localStorage.setItem('auth_token', data.token);
      
      return data;
      
    } catch (error) {
      console.error('Authentication error:', error);
      throw error;
    }
  }

  logout(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  getToken(): string | null {
    return this.token;
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }
}

// Export singleton instance
export const authService = new AuthService();

// Convenience functions
export const authenticateUser = (credentials: LoginCredentials) => 
  authService.authenticateUser(credentials);

export const logout = () => authService.logout();

export const getAuthHeaders = () => authService.getAuthHeaders();

export const isAuthenticated = () => authService.isAuthenticated();