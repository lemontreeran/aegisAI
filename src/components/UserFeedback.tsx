import React, { useState } from 'react';
import { Send, Star } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useFeedbackSubmission } from '../hooks/useGovernance';

interface User {
  username: string;
  role: string;
  permissions: string[];
}

interface UserFeedbackProps {
  user: User | null;
}

const UserFeedback: React.FC<UserFeedbackProps> = ({ user }) => {
  const [feedbackType, setFeedbackType] = useState('Bug Report');
  const [rating, setRating] = useState(5);
  const [feedbackText, setFeedbackText] = useState('');
  
  const { data: feedbackResult, loading: feedbackLoading, error: feedbackError, submitFeedback } = useFeedbackSubmission();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!feedbackText.trim()) return;
    
    try {
      await submitFeedback({
        feedback_type: feedbackType,
        content: feedbackText,
        rating: rating,
        category: feedbackType.toLowerCase().replace(' ', '_'),
        anonymous: true
      });
      
      // Reset form after successful submission
      setTimeout(() => {
        setFeedbackText('');
        setRating(5);
      }, 2000);
    } catch (error) {
      console.error('Feedback submission failed:', error);
    }
  };

  // Mock feedback analytics data
  const ratingDistribution = [
    { name: '5 Stars', value: 45 },
    { name: '4 Stars', value: 32 },
    { name: '3 Stars', value: 15 },
    { name: '2 Stars', value: 6 },
    { name: '1 Star', value: 2 }
  ];

  const typeDistribution = [
    { name: 'Feature Request', value: 40, color: '#3b82f6' },
    { name: 'Bug Report', value: 30, color: '#ef4444' },
    { name: 'Usability Issue', value: 20, color: '#f59e0b' },
    { name: 'General Feedback', value: 10, color: '#10b981' }
  ];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">💬 User Feedback</h1>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <p className="text-purple-700">Collect and analyze user feedback to improve the governance system.</p>
      </div>

      {/* Feedback Submission */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Submit Feedback</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Feedback Type</label>
              <select
                value={feedbackType}
                onChange={(e) => setFeedbackType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option>Bug Report</option>
                <option>Feature Request</option>
                <option>Usability Issue</option>
                <option>General Feedback</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Overall Rating</label>
              <div className="flex items-center space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className={`p-1 ${star <= rating ? 'text-yellow-400' : 'text-gray-300'} hover:text-yellow-400 transition-colors`}
                  >
                    <Star className="h-6 w-6 fill-current" />
                  </button>
                ))}
                <span className="ml-2 text-sm text-gray-600">({rating} star{rating !== 1 ? 's' : ''})</span>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Your Feedback</label>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Please provide detailed feedback..."
              required
            />
          </div>

          <button
            type="submit"
            disabled={!feedbackText.trim() || feedbackLoading}
            className="flex items-center space-x-2 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
          >
            {feedbackLoading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
            <Send className="h-4 w-4" />
            <span>{feedbackLoading ? 'Submitting...' : 'Submit Feedback'}</span>
          </button>
        </form>

        {feedbackError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">Error: {feedbackError}</p>
          </div>
        )}

        {feedbackResult && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800">
              {feedbackResult.acknowledgment || 'Thank you for your feedback! It has been submitted anonymously.'}
            </p>
          </div>
        )}
      </div>

      {/* Feedback Analytics (Admin only) */}
      {user?.role === 'Admin' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-gray-900">Feedback Analytics</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Rating Distribution */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Rating Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={ratingDistribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Feedback Types */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Feedback Types</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={typeDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {typeDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserFeedback;