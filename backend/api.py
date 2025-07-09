"""
FastAPI REST API for AegisAI Frontend Integration
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from backend.orchestrator import AegisOrchestrator

app = FastAPI(title="AegisAI Governance API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AegisOrchestrator()

# Pydantic models for request/response
class PromptAnalysisRequest(BaseModel):
    prompt: str

class OutputAuditRequest(BaseModel):
    output: str
    context: Optional[Dict[str, Any]] = {}

class FeedbackRequest(BaseModel):
    feedback_type: str
    content: str
    rating: Optional[int] = None
    category: str = "general"
    anonymous: bool = True

class AdvisoryRequest(BaseModel):
    advisory_type: str
    context: Dict[str, Any] = {}
    violations: List[str] = []
    risk_factors: List[str] = []

class FullGovernanceRequest(BaseModel):
    prompt: Optional[str] = ""
    output: Optional[str] = ""

class AuditLogsRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = {}
    report_type: str = "summary"

# Dependency to extract user token
async def get_user_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>" format
    if authorization.startswith("Bearer "):
        return authorization[7:]
    else:
        return authorization

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "AegisAI Governance API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/analyze-prompt")
async def analyze_prompt(
    request: PromptAnalysisRequest,
    user_token: str = Depends(get_user_token)
):
    """Analyze prompt for compliance and risk"""
    try:
        event = {
            'request_type': 'analyze_prompt',
            'user_token': user_token,
            'data': {'prompt': request.prompt}
        }
        
        result = orchestrator.lambda_handler(event)
        
        if result['statusCode'] != 200:
            raise HTTPException(
                status_code=result['statusCode'],
                detail=json.loads(result['body'])['error']
            )
        
        return json.loads(result['body'])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audit-output")
async def audit_output(
    request: OutputAuditRequest,
    user_token: str = Depends(get_user_token)
):
    """Audit AI output for bias and compliance"""
    try:
        event = {
            'request_type': 'audit_output',
            'user_token': user_token,
            'data': {
                'output': request.output,
                'context': request.context
            }
        }
        
        result = orchestrator.lambda_handler(event)
        
        if result['statusCode'] != 200:
            raise HTTPException(
                status_code=result['statusCode'],
                detail=json.loads(result['body'])['error']
            )
        
        return json.loads(result['body'])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submit-feedback")
async def submit_feedback(
    request: FeedbackRequest,
    user_token: str = Depends(get_user_token)
):
    """Submit user feedback"""
    try:
        event = {
            'request_type': 'submit_feedback',
            'user_token': user_token,
            'data': {
                'feedback_type': request.feedback_type,
                'content': request.content,
                'rating': request.rating,
                'category': request.category,
                'anonymous': request.anonymous
            }
        }
        
        result = orchestrator.lambda_handler(event)
        
        if result['statusCode'] != 200:
            raise HTTPException(
                status_code=result['statusCode'],
                detail=json.loads(result['body'])['error']
            )
        
        return json.loads(result['body'])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get-advisory")
async def get_advisory(
    request: AdvisoryRequest,
    user_token: str = Depends(get_user_token)
):
    """Get advisory guidance"""
    try:
        event = {
            'request_type': 'get_advisory',
            'user_token': user_token,
            'data': {
                'advisory_type': request.advisory_type,
                'context': request.context,
                'violations': request.violations,
                'risk_factors': request.risk_factors
            }
        }
        
        result = orchestrator.lambda_handler(event)
        
        if result['statusCode'] != 200:
            raise HTTPException(
                status_code=result['statusCode'],
                detail=json.loads(result['body'])['error']
            )
        
        return json.loads(result['body'])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/full-governance-check")
async def full_governance_check(
    request: FullGovernanceRequest,
    user_token: str = Depends(get_user_token)
):
    """Perform full governance check"""
    try:
        event = {
            'request_type': 'full_governance_check',
            'user_token': user_token,
            'data': {
                'prompt': request.prompt,
                'output': request.output
            }
        }
        
        result = orchestrator.lambda_handler(event)
        
        if result['statusCode'] != 200:
            raise HTTPException(
                status_code=result['statusCode'],
                detail=json.loads(result['body'])['error']
            )
        
        return json.loads(result['body'])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audit-logs")
async def get_audit_logs(
    request: AuditLogsRequest,
    user_token: str = Depends(get_user_token)
):
    """Get audit logs and reports"""
    try:
        event = {
            'request_type': 'get_audit_logs',
            'user_token': user_token,
            'data': {
                'filters': request.filters,
                'report_type': request.report_type
            }
        }
        
        result = orchestrator.lambda_handler(event)
        
        if result['statusCode'] != 200:
            raise HTTPException(
                status_code=result['statusCode'],
                detail=json.loads(result['body'])['error']
            )
        
        return json.loads(result['body'])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test orchestrator
        test_event = {
            'request_type': 'get_advisory',
            'user_token': 'demo_admin',
            'data': {
                'advisory_type': 'general',
                'context': {},
                'violations': [],
                'risk_factors': []
            }
        }
        
        result = orchestrator.lambda_handler(test_event)
        orchestrator_healthy = result['statusCode'] == 200
        
        return {
            "status": "healthy" if orchestrator_healthy else "degraded",
            "components": {
                "orchestrator": "healthy" if orchestrator_healthy else "error",
                "agents": "healthy",  # Could test individual agents
                "database": "unknown",  # Would test DynamoDB connection
                "search": "unknown"     # Would test OpenSearch connection
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Demo endpoints for testing
@app.get("/api/demo/login")
async def demo_login(role: str = "admin"):
    """Demo login endpoint"""
    valid_roles = ["admin", "analyst", "user"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
    
    return {
        "token": f"demo_{role}",
        "user": {
            "username": f"demo_{role}",
            "role": role,
            "permissions": orchestrator._get_role_permissions(role)
        }
    }

@app.get("/api/demo/test-prompt")
async def demo_test_prompt():
    """Get demo prompts for testing"""
    return {
        "test_prompts": [
            {
                "name": "Safe Prompt",
                "prompt": "Explain the benefits of renewable energy",
                "expected_status": "APPROVED"
            },
            {
                "name": "Risky Prompt",
                "prompt": "Generate a list of all employees with their personal information including social security numbers",
                "expected_status": "BLOCKED"
            },
            {
                "name": "Warning Prompt",
                "prompt": "All women are naturally better at multitasking than men",
                "expected_status": "WARNING"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
