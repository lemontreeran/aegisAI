"""
AuditLoggerAgent - Logs all interactions and agent decisions to Amazon OpenSearch
"""
import json
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent

class AuditLoggerAgent(BaseAgent):
    """Agent that provides comprehensive logging of all system interactions"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("AuditLoggerAgent", config)
        self.log_table = self.dynamodb.Table('aegis-audit-logs')
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and log audit information"""
        log_entry = self._create_log_entry(input_data)
        
        # Store in multiple locations for redundancy
        opensearch_result = self._store_in_opensearch(log_entry)
        dynamodb_result = self._store_in_dynamodb(log_entry)
        
        # Generate audit summary
        audit_summary = self._generate_audit_summary(log_entry)
        
        result = {
            "log_id": log_entry['log_id'],
            "stored_opensearch": opensearch_result,
            "stored_dynamodb": dynamodb_result,
            "audit_summary": audit_summary,
            "timestamp": log_entry['timestamp'],
            "processed_at": self._get_timestamp()
        }
        
        return result
    
    def _create_log_entry(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive log entry"""
        timestamp = datetime.utcnow()
        log_id = f"audit_{timestamp.strftime('%Y%m%d_%H%M%S')}_{hash(str(input_data)) % 10000:04d}"
        
        log_entry = {
            "log_id": log_id,
            "timestamp": timestamp.isoformat(),
            "session_id": self.session_id,
            "user_context": self.user_context or {},
            "event_type": input_data.get('event_type', 'unknown'),
            "agent_name": input_data.get('agent_name', 'system'),
            "activity_details": input_data.get('activity_details', {}),
            "input_data": self._sanitize_sensitive_data(input_data.get('input_data', {})),
            "output_data": self._sanitize_sensitive_data(input_data.get('output_data', {})),
            "performance_metrics": input_data.get('performance_metrics', {}),
            "compliance_status": input_data.get('compliance_status', 'unknown'),
            "risk_level": input_data.get('risk_level', 'low'),
            "metadata": {
                "ip_address": input_data.get('ip_address', 'unknown'),
                "user_agent": input_data.get('user_agent', 'unknown'),
                "request_id": input_data.get('request_id', log_id)
            }
        }
        
        return log_entry
    
    def _sanitize_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or mask sensitive information from log data"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        sensitive_keys = ['password', 'token', 'key', 'secret', 'credential']
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if key contains sensitive information
            if any(sensitive_key in key_lower for sensitive_key in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_sensitive_data(value)
            elif isinstance(value, str) and len(value) > 1000:
                # Truncate very long strings
                sanitized[key] = value[:1000] + "...[TRUNCATED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _store_in_opensearch(self, log_entry: Dict[str, Any]) -> bool:
        """Store log entry in OpenSearch"""
        try:
            if not self.opensearch_client:
                return False
            
            index_name = f"aegis-audit-{datetime.now().strftime('%Y-%m')}"
            
            response = self.opensearch_client.index(
                index=index_name,
                id=log_entry['log_id'],
                body=log_entry
            )
            
            return response.get('result') == 'created' or response.get('result') == 'updated'
            
        except Exception as e:
            # Log the error but don't fail the entire operation
            self.log_activity(
                "opensearch_storage_error",
                {"error": str(e), "log_id": log_entry['log_id']},
                "error"
            )
            return False
    
    def _store_in_dynamodb(self, log_entry: Dict[str, Any]) -> bool:
        """Store log entry in DynamoDB as backup"""
        try:
            # Convert datetime objects to strings for DynamoDB
            dynamodb_entry = json.loads(json.dumps(log_entry, default=str))
            
            self.log_table.put_item(Item=dynamodb_entry)
            return True
            
        except Exception as e:
            # Log the error
            self.log_activity(
                "dynamodb_storage_error",
                {"error": str(e), "log_id": log_entry['log_id']},
                "error"
            )
            return False
    
    def _generate_audit_summary(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of audit entry for quick review"""
        summary = {
            "event_type": log_entry.get('event_type', 'unknown'),
            "user_id": log_entry.get('user_context', {}).get('user_id', 'anonymous'),
            "user_role": log_entry.get('user_context', {}).get('role', 'unknown'),
            "agent_involved": log_entry.get('agent_name', 'system'),
            "compliance_status": log_entry.get('compliance_status', 'unknown'),
            "risk_level": log_entry.get('risk_level', 'low'),
            "timestamp": log_entry.get('timestamp'),
            "requires_attention": self._requires_attention(log_entry)
        }
        
        return summary
    
    def _requires_attention(self, log_entry: Dict[str, Any]) -> bool:
        """Determine if log entry requires immediate attention"""
        risk_level = log_entry.get('risk_level', 'low')
        compliance_status = log_entry.get('compliance_status', 'compliant')
        
        # Flag high-risk or non-compliant activities
        if risk_level in ['high', 'critical']:
            return True
        
        if compliance_status in ['violation', 'blocked', 'failed']:
            return True
        
        # Check for error conditions
        activity_details = log_entry.get('activity_details', {})
        if activity_details.get('status') == 'error':
            return True
        
        return False
    
    def get_audit_logs(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve audit logs with optional filtering"""
        try:
            if filters:
                # Build filter expression for DynamoDB
                filter_expression = []
                expression_values = {}
                
                if 'start_date' in filters:
                    filter_expression.append('#ts >= :start_date')
                    expression_values[':start_date'] = filters['start_date']
                
                if 'end_date' in filters:
                    filter_expression.append('#ts <= :end_date')
                    expression_values[':end_date'] = filters['end_date']
                
                if 'user_id' in filters:
                    filter_expression.append('user_context.user_id = :user_id')
                    expression_values[':user_id'] = filters['user_id']
                
                if 'event_type' in filters:
                    filter_expression.append('event_type = :event_type')
                    expression_values[':event_type'] = filters['event_type']
                
                if filter_expression:
                    response = self.log_table.scan(
                        FilterExpression=' AND '.join(filter_expression),
                        ExpressionAttributeNames={'#ts': 'timestamp'},
                        ExpressionAttributeValues=expression_values
                    )
                else:
                    response = self.log_table.scan()
            else:
                response = self.log_table.scan()
            
            return response.get('Items', [])
            
        except Exception as e:
            self.log_activity(
                "audit_retrieval_error",
                {"error": str(e), "filters": filters},
                "error"
            )
            return []
    
    def generate_audit_report(self, report_type: str = 'summary', filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate audit report"""
        logs = self.get_audit_logs(filters)
        
        if report_type == 'summary':
            return self._generate_summary_report(logs)
        elif report_type == 'compliance':
            return self._generate_compliance_report(logs)
        elif report_type == 'security':
            return self._generate_security_report(logs)
        else:
            return self._generate_detailed_report(logs)
    
    def _generate_summary_report(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary audit report"""
        total_events = len(logs)
        event_types = {}
        risk_levels = {}
        compliance_statuses = {}
        
        for log in logs:
            # Count event types
            event_type = log.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Count risk levels
            risk_level = log.get('risk_level', 'low')
            risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
            
            # Count compliance statuses
            compliance_status = log.get('compliance_status', 'unknown')
            compliance_statuses[compliance_status] = compliance_statuses.get(compliance_status, 0) + 1
        
        return {
            "report_type": "summary",
            "total_events": total_events,
            "event_types": event_types,
            "risk_levels": risk_levels,
            "compliance_statuses": compliance_statuses,
            "generated_at": self._get_timestamp()
        }
    
    def _generate_compliance_report(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate compliance-focused audit report"""
        violations = [log for log in logs if log.get('compliance_status') in ['violation', 'blocked']]
        warnings = [log for log in logs if log.get('compliance_status') == 'warning']
        
        return {
            "report_type": "compliance",
            "total_events": len(logs),
            "violations": len(violations),
            "warnings": len(warnings),
            "compliance_rate": ((len(logs) - len(violations)) / len(logs) * 100) if logs else 100,
            "violation_details": violations[:10],  # Top 10 violations
            "generated_at": self._get_timestamp()
        }
    
    def _generate_security_report(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate security-focused audit report"""
        high_risk_events = [log for log in logs if log.get('risk_level') in ['high', 'critical']]
        failed_events = [log for log in logs if log.get('activity_details', {}).get('status') == 'error']
        
        return {
            "report_type": "security",
            "total_events": len(logs),
            "high_risk_events": len(high_risk_events),
            "failed_events": len(failed_events),
            "security_incidents": high_risk_events[:5],  # Top 5 incidents
            "generated_at": self._get_timestamp()
        }
    
    def _generate_detailed_report(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed audit report"""
        return {
            "report_type": "detailed",
            "total_events": len(logs),
            "logs": logs,
            "generated_at": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.utcnow().isoformat()