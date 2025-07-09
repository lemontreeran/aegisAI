// API Configuration for AegisAI Backend Integration

export const API_BASE_URL = 'http://localhost:8000/api';

export const API_ENDPOINTS = {
  // Authentication
  DEMO_LOGIN: '/demo/login',
  
  // Governance Operations
  ANALYZE_PROMPT: '/analyze-prompt',
  AUDIT_OUTPUT: '/audit-output',
  SUBMIT_FEEDBACK: '/submit-feedback',
  GET_ADVISORY: '/get-advisory',
  FULL_GOVERNANCE_CHECK: '/full-governance-check',
  AUDIT_LOGS: '/audit-logs',
  
  // Health Check
  HEALTH: '/health',
  
  // Demo Data
  TEST_PROMPTS: '/demo/test-prompt'
};

export const API_CONFIG = {
  timeout: 30000,
  retries: 3,
  headers: {
    'Content-Type': 'application/json',
  }
};