"""
Base Agent class for AegisAI Governance System
"""
import json
import boto3
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AegisAI governance agents"""
    
    def __init__(self, agent_name: str, config: Dict[str, Any] = None):
        self.agent_name = agent_name
        self.config = config or {}
        self.session_id = None
        self.user_context = None
        
        # Initialize AWS clients
        self.bedrock_client = boto3.client('bedrock-runtime')
        self.dynamodb = boto3.resource('dynamodb')
        self.opensearch_client = self._init_opensearch()
        
    def _init_opensearch(self):
        """Initialize OpenSearch client"""
        try:
            from opensearchpy import OpenSearch
            return OpenSearch([{
                'host': self.config.get('opensearch_endpoint', 'localhost'),
                'port': 443
            }])
        except Exception as e:
            logger.warning(f"OpenSearch initialization failed: {e}")
            return None
    
    def set_context(self, session_id: str, user_context: Dict[str, Any]):
        """Set execution context for the agent"""
        self.session_id = session_id
        self.user_context = user_context
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    def log_activity(self, activity_type: str, details: Dict[str, Any], status: str = "success"):
        """Log agent activity to OpenSearch"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "user_id": self.user_context.get('user_id') if self.user_context else None,
            "activity_type": activity_type,
            "status": status,
            "details": details
        }
        
        try:
            if self.opensearch_client:
                self.opensearch_client.index(
                    index=f"aegis-logs-{datetime.now().strftime('%Y-%m')}",
                    body=log_entry
                )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    def call_bedrock(self, prompt: str, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> str:
        """Call Amazon Bedrock for AI inference"""
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Bedrock call failed: {e}")
            return ""