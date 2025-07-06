import React, { useState, useEffect } from 'react';
import { Shield, BarChart3, Users, Settings, FileText, AlertTriangle, MessageSquare, LogOut, Menu, X } from 'lucide-react';
import Dashboard from './components/Dashboard';
import GovernanceAgents from './components/GovernanceAgents';
import PolicyManagement from './components/PolicyManagement';
import AuditLogs from './components/AuditLogs';
import RiskAssessment from './components/RiskAssessment';
import UserFeedback from './components/UserFeedback';
import SettingsPage from './components/SettingsPage';
import LoginPage from './components/LoginPage';

interface User {
  username: string;
  role: string;
  permissions: string[];
}

type PageType = 'Dashboard' | 'Governance Agents' | 'Policy Management' | 'Audit Logs' | 'Risk Assessment' | 'User Feedback' | 'Settings';

function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [currentPage, setCurrentPage] = useState<PageType>('Dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogin = (userData: User) => {
    setAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    setAuthenticated(false);
    setUser(null);
    setCurrentPage('Dashboard');
  };

  const navigationItems = [
    { id: 'Dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'Governance Agents', label: 'Governance Agents', icon: Shield },
    { id: 'Policy Management', label: 'Policy Management', icon: FileText },
    { id: 'Audit Logs', label: 'Audit Logs', icon: FileText },
    { id: 'Risk Assessment', label: 'Risk Assessment', icon: AlertTriangle },
    { id: 'User Feedback', label: 'User Feedback', icon: MessageSquare },
    { id: 'Settings', label: 'Settings', icon: Settings },
  ];

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'Dashboard':
        return <Dashboard user={user} />;
      case 'Governance Agents':
        return <GovernanceAgents user={user} />;
      case 'Policy Management':
        return <PolicyManagement user={user} />;
      case 'Audit Logs':
        return <AuditLogs user={user} />;
      case 'Risk Assessment':
        return <RiskAssessment user={user} />;
      case 'User Feedback':
        return <UserFeedback user={user} />;
      case 'Settings':
        return <SettingsPage user={user} />;
      default:
        return <Dashboard user={user} />;
    }
  };

  if (!authenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-gradient-to-b from-gray-900 to-gray-800 text-white transition-all duration-300 flex flex-col`}>
        {/* Header */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className={`flex items-center space-x-3 ${!sidebarOpen && 'justify-center'}`}>
              <Shield className="h-8 w-8 text-blue-400" />
              {sidebarOpen && <span className="text-xl font-bold">AegisAI</span>}
            </div>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1 rounded-lg hover:bg-gray-700 transition-colors"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* User Info */}
        {sidebarOpen && (
          <div className="p-4 border-b border-gray-700">
            <div className="text-sm">
              <p className="font-medium">{user?.username}</p>
              <p className="text-gray-400">{user?.role}</p>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.id}>
                  <button
                    onClick={() => setCurrentPage(item.id as PageType)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                      currentPage === item.id
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    } ${!sidebarOpen && 'justify-center'}`}
                  >
                    <Icon className="h-5 w-5" />
                    {sidebarOpen && <span>{item.label}</span>}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Logout */}
        <div className="p-4 border-t border-gray-700">
          <button
            onClick={handleLogout}
            className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition-colors ${!sidebarOpen && 'justify-center'}`}
          >
            <LogOut className="h-5 w-5" />
            {sidebarOpen && <span>Sign Out</span>}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {renderCurrentPage()}
      </div>
    </div>
  );
}

export default App;