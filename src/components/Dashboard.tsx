import React from 'react';
import { TrendingUp, TrendingDown, Shield, AlertTriangle, CheckCircle, Users } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

interface User {
  username: string;
  role: string;
  permissions: string[];
}

interface DashboardProps {
  user: User | null;
}

const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  // Mock data
  const metrics = {
    totalRequests: 12847,
    requestsDelta: 234,
    complianceRate: 94.2,
    complianceDelta: 2.1,
    riskScore: 3.2,
    riskDelta: 0.8,
    activePolicies: 28,
    policiesDelta: 3
  };

  const complianceTrends = [
    { date: '2024-01-01', compliance_rate: 92.1 },
    { date: '2024-01-02', compliance_rate: 93.5 },
    { date: '2024-01-03', compliance_rate: 91.8 },
    { date: '2024-01-04', compliance_rate: 94.2 },
    { date: '2024-01-05', compliance_rate: 95.1 },
    { date: '2024-01-06', compliance_rate: 93.8 },
    { date: '2024-01-07', compliance_rate: 94.2 }
  ];

  const riskDistribution = [
    { name: 'Low', value: 65, color: '#10b981' },
    { name: 'Medium', value: 28, color: '#f59e0b' },
    { name: 'High', value: 7, color: '#ef4444' }
  ];

  const agentStatus = [
    {
      name: 'Prompt Guard Agent',
      description: 'Screening GenAI inputs for compliance',
      status: 'Active',
      processed: 3247,
      accuracy: 96.8
    },
    {
      name: 'Output Auditor Agent',
      description: 'Reviewing outputs for bias and fairness',
      status: 'Active',
      processed: 2891,
      accuracy: 94.2
    },
    {
      name: 'Policy Enforcer Agent',
      description: 'Applying governance rules dynamically',
      status: 'Active',
      processed: 1456,
      accuracy: 98.1
    },
    {
      name: 'Audit Logger Agent',
      description: 'Comprehensive interaction logging',
      status: 'Active',
      processed: 12847,
      accuracy: 99.9
    }
  ];

  const MetricCard = ({ title, value, delta, icon: Icon, trend }: any) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          <div className="flex items-center mt-2">
            {trend === 'up' ? (
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
            )}
            <span className={`text-sm font-medium ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
              {delta}
            </span>
          </div>
        </div>
        <div className="p-3 bg-blue-50 rounded-lg">
          <Icon className="h-6 w-6 text-blue-600" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-8">
        <h1 className="text-3xl font-bold mb-2">🛡️ AegisAI Governance Dashboard</h1>
        <p className="text-blue-200">Welcome back, {user?.username}. Here's your governance overview.</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Requests Today"
          value={metrics.totalRequests.toLocaleString()}
          delta={`+${metrics.requestsDelta}`}
          icon={Users}
          trend="up"
        />
        <MetricCard
          title="Compliance Rate"
          value={`${metrics.complianceRate}%`}
          delta={`+${metrics.complianceDelta}%`}
          icon={CheckCircle}
          trend="up"
        />
        <MetricCard
          title="Risk Score"
          value={metrics.riskScore.toFixed(1)}
          delta={`-${metrics.riskDelta}`}
          icon={AlertTriangle}
          trend="up"
        />
        <MetricCard
          title="Active Policies"
          value={metrics.activePolicies}
          delta={`+${metrics.policiesDelta}`}
          icon={Shield}
          trend="up"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compliance Trends */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={complianceTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="compliance_rate" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Agent Status Overview */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Agent Status Overview</h3>
        <div className="space-y-4">
          {agentStatus.map((agent, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{agent.name}</h4>
                <p className="text-sm text-gray-600">{agent.description}</p>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                    agent.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {agent.status}
                  </span>
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-900">{agent.processed.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">processed</p>
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-900">{agent.accuracy}%</p>
                  <p className="text-xs text-gray-500">accuracy</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;