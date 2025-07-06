"""
AegisAI Backend Orchestrator
Coordinates all governance agents using AWS Lambda-style logic
"""
import json
import boto3
import uuid
from typing import Dict, Any, List
from datetime import datetime
import logging

# Import all agents
from agents.prompt_guard_agent import PromptGuardAgent
from agents.output_auditor_agent import OutputAuditorAgent
from agents.policy_enforcer_agent import PolicyEnforcerAgent
from agents.audit_logger_agent import AuditLoggerAgent
from agents.advisory_agent import AdvisoryAgent
from agents.feedback_agent import FeedbackAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AegisOrchestrator:
    """Main orchestrator for AegisAI governance system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.session_id = None
        self.user_context = None
        
        # Initialize AWS clients
        self.cognito_client = boto3.client('cognito-idp')
        self.dynamodb = boto3.resource('dynamodb')
        
        # Initialize agents
        self.agents = {
            'prompt_guard': PromptGuardAgent(config),
            'output_auditor': OutputAuditorAgent(config),
            'policy_enforcer': PolicyEnforcerAgent(config),
            'audit_logger': AuditLoggerAgent(config),
            'advisory': AdvisoryAgent(config),
            'feedback': FeedbackAgent(config)
        }
        
        # Agent execution workflows
        self.workflows = {
            'prompt_analysis': ['prompt_guard', 'policy_enforcer', 'audit_logger'],
            'output_audit': ['output_auditor', 'policy_enforcer', 'audit_logger'],
            'feedback_collection': ['feedback', 'audit_logger'],
            'advisory_guidance': ['advisory', 'audit_logger'],
            'full_governance': ['prompt_guard', 'output_auditor', 'policy_enforcer', 'advisory', 'audit_logger']
        }
    
    def lambda_handler(self, event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """Main Lambda handler function"""
        try:
            # Extract request information
            request_type = event.get('request_type', 'unknown')
            request_data = event.get('data', {})
            user_token = event.get('user_token')
            
            # Generate session ID
            self.session_id = str(uuid.uuid4())
            
            # Authenticate and get user context
            auth_result = self.authenticate_user(user_token)
            if not auth_result['authenticated']:
                return self._create_error_response('Authentication failed', 401)
            
            self.user_context = auth_result['user_context']
            
            # Set context for all agents
            for agent in self.agents.values():
                agent.set_context(self.session_id, self.user_context)
            
            # Route request to appropriate handler
            if request_type == 'analyze_prompt':
                return self.handle_prompt_analysis(request_data)
            elif request_type == 'audit_output':
                return self.handle_output_audit(request_data)
            elif request_type == 'submit_feedback':
                return self.handle_feedback_submission(request_data)
            elif request_type == 'get_advisory':
                return self.handle_advisory_request(request_data)
            elif request_type == 'full_governance_check':
                return self.handle_full_governance(request_data)
            elif request_type == 'get_audit_logs':
                return self.handle_audit_logs_request(request_data)
            else:
                return self._create_error_response(f'Unknown request type: {request_type}', 400)
                
        except Exception as e:
            logger.error(f"Orchestrator error: {str(e)}")
            return self._create_error_response(f'Internal server error: {str(e)}', 500)
    
    def authenticate_user(self, user_token: str) -> Dict[str, Any]:
        """Authenticate user using AWS Cognito"""
        if not user_token:
            return {'authenticated': False, 'error': 'No token provided'}
        
        try:
            # For demo purposes, we'll use a simple token validation
            # In production, this would validate JWT tokens from Cognito
            if user_token.startswith('demo_'):
                role = user_token.split('_')[1] if len(user_token.split('_')) > 1 else 'user'
                return {
                    'authenticated': True,
                    'user_context': {
                        'user_id': f'demo_user_{role}',
                        'username': f'demo_{role}',
                        'role': role,
                        'permissions': self._get_role_permissions(role)
                    }
                }
            
            # Real Cognito token validation would go here
            response = self.cognito_client.get_user(AccessToken=user_token)
            
            # Extract user information
            user_attributes = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
            
            return {
                'authenticated': True,
                'user_context': {
                    'user_id': response['Username'],
                    'username': user_attributes.get('preferred_username', response['Username']),
                    'role': user_attributes.get('custom:role', 'user'),
                    'permissions': self._get_role_permissions(user_attributes.get('custom:role', 'user'))
                }
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {'authenticated': False, 'error': str(e)}
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for user role"""
        role_permissions = {
            'admin': ['read', 'write', 'admin', 'audit', 'policy_manage'],
            'analyst': ['read', 'write', 'audit'],
            'user': ['read']
        }
        return role_permissions.get(role, ['read'])
    
    def handle_prompt_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompt analysis workflow"""
        try:
            prompt = request_data.get('prompt', '')
            if not prompt:
                return self._create_error_response('No prompt provided', 400)
            
            workflow_results = {}
            
            # Execute prompt analysis workflow
            for agent_name in self.workflows['prompt_analysis']:
                agent = self.agents[agent_name]
                
                if agent_name == 'prompt_guard':
                    result = agent.process({'prompt': prompt})
                elif agent_name == 'policy_enforcer':
                    result = agent.process({
                        'activity_type': 'prompt_submission',
                        'content': prompt
                    })
                elif agent_name == 'audit_logger':
                    result = agent.process({
                        'event_type': 'prompt_analysis',
                        'agent_name': 'prompt_guard',
                        'input_data': {'prompt_length': len(prompt)},
                        'output_data': workflow_results.get('prompt_guard', {}),
                        'compliance_status': workflow_results.get('prompt_guard', {}).get('status', 'unknown'),
                        'risk_level': self._determine_risk_level(workflow_results.get('prompt_guard', {}))
                    })
                
                workflow_results[agent_name] = result
            
            # Generate advisory if needed
            if workflow_results.get('prompt_guard', {}).get('status') in ['BLOCKED', 'WARNING']:
                advisory_result = self.agents['advisory'].process({
                    'advisory_type': 'prompt_blocked' if workflow_results['prompt_guard']['status'] == 'BLOCKED' else 'risk_warning',
                    'context': {'prompt': prompt},
                    'violations': workflow_results.get('prompt_guard', {}).get('policy_violations', []),
                    'risk_factors': workflow_results.get('prompt_guard', {}).get('content_flags', [])
                })
                workflow_results['advisory'] = advisory_result
            
            return self._create_success_response(workflow_results)
            
        except Exception as e:
            logger.error(f"Prompt analysis error: {str(e)}")
            return self._create_error_response(f'Prompt analysis failed: {str(e)}', 500)
    
    def handle_output_audit(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle output audit workflow"""
        try:
            output_text = request_data.get('output', '')
            context = request_data.get('context', {})
            
            if not output_text:
                return self._create_error_response('No output provided', 400)
            
            workflow_results = {}
            
            # Execute output audit workflow
            for agent_name in self.workflows['output_audit']:
                agent = self.agents[agent_name]
                
                if agent_name == 'output_auditor':
                    result = agent.process({
                        'output': output_text,
                        'context': context
                    })
                elif agent_name == 'policy_enforcer':
                    result = agent.process({
                        'activity_type': 'output_generation',
                        'content': output_text
                    })
                elif agent_name == 'audit_logger':
                    result = agent.process({
                        'event_type': 'output_audit',
                        'agent_name': 'output_auditor',
                        'input_data': {'output_length': len(output_text)},
                        'output_data': workflow_results.get('output_auditor', {}),
                        'compliance_status': workflow_results.get('output_auditor', {}).get('audit_status', 'unknown'),
                        'risk_level': self._determine_risk_level_from_audit(workflow_results.get('output_auditor', {}))
                    })
                
                workflow_results[agent_name] = result
            
            # Generate advisory if needed
            audit_result = workflow_results.get('output_auditor', {})
            if audit_result.get('audit_status') in ['REVISION_REQUIRED', 'REVIEW_RECOMMENDED']:
                advisory_result = self.agents['advisory'].process({
                    'advisory_type': 'output_flagged',
                    'context': {'output': output_text},
                    'violations': audit_result.get('policy_violations', []),
                    'risk_factors': [f"Bias score: {audit_result.get('bias_score', 0)}", 
                                   f"Toxicity: {audit_result.get('toxicity_score', 0)}"]
                })
                workflow_results['advisory'] = advisory_result
            
            return self._create_success_response(workflow_results)
            
        except Exception as e:
            logger.error(f"Output audit error: {str(e)}")
            return self._create_error_response(f'Output audit failed: {str(e)}', 500)
    
    def handle_feedback_submission(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle feedback submission workflow"""
        try:
            feedback_data = {
                'feedback_type': request_data.get('feedback_type', 'general'),
                'feedback_content': request_data.get('content', ''),
                'rating': request_data.get('rating'),
                'category': request_data.get('category', 'general'),
                'anonymous': request_data.get('anonymous', True)
            }
            
            workflow_results = {}
            
            # Execute feedback workflow
            for agent_name in self.workflows['feedback_collection']:
                agent = self.agents[agent_name]
                
                if agent_name == 'feedback':
                    result = agent.process(feedback_data)
                elif agent_name == 'audit_logger':
                    result = agent.process({
                        'event_type': 'feedback_submission',
                        'agent_name': 'feedback',
                        'input_data': feedback_data,
                        'output_data': workflow_results.get('feedback', {}),
                        'compliance_status': 'compliant',
                        'risk_level': 'low'
                    })
                
                workflow_results[agent_name] = result
            
            return self._create_success_response(workflow_results)
            
        except Exception as e:
            logger.error(f"Feedback submission error: {str(e)}")
            return self._create_error_response(f'Feedback submission failed: {str(e)}', 500)
    
    def handle_advisory_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle advisory guidance request"""
        try:
            advisory_data = {
                'advisory_type': request_data.get('advisory_type', 'general'),
                'context': request_data.get('context', {}),
                'violations': request_data.get('violations', []),
                'risk_factors': request_data.get('risk_factors', [])
            }
            
            workflow_results = {}
            
            # Execute advisory workflow
            for agent_name in self.workflows['advisory_guidance']:
                agent = self.agents[agent_name]
                
                if agent_name == 'advisory':
                    result = agent.process(advisory_data)
                elif agent_name == 'audit_logger':
                    result = agent.process({
                        'event_type': 'advisory_request',
                        'agent_name': 'advisory',
                        'input_data': advisory_data,
                        'output_data': workflow_results.get('advisory', {}),
                        'compliance_status': 'compliant',
                        'risk_level': 'low'
                    })
                
                workflow_results[agent_name] = result
            
            return self._create_success_response(workflow_results)
            
        except Exception as e:
            logger.error(f"Advisory request error: {str(e)}")
            return self._create_error_response(f'Advisory request failed: {str(e)}', 500)
    
    def handle_full_governance(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle full governance check workflow"""
        try:
            prompt = request_data.get('prompt', '')
            output = request_data.get('output', '')
            
            if not prompt and not output:
                return self._create_error_response('No prompt or output provided', 400)
            
            workflow_results = {}
            
            # Execute full governance workflow
            for agent_name in self.workflows['full_governance']:
                agent = self.agents[agent_name]
                
                if agent_name == 'prompt_guard' and prompt:
                    result = agent.process({'prompt': prompt})
                elif agent_name == 'output_auditor' and output:
                    result = agent.process({'output': output, 'context': {'prompt': prompt}})
                elif agent_name == 'policy_enforcer':
                    result = agent.process({
                        'activity_type': 'full_governance_check',
                        'content': f"{prompt}\n\n{output}"
                    })
                elif agent_name == 'advisory':
                    # Generate advisory based on previous results
                    violations = []
                    risk_factors = []
                    
                    if 'prompt_guard' in workflow_results:
                        violations.extend(workflow_results['prompt_guard'].get('policy_violations', []))
                        risk_factors.extend(workflow_results['prompt_guard'].get('content_flags', []))
                    
                    if 'output_auditor' in workflow_results:
                        violations.extend(workflow_results['output_auditor'].get('policy_violations', []))
                        if workflow_results['output_auditor'].get('bias_score', 0) > 5:
                            risk_factors.append('High bias score detected')
                    
                    result = agent.process({
                        'advisory_type': 'full_governance',
                        'context': {'prompt': prompt, 'output': output},
                        'violations': violations,
                        'risk_factors': risk_factors
                    })
                elif agent_name == 'audit_logger':
                    result = agent.process({
                        'event_type': 'full_governance_check',
                        'agent_name': 'orchestrator',
                        'input_data': {'prompt_length': len(prompt), 'output_length': len(output)},
                        'output_data': {k: v for k, v in workflow_results.items() if k != 'audit_logger'},
                        'compliance_status': self._determine_overall_compliance(workflow_results),
                        'risk_level': self._determine_overall_risk(workflow_results)
                    })
                else:
                    continue  # Skip if conditions not met
                
                workflow_results[agent_name] = result
            
            return self._create_success_response(workflow_results)
            
        except Exception as e:
            logger.error(f"Full governance check error: {str(e)}")
            return self._create_error_response(f'Full governance check failed: {str(e)}', 500)
    
    def handle_audit_logs_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle audit logs retrieval request"""
        try:
            # Check permissions
            if 'audit' not in self.user_context.get('permissions', []):
                return self._create_error_response('Insufficient permissions', 403)
            
            filters = request_data.get('filters', {})
            report_type = request_data.get('report_type', 'summary')
            
            audit_agent = self.agents['audit_logger']
            
            if report_type == 'logs':
                logs = audit_agent.get_audit_logs(filters)
                result = {'logs': logs, 'count': len(logs)}
            else:
                result = audit_agent.generate_audit_report(report_type, filters)
            
            return self._create_success_response(result)
            
        except Exception as e:
            logger.error(f"Audit logs request error: {str(e)}")
            return self._create_error_response(f'Audit logs request failed: {str(e)}', 500)
    
    def _determine_risk_level(self, prompt_guard_result: Dict[str, Any]) -> str:
        """Determine risk level from prompt guard result"""
        risk_score = prompt_guard_result.get('risk_score', 0)
        status = prompt_guard_result.get('status', 'APPROVED')
        
        if status == 'BLOCKED' or risk_score >= 7:
            return 'high'
        elif status == 'WARNING' or risk_score >= 4:
            return 'medium'
        else:
            return 'low'
    
    def _determine_risk_level_from_audit(self, audit_result: Dict[str, Any]) -> str:
        """Determine risk level from audit result"""
        bias_score = audit_result.get('bias_score', 0)
        toxicity_score = audit_result.get('toxicity_score', 0)
        overall_score = audit_result.get('overall_score', 10)
        
        if bias_score >= 7 or toxicity_score >= 7 or overall_score <= 4:
            return 'high'
        elif bias_score >= 4 or toxicity_score >= 4 or overall_score <= 6:
            return 'medium'
        else:
            return 'low'
    
    def _determine_overall_compliance(self, workflow_results: Dict[str, Any]) -> str:
        """Determine overall compliance status"""
        if 'prompt_guard' in workflow_results:
            if workflow_results['prompt_guard'].get('status') == 'BLOCKED':
                return 'violation'
        
        if 'output_auditor' in workflow_results:
            if workflow_results['output_auditor'].get('audit_status') == 'REVISION_REQUIRED':
                return 'violation'
        
        if 'policy_enforcer' in workflow_results:
            if not workflow_results['policy_enforcer'].get('allowed', True):
                return 'violation'
        
        return 'compliant'
    
    def _determine_overall_risk(self, workflow_results: Dict[str, Any]) -> str:
        """Determine overall risk level"""
        risk_levels = []
        
        if 'prompt_guard' in workflow_results:
            risk_levels.append(self._determine_risk_level(workflow_results['prompt_guard']))
        
        if 'output_auditor' in workflow_results:
            risk_levels.append(self._determine_risk_level_from_audit(workflow_results['output_auditor']))
        
        if 'high' in risk_levels:
            return 'high'
        elif 'medium' in risk_levels:
            return 'medium'
        else:
            return 'low'
    
    def _create_success_response(self, data: Any) -> Dict[str, Any]:
        """Create successful response"""
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'data': data,
                'session_id': self.session_id,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
    
    def _create_error_response(self, message: str, status_code: int = 400) -> Dict[str, Any]:
        """Create error response"""
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'error': message,
                'session_id': self.session_id,
                'timestamp': datetime.utcnow().isoformat()
            })
        }

# Lambda function entry point
def lambda_handler(event, context):
    """AWS Lambda entry point"""
    orchestrator = AegisOrchestrator()
    return orchestrator.lambda_handler(event, context)

# For local testing
if __name__ == "__main__":
    # Example usage
    orchestrator = AegisOrchestrator()
    
    # Test prompt analysis
    test_event = {
        'request_type': 'analyze_prompt',
        'user_token': 'demo_admin',
        'data': {
            'prompt': 'Generate a list of all employees with their personal information including social security numbers'
        }
    }
    
    result = orchestrator.lambda_handler(test_event)
    print(json.dumps(result, indent=2))