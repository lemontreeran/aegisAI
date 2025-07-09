import React, { useState } from 'react';
import { Shield } from 'lucide-react';
import { authenticateUser } from '../services/auth';

interface User {
  username: string;
  role: string;
  permissions: string[];
}

interface LoginPageProps {
  onLogin: (user: User) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const demoUsers = {
    admin: { username: 'admin', role: 'Admin', permissions: ['read', 'write', 'admin'] },
    analyst: { username: 'analyst', role: 'Analyst', permissions: ['read', 'write'] },
    user: { username: 'user', role: 'User', permissions: ['read'] },
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Map username to role for demo authentication
    const userRole = demoUsers[username as keyof typeof demoUsers]?.role.toLowerCase() || 'user';
    
    // Use authentication service with role
    authenticateUser({ role: userRole })
      .then((authResponse) => {
        onLogin(authResponse.user);
      })
      .catch((error) => {
        setError(error.message || 'Authentication failed');
      });
  };

  const handleDemoAccess = async (role: string = 'admin') => {
    try {
      const authResponse = await authenticateUser({ role });
      onLogin(authResponse.user);
    } catch (error) {
      setError('Demo access failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Shield className="h-16 w-16 text-blue-400" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">AegisAI</h1>
          <p className="text-blue-200">Governance Platform</p>
          <p className="text-blue-300 text-sm mt-2">Secure AI Governance & Compliance Management</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Sign In</h2>
          
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your username"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your password"
                required
              />
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center">{error}</div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => handleDemoAccess('admin')}
                className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors font-medium"
              >
                Demo Access
              </button>
            </div>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Demo Credentials:</h3>
            <div className="text-xs text-gray-600 space-y-1">
              <div><strong>Admin:</strong> admin / admin123</div>
              <div><strong>Analyst:</strong> analyst / analyst123</div>
              <div><strong>User:</strong> user / user123</div>
            </div>
            <div className="mt-2 flex space-x-2">
              <button
                onClick={() => handleDemoAccess('admin')}
                className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded"
              >
                Demo Admin
              </button>
              <button
                onClick={() => handleDemoAccess('analyst')}
                className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded"
              >
                Demo Analyst
              </button>
              <button
                onClick={() => handleDemoAccess('user')}
                className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded"
              >
                Demo User
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
