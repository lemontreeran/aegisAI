// Governance API Service for AegisAI Backend Integration

import { API_BASE_URL, API_ENDPOINTS } from '../config/api';
import { getAuthHeaders } from './auth';

export interface PromptAnalysisRequest {
  prompt: string;
}

export interface PromptAnalysisResponse {
  status: 'APPROVED' | 'WARNING' | 'BLOCKED';
  risk_score: number;
  confidence: number;
  policy_violations: string[];
  content_flags: string[];
  suggestions: string[];
}

export interface OutputAuditRequest {
  output: string;
  context?: Record<string, any>;
}

export interface OutputAuditResponse {
  bias_score: number;
  toxicity_score: number;
  fairness_score: number;
  overall_score: number;
  audit_status: 'APPROVED' | 'REVIEW_RECOMMENDED' | 'REVISION_REQUIRED';
  policy_violations: string[];
  recommendations: string[];
}

export interface FeedbackRequest {
  feedback_type: string;
  content: string;
  rating?: number;
  category: string;
  anonymous: boolean;
}

export interface AdvisoryRequest {
  advisory_type: string;
  context: Record<string, any>;
  violations: string[];
  risk_factors: string[];
}

export interface FullGovernanceRequest {
  prompt?: string;
  output?: string;
}

export interface AuditLogsRequest {
  filters?: Record<string, any>;
  report_type: string;
}

class GovernanceAPI {
  private async makeRequest<T>(
    endpoint: string,
    method: 'GET' | 'POST' = 'POST',
    data?: any
  ): Promise<T> {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const headers = getAuthHeaders();
      
      const config: RequestInit = {
        method,
        headers,
      };
      
      if (data && method === 'POST') {
        config.body = JSON.stringify(data);
      }
      
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      return result.data || result;
      
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  async analyzePrompt(prompt: string): Promise<PromptAnalysisResponse> {
    return this.makeRequest<PromptAnalysisResponse>(
      API_ENDPOINTS.ANALYZE_PROMPT,
      'POST',
      { prompt }
    );
  }

  async auditOutput(output: string, context: Record<string, any> = {}): Promise<OutputAuditResponse> {
    return this.makeRequest<OutputAuditResponse>(
      API_ENDPOINTS.AUDIT_OUTPUT,
      'POST',
      { output, context }
    );
  }

  async submitFeedback(feedbackData: FeedbackRequest): Promise<any> {
    return this.makeRequest(
      API_ENDPOINTS.SUBMIT_FEEDBACK,
      'POST',
      feedbackData
    );
  }

  async getAdvisory(advisoryData: AdvisoryRequest): Promise<any> {
    return this.makeRequest(
      API_ENDPOINTS.GET_ADVISORY,
      'POST',
      advisoryData
    );
  }

  async fullGovernanceCheck(data: FullGovernanceRequest): Promise<any> {
    return this.makeRequest(
      API_ENDPOINTS.FULL_GOVERNANCE_CHECK,
      'POST',
      data
    );
  }

  async getAuditLogs(request: AuditLogsRequest): Promise<any> {
    return this.makeRequest(
      API_ENDPOINTS.AUDIT_LOGS,
      'POST',
      request
    );
  }

  async getHealth(): Promise<any> {
    return this.makeRequest(API_ENDPOINTS.HEALTH, 'GET');
  }

  async getTestPrompts(): Promise<any> {
    return this.makeRequest(API_ENDPOINTS.TEST_PROMPTS, 'GET');
  }
}

// Export singleton instance
export const governanceAPI = new GovernanceAPI();

// Export convenience functions
export const analyzePrompt = (prompt: string) => governanceAPI.analyzePrompt(prompt);
export const auditOutput = (output: string, context?: Record<string, any>) => 
  governanceAPI.auditOutput(output, context);
export const submitFeedback = (data: FeedbackRequest) => governanceAPI.submitFeedback(data);
export const getAdvisory = (data: AdvisoryRequest) => governanceAPI.getAdvisory(data);
export const fullGovernanceCheck = (data: FullGovernanceRequest) => 
  governanceAPI.fullGovernanceCheck(data);
export const getAuditLogs = (data: AuditLogsRequest) => governanceAPI.getAuditLogs(data);