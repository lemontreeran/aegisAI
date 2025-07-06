import React, { useState } from 'react';
import { Shield, Search, AlertTriangle, FileText, Lightbulb, MessageSquare } from 'lucide-react';

interface User {
  username: string;
  role: string;
  permissions: string[];
}

interface GovernanceAgentsProps {
  user: User | null;
}

const GovernanceAgents: React.FC<GovernanceAgentsProps> = ({ user }) => {
  const [activeTab, setActiveTab] = useState('prompt-guard');
  const [promptText, setPromptText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const tabs = [
    { id: 'prompt-guard', label: 'Prompt Guard', icon: Shield },
    { id: 'output-auditor', label: 'Output Auditor', icon: Search },
    { id: 'policy-enforcer', label: 'Policy Enforcer', icon: AlertTriangle },
    { id: 'audit-logger', label: 'Audit Logger', icon: FileText },
    { id: 'advisory', label: 'Advisory', icon: Lightbulb },
    { id: 'feedback', label: 'Feedback', icon: MessageSquare }
  ];

  const analyzePrompt = () => {
    // Mock analysis
    const mockResult = {
      status: Math.random() > 0.7 ? 'BLOCKED' : Math.random() > 0.4 ? 'WARNING' : 'APPROVED',
      risk_score: Math.random() * 10,
      confidence: 85 + Math.random() * 15,
      issues: Math.random() > 0.5 ? ['Potential bias detected', 'Sensitive content identified'] : [],
      suggestions: ['Consider rephrasing to be more neutral', 'Add context for clarity']
    };
    setAnalysisResult(mockResult);
  };

  const auditOutput = () => {
    // Mock audit
    const mockResult = {
      bias_score: Math.random() * 10,
      toxicity: Math.random() * 100,
      fairness: 7 + Math.random() * 3,
      violations: Math.random() > 0.7 ? ['Gender bias detected'] : [],
      recommendations: ['Review for inclusive language', 'Consider alternative phrasing']
    };
    setAnalysisResult(mockResult);
  };

  const renderPromptGuard = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">🛡️ Prompt Guard Agent</h3>
        <p className="text-blue-700">Screens GenAI inputs for compliance issues and potential risks.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Test Prompt Input
          </label>
          <textarea
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            className="w-full h-40 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter a prompt to test for compliance..."
          />
          <button
            onClick={analyzePrompt}
            disabled={!promptText}
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            Analyze Prompt
          </button>

          {analysisResult && (
            <div className="mt-6 bg-white border border-gray-200 rounded-lg p-6">
              <h4 className="text-lg font-semibold mb-4">Analysis Results</h4>
              
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                    analysisResult.status === 'APPROVED' ? 'bg-green-100 text-green-800' :
                    analysisResult.status === 'WARNING' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {analysisResult.status}
                  </div>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{analysisResult.risk_score.toFixed(1)}</p>
                  <p className="text-sm text-gray-600">Risk Score</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{analysisResult.confidence.toFixed(1)}%</p>
                  <p className="text-sm text-gray-600">Confidence</p>
                </div>
              </div>

              {analysisResult.issues.length > 0 && (
                <div className="mb-4">
                  <h5 className="font-medium text-red-800 mb-2">Identified Issues</h5>
                  {analysisResult.issues.map((issue: string, index: number) => (
                    <div key={index} className="text-red-700 text-sm">• {issue}</div>
                  ))}
                </div>
              )}

              {analysisResult.suggestions.length > 0 && (
                <div>
                  <h5 className="font-medium text-blue-800 mb-2">Suggestions</h5>
                  {analysisResult.suggestions.map((suggestion: string, index: number) => (
                    <div key={index} className="text-blue-700 text-sm">• {suggestion}</div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div>
          <h4 className="font-medium text-gray-900 mb-4">Recent Activity</h4>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm font-medium text-gray-900">2024-01-0{i} 14:3{i}</p>
                <p className="text-sm text-gray-600">Status: {i % 2 === 0 ? 'APPROVED' : 'WARNING'}</p>
                <p className="text-sm text-gray-600">Risk: {(Math.random() * 10).toFixed(1)}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderOutputAuditor = () => (
    <div className="space-y-6">
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-green-900 mb-2">🔍 Output Auditor Agent</h3>
        <p className="text-green-700">Reviews GenAI outputs for bias, fairness, and compliance.</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            AI Output to Audit
          </label>
          <textarea
            value={outputText}
            onChange={(e) => setOutputText(e.target.value)}
            className="w-full h-40 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            placeholder="Paste AI-generated content here for bias and fairness analysis..."
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Audit Type</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500">
              <option>Bias Detection</option>
              <option>Toxicity Check</option>
              <option>Fairness Analysis</option>
              <option>Content Policy</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sensitivity Level</label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500">
              <option>Low</option>
              <option>Medium</option>
              <option>High</option>
            </select>
          </div>
        </div>

        <button
          onClick={auditOutput}
          disabled={!outputText}
          className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
        >
          Audit Output
        </button>

        {analysisResult && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="text-lg font-semibold mb-4">Audit Results</h4>
            
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">{analysisResult.bias_score?.toFixed(1) || '0.0'}</p>
                <p className="text-sm text-gray-600">Bias Score</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">{analysisResult.toxicity?.toFixed(1) || '0.0'}%</p>
                <p className="text-sm text-gray-600">Toxicity Level</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">{analysisResult.fairness?.toFixed(1) || '0.0'}</p>
                <p className="text-sm text-gray-600">Fairness Rating</p>
              </div>
            </div>

            {analysisResult.violations?.length > 0 && (
              <div className="mb-4">
                <h5 className="font-medium text-red-800 mb-2">Policy Violations</h5>
                {analysisResult.violations.map((violation: string, index: number) => (
                  <div key={index} className="text-red-700 text-sm">• {violation}</div>
                ))}
              </div>
            )}

            {analysisResult.recommendations?.length > 0 && (
              <div>
                <h5 className="font-medium text-blue-800 mb-2">Recommendations</h5>
                {analysisResult.recommendations.map((rec: string, index: number) => (
                  <div key={index} className="text-blue-700 text-sm">• {rec}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  const renderPlaceholder = (title: string, description: string) => (
    <div className="text-center py-12">
      <div className="bg-gray-100 rounded-lg p-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
        <p className="text-sm text-gray-500 mt-4">This interface would be implemented here</p>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'prompt-guard':
        return renderPromptGuard();
      case 'output-auditor':
        return renderOutputAuditor();
      case 'policy-enforcer':
        return renderPlaceholder('Policy Enforcer Agent', 'Dynamically applies governance rules based on user roles and activity type.');
      case 'audit-logger':
        return renderPlaceholder('Audit Logger Agent', 'Comprehensive logging of all interactions and agent decisions.');
      case 'advisory':
        return renderPlaceholder('Advisory Agent', 'Provides explanations and suggests compliant alternatives.');
      case 'feedback':
        return renderPlaceholder('Feedback Agent', 'Collect and analyze user feedback to improve the governance system.');
      default:
        return renderPromptGuard();
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">🤖 Governance Agents</h1>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {renderTabContent()}
    </div>
  );
};

export default GovernanceAgents;