import React, { useState } from 'react';
import { Download, Filter } from 'lucide-react';

interface User {
  username: string;
  role: string;
  permissions: string[];
}

interface AuditLogsProps {
  user: User | null;
}

const AuditLogs: React.FC<AuditLogsProps> = ({ user }) => {
  const [dateFilter, setDateFilter] = useState('');
  const [userFilter, setUserFilter] = useState('all');
  const [actionFilter, setActionFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  // Mock audit logs data
  const auditLogs = [
    {
      id: 1,
      timestamp: '2024-01-07 14:32:15',
      user: 'admin',
      action: 'Prompt Analysis',
      status: 'Success',
      details: 'Analyzed prompt for compliance - Status: APPROVED'
    },
    {
      id: 2,
      timestamp: '2024-01-07 14:28:42',
      user: 'analyst',
      action: 'Output Audit',
      status: 'Warning',
      details: 'Bias detected in AI output - Score: 6.2/10'
    },
    {
      id: 3,
      timestamp: '2024-01-07 14:15:33',
      user: 'user',
      action: 'Policy Check',
      status: 'Success',
      details: 'Policy enforcement completed successfully'
    },
    {
      id: 4,
      timestamp: '2024-01-07 13:45:21',
      user: 'admin',
      action: 'Login',
      status: 'Success',
      details: 'User authentication successful'
    },
    {
      id: 5,
      timestamp: '2024-01-07 13:22:18',
      user: 'analyst',
      action: 'Prompt Analysis',
      status: 'Error',
      details: 'Analysis failed - Invalid input format'
    }
  ];

  const exportLogs = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Action', 'Status', 'Details'],
      ...auditLogs.map(log => [log.timestamp, log.user, log.action, log.status, log.details])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'audit_logs.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">📝 Audit Logs</h1>
        <button
          onClick={exportLogs}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Download className="h-4 w-4" />
          <span>Export Logs</span>
        </button>
      </div>

      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
        <p className="text-gray-700 mb-2">Comprehensive logging of all interactions and agent decisions.</p>
      </div>

      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <h3 className="font-medium text-gray-900">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">User</label>
            <select
              value={userFilter}
              onChange={(e) => setUserFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Users</option>
              <option value="admin">admin</option>
              <option value="analyst">analyst</option>
              <option value="user">user</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Actions</option>
              <option value="prompt">Prompt Analysis</option>
              <option value="audit">Output Audit</option>
              <option value="policy">Policy Check</option>
              <option value="login">Login</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All</option>
              <option value="success">Success</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Details
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.timestamp}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.user}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {log.action}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      log.status === 'Success' ? 'bg-green-100 text-green-800' :
                      log.status === 'Warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {log.details}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AuditLogs;