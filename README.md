# AegisAI - Multi-Agent Governance System

AegisAI is a comprehensive AI governance platform that implements a multi-agent system for GenAI applications. It provides real-time compliance monitoring, risk assessment, and policy enforcement for AI-powered applications.

## 🏗️ Architecture

### Frontend (React/TypeScript)
- **Dashboard**: Real-time governance metrics and agent status
- **Governance Agents**: Interactive interfaces for testing and monitoring
- **Audit Logs**: Comprehensive logging and reporting
- **User Feedback**: Feedback collection and analytics
- **Policy Management**: Policy configuration and enforcement

### Backend (Python)
- **Orchestrator**: AWS Lambda-style coordination of all agents
- **6 Specialized Agents**: Each handling specific governance aspects
- **AWS Integration**: Bedrock, Cognito, DynamoDB, OpenSearch
- **REST API**: FastAPI-based API for frontend integration

## 🤖 Governance Agents

### 1. PromptGuardAgent
- **Purpose**: Screens GenAI inputs for compliance issues
- **Features**:
  - Risk scoring based on content analysis
  - Policy violation detection
  - Harmful content identification
  - AI-powered analysis using Amazon Bedrock
  - Contextual suggestions for improvement

### 2. OutputAuditorAgent
- **Purpose**: Reviews GenAI outputs for bias and fairness
- **Features**:
  - Bias detection and scoring
  - Toxicity analysis
  - Fairness assessment
  - Sentiment analysis
  - Policy compliance checking
  - Actionable recommendations

### 3. PolicyEnforcerAgent
- **Purpose**: Dynamically applies governance rules based on user roles and activity type
- **Features**:
  - Role-based access control
  - Dynamic policy application
  - Content filtering
  - Time-based restrictions
  - AI-powered policy analysis
  - Enforcement action logging

### 4. AuditLoggerAgent
- **Purpose**: Comprehensive logging of all interactions and agent decisions
- **Features**:
  - Multi-storage logging (OpenSearch + DynamoDB)
  - Sensitive data sanitization
  - Audit report generation
  - Compliance tracking
  - Security incident detection

### 5. AdvisoryAgent
- **Purpose**: Provides explanations for rejected/modified requests and suggests compliant alternatives
- **Features**:
  - Contextual guidance generation
  - Alternative suggestion engine
  - Educational content provision
  - Severity assessment
  - AI-powered recommendations

### 6. FeedbackAgent
- **Purpose**: Collects user feedback anonymously and stores it in DynamoDB
- **Features**:
  - Anonymous feedback collection
  - Sentiment analysis
  - Theme extraction
  - Priority assessment
  - Analytics and reporting

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- AWS Account (for full functionality)
- AWS CLI configured

### Backend Setup

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure AWS services** (optional for demo):
```bash
# Set up AWS credentials
aws configure

# Create required DynamoDB tables
python scripts/setup_dynamodb.py

# Configure OpenSearch domain
python scripts/setup_opensearch.py
```

3. **Start the FastAPI server**:
```bash
# For development
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000

# For production
python backend/api.py
```

### Frontend Setup

The frontend is already running in your current environment. To integrate with the backend:

1. **Update API configuration** in `src/config/api.ts`:
```typescript
export const API_BASE_URL = 'http://localhost:8000/api';
```

2. **Add authentication integration** in `src/services/auth.ts`:
```typescript
export const authenticateUser = async (credentials) => {
  const response = await fetch(`${API_BASE_URL}/demo/login?role=${credentials.role}`);
  return response.json();
};
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# DynamoDB Tables
DYNAMODB_POLICIES_TABLE=aegis-policies
DYNAMODB_USERS_TABLE=aegis-users
DYNAMODB_AUDIT_LOGS_TABLE=aegis-audit-logs
DYNAMODB_FEEDBACK_TABLE=aegis-feedback

# OpenSearch
OPENSEARCH_ENDPOINT=your-opensearch-endpoint
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=your-password

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Cognito
COGNITO_USER_POOL_ID=your-user-pool-id
COGNITO_CLIENT_ID=your-client-id
```

### Agent Configuration

Each agent can be configured via the `config` parameter:

```python
config = {
    'opensearch_endpoint': 'your-endpoint',
    'bedrock_model': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'risk_threshold': 5.0,
    'enable_ai_analysis': True
}

agent = PromptGuardAgent(config)
```

## 🔗 Frontend Integration

### API Integration

Update your frontend components to use the backend API:

```typescript
// src/services/governanceApi.ts
export class GovernanceAPI {
  private baseUrl = 'http://localhost:8000/api';
  private token = localStorage.getItem('auth_token');

  async analyzePrompt(prompt: string) {
    const response = await fetch(`${this.baseUrl}/analyze-prompt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({ prompt })
    });
    return response.json();
  }

  async auditOutput(output: string, context = {}) {
    const response = await fetch(`${this.baseUrl}/audit-output`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({ output, context })
    });
    return response.json();
  }

  async submitFeedback(feedbackData: any) {
    const response = await fetch(`${this.baseUrl}/submit-feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(feedbackData)
    });
    return response.json();
  }
}
```

### Component Updates

Update your React components to use real API calls:

```typescript
// src/components/GovernanceAgents.tsx
import { GovernanceAPI } from '../services/governanceApi';

const api = new GovernanceAPI();

const analyzePrompt = async () => {
  try {
    const result = await api.analyzePrompt(promptText);
    setAnalysisResult(result.data);
  } catch (error) {
    console.error('Analysis failed:', error);
  }
};
```

## 📊 Monitoring and Analytics

### Dashboard Metrics
- Total requests processed
- Compliance rate
- Risk score distribution
- Agent performance metrics
- Policy violation trends

### Audit Logs
- Comprehensive interaction logging
- Compliance tracking
- Security incident detection
- Performance monitoring
- User activity analysis

### Reporting
- Compliance reports
- Security assessments
- User feedback analytics
- Agent performance reports
- Policy effectiveness analysis

## 🔒 Security Features

### Authentication
- AWS Cognito integration
- Role-based access control (Admin, Analyst, User)
- JWT token validation
- Session management

### Data Protection
- Sensitive data sanitization
- Encrypted storage
- Audit trail maintenance
- Privacy-preserving analytics

### Compliance
- Policy enforcement
- Regulatory compliance tracking
- Automated violation detection
- Remediation workflows

## 🧪 Testing

### Demo Mode
The system includes demo functionality for testing without AWS setup:

```bash
# Start backend in demo mode
python backend/api.py

# Test with demo credentials
curl -X POST "http://localhost:8000/api/analyze-prompt" \
  -H "Authorization: Bearer demo_admin" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test prompt for analysis"}'
```

### Unit Tests
```bash
# Run agent tests
python -m pytest tests/test_agents.py

# Run orchestrator tests
python -m pytest tests/test_orchestrator.py

# Run API tests
python -m pytest tests/test_api.py
```

## 📈 Scaling and Deployment

### AWS Lambda Deployment
```bash
# Package for Lambda
zip -r aegis-lambda.zip agents/ backend/ requirements.txt

# Deploy using AWS CLI
aws lambda create-function \
  --function-name aegis-orchestrator \
  --runtime python3.9 \
  --role arn:aws:iam::account:role/lambda-role \
  --handler backend.orchestrator.lambda_handler \
  --zip-file fileb://aegis-lambda.zip
```

### Container Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the demo examples

## 🔮 Roadmap

- [ ] Advanced ML model integration
- [ ] Real-time streaming analytics
- [ ] Multi-language support
- [ ] Enhanced visualization
- [ ] Mobile application
- [ ] Third-party integrations