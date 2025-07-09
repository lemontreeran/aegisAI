// React Hooks for Governance Operations

import { useState, useCallback } from 'react';
import { 
  governanceAPI, 
  PromptAnalysisResponse, 
  OutputAuditResponse,
  PromptAnalysisRequest,
  OutputAuditRequest,
  FeedbackRequest,
  AdvisoryRequest,
  FullGovernanceRequest,
  AuditLogsRequest
} from '../services/governanceApi';

interface UseGovernanceState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function usePromptAnalysis() {
  const [state, setState] = useState<UseGovernanceState<PromptAnalysisResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const analyzePrompt = useCallback(async (prompt: string) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await governanceAPI.analyzePrompt(prompt);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Analysis failed';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    analyzePrompt,
  };
}

export function useOutputAudit() {
  const [state, setState] = useState<UseGovernanceState<OutputAuditResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const auditOutput = useCallback(async (output: string, context: Record<string, any> = {}) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await governanceAPI.auditOutput(output, context);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Audit failed';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    auditOutput,
  };
}

export function useFeedbackSubmission() {
  const [state, setState] = useState<UseGovernanceState<any>>({
    data: null,
    loading: false,
    error: null,
  });

  const submitFeedback = useCallback(async (feedbackData: FeedbackRequest) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await governanceAPI.submitFeedback(feedbackData);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Feedback submission failed';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    submitFeedback,
  };
}

export function useAdvisory() {
  const [state, setState] = useState<UseGovernanceState<any>>({
    data: null,
    loading: false,
    error: null,
  });

  const getAdvisory = useCallback(async (advisoryData: AdvisoryRequest) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await governanceAPI.getAdvisory(advisoryData);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Advisory request failed';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    getAdvisory,
  };
}

export function useFullGovernance() {
  const [state, setState] = useState<UseGovernanceState<any>>({
    data: null,
    loading: false,
    error: null,
  });

  const performFullCheck = useCallback(async (data: FullGovernanceRequest) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await governanceAPI.fullGovernanceCheck(data);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Full governance check failed';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    performFullCheck,
  };
}

export function useAuditLogs() {
  const [state, setState] = useState<UseGovernanceState<any>>({
    data: null,
    loading: false,
    error: null,
  });

  const getAuditLogs = useCallback(async (request: AuditLogsRequest) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await governanceAPI.getAuditLogs(request);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Audit logs retrieval failed';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    getAuditLogs,
  };
}

// Utility hook for health checks
export function useHealthCheck() {
  const [state, setState] = useState<UseGovernanceState<any>>({
    data: null,
    loading: false,
    error: null,
  });

  const checkHealth = useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await governanceAPI.getHealth();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Health check failed';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    checkHealth,
  };
}