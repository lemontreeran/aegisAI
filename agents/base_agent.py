"""
Base Agent class for AegisAI Governance System
"""
import json
import boto3
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv
import time
import random

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AegisAI governance agents"""
    
    def __init__(self, agent_name: str, config: Dict[str, Any] = None):
        self.agent_name = agent_name
        self.config = config or {}
        self.session_id = None
        self.user_context = None

        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.default_model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-lite-v1")
        
        # Initialize AWS clients
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=self.aws_region)
        self.dynamodb = boto3.resource('dynamodb', region_name=self.aws_region)
        self.opensearch_client = self._init_opensearch()
        
    def _init_opensearch(self):
        """Initialize OpenSearch client with AWS auth"""
        try:
            from opensearchpy import OpenSearch, RequestsHttpConnection
            from requests_aws4auth import AWS4Auth

            region = self.aws_region
            service = 'es'
            endpoint = self.config.get("opensearch_endpoint") or os.getenv("OPENSEARCH_ENDPOINT")

            if not endpoint:
                raise ValueError("Missing OPENSEARCH_ENDPOINT in config or .env")

            if endpoint.startswith("https://"):
                host = endpoint.replace("https://", "")
                use_ssl = True
            else:
                host = endpoint
                use_ssl = False

            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                region,
                service,
                session_token=credentials.token
            )

            return OpenSearch(
                hosts=[{'host': host, 'port': 443}],
                http_auth=awsauth,
                use_ssl=use_ssl,
                verify_certs=True,
                connection_class=RequestsHttpConnection
            )
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
    
def call_bedrock(self, prompt: str, model_id: Optional[str] = None) -> str:
    model_to_use = model_id or self.default_model_id
    logger.info(f"[Bedrock] Using model: {model_to_use} | Region: {self.aws_region}")

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    })

    retries = 0
    while retries < 4:
        try:
            response = self.bedrock_client.invoke_model(
                modelId=model_to_use,
                body=body
            )
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
        except self.bedrock_client.exceptions.ThrottlingException as e:
            wait_time = (2 ** retries) + random.uniform(0, 1)
            logger.warning(f"Bedrock throttled, retrying in {wait_time:.2f}s...")
            time.sleep(wait_time)
            retries += 1
        except Exception as e:
            logger.error(f"Bedrock call failed: {e}")
            break

    return "[Error: throttled or failed after retries]"
