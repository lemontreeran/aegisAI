"""
PolicyEnforcerAgent - Dynamically applies governance rules based on user roles and activity type
"""
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent

class PolicyEnforcerAgent(BaseAgent):
    """Agent that enforces policies based on user context and activity"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("PolicyEnforcerAgent", config)
        self.policy_table = self.dynamodb.Table('aegis-policies')
        self.user_table = self.dynamodb.Table('aegis-users')
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce policies based on user context and activity"""
        activity_type = input_data.get('activity_type', 'general')
        content = input_data.get('content', '')
        user_id = self.user_context.get('user_id') if self.user_context else None
        user_role = self.user_context.get('role', 'user') if self.user_context else 'user'
        
        # Get applicable policies
        applicable_policies = self._get_applicable_policies(user_role, activity_type)
        
        # Evaluate each policy
        policy_results = []
        overall_allowed = True
        enforcement_actions = []
        
        for policy in applicable_policies:
            result = self._evaluate_policy(policy, content, user_role, activity_type)
            policy_results.append(result)
            
            if not result['allowed']:
                overall_allowed = False
                enforcement_actions.extend(result.get('actions', []))
        
        # Apply enforcement actions
        if not overall_allowed:
            self._apply_enforcement_actions(enforcement_actions, user_id)
        
        result = {
            "allowed": overall_allowed,
            "policy_results": policy_results,
            "enforcement_actions": enforcement_actions,
            "applicable_policies_count": len(applicable_policies),
            "user_role": user_role,
            "activity_type": activity_type,
            "processed_at": self._get_timestamp()
        }
        
        # Log enforcement activity
        self.log_activity(
            "policy_enforcement",
            {
                "user_role": user_role,
                "activity_type": activity_type,
                "allowed": overall_allowed,
                "policies_evaluated": len(applicable_policies),
                "violations": len([r for r in policy_results if not r['allowed']])
            }
        )
        
        return result
    
    def _get_applicable_policies(self, user_role: str, activity_type: str) -> List[Dict]:
        """Get policies applicable to the user role and activity type"""
        try:
            response = self.policy_table.scan()
            policies = response.get('Items', [])
            
            applicable = []
            for policy in policies:
                # Check if policy applies to user role
                applicable_roles = policy.get('applicable_roles', ['admin', 'analyst', 'user'])
                if user_role not in applicable_roles:
                    continue
                
                # Check if policy applies to activity type
                applicable_activities = policy.get('applicable_activities', ['all'])
                if 'all' not in applicable_activities and activity_type not in applicable_activities:
                    continue
                
                # Check if policy is active
                if policy.get('status', 'active') == 'active':
                    applicable.append(policy)
            
            return applicable
            
        except Exception as e:
            self.log_activity("policy_retrieval_error", {"error": str(e)}, "error")
            return []
    
    def _evaluate_policy(self, policy: Dict, content: str, user_role: str, activity_type: str) -> Dict[str, Any]:
        """Evaluate a single policy against the content"""
        policy_name = policy.get('policy_name', 'Unknown')
        rules = policy.get('rules', [])
        
        violations = []
        allowed = True
        actions = []
        
        for rule in rules:
            rule_result = self._evaluate_rule(rule, content, user_role, activity_type)
            
            if not rule_result['passed']:
                violations.append(rule_result)
                allowed = False
                actions.extend(rule_result.get('actions', []))
        
        return {
            "policy_name": policy_name,
            "allowed": allowed,
            "violations": violations,
            "actions": actions,
            "rule_count": len(rules)
        }
    
    def _evaluate_rule(self, rule: Dict, content: str, user_role: str, activity_type: str) -> Dict[str, Any]:
        """Evaluate a single rule"""
        rule_type = rule.get('type', 'unknown')
        rule_name = rule.get('name', 'Unnamed Rule')
        
        if rule_type == 'content_filter':
            return self._evaluate_content_filter(rule, content)
        elif rule_type == 'role_restriction':
            return self._evaluate_role_restriction(rule, user_role, activity_type)
        elif rule_type == 'time_restriction':
            return self._evaluate_time_restriction(rule)
        elif rule_type == 'content_length':
            return self._evaluate_content_length(rule, content)
        elif rule_type == 'ai_analysis':
            return self._evaluate_ai_analysis(rule, content)
        else:
            return {
                "rule_name": rule_name,
                "passed": True,
                "message": f"Unknown rule type: {rule_type}",
                "actions": []
            }
    
    def _evaluate_content_filter(self, rule: Dict, content: str) -> Dict[str, Any]:
        """Evaluate content filter rule"""
        rule_name = rule.get('name', 'Content Filter')
        blocked_terms = rule.get('blocked_terms', [])
        required_terms = rule.get('required_terms', [])
        
        content_lower = content.lower()
        violations = []
        
        # Check blocked terms
        for term in blocked_terms:
            if term.lower() in content_lower:
                violations.append(f"Contains blocked term: {term}")
        
        # Check required terms
        for term in required_terms:
            if term.lower() not in content_lower:
                violations.append(f"Missing required term: {term}")
        
        passed = len(violations) == 0
        actions = rule.get('enforcement_actions', ['warn']) if not passed else []
        
        return {
            "rule_name": rule_name,
            "passed": passed,
            "message": "; ".join(violations) if violations else "Content filter passed",
            "actions": actions
        }
    
    def _evaluate_role_restriction(self, rule: Dict, user_role: str, activity_type: str) -> Dict[str, Any]:
        """Evaluate role-based restriction"""
        rule_name = rule.get('name', 'Role Restriction')
        allowed_roles = rule.get('allowed_roles', ['admin'])
        restricted_activities = rule.get('restricted_activities', [])
        
        violations = []
        
        # Check if user role is allowed
        if user_role not in allowed_roles:
            violations.append(f"Role '{user_role}' not authorized for this action")
        
        # Check if activity is restricted
        if activity_type in restricted_activities:
            violations.append(f"Activity '{activity_type}' is restricted")
        
        passed = len(violations) == 0
        actions = rule.get('enforcement_actions', ['block']) if not passed else []
        
        return {
            "rule_name": rule_name,
            "passed": passed,
            "message": "; ".join(violations) if violations else "Role restriction passed",
            "actions": actions
        }
    
    def _evaluate_time_restriction(self, rule: Dict) -> Dict[str, Any]:
        """Evaluate time-based restriction"""
        rule_name = rule.get('name', 'Time Restriction')
        
        # For demo purposes, always pass time restrictions
        # In production, this would check business hours, maintenance windows, etc.
        
        return {
            "rule_name": rule_name,
            "passed": True,
            "message": "Time restriction passed",
            "actions": []
        }
    
    def _evaluate_content_length(self, rule: Dict, content: str) -> Dict[str, Any]:
        """Evaluate content length restrictions"""
        rule_name = rule.get('name', 'Content Length')
        max_length = rule.get('max_length', 10000)
        min_length = rule.get('min_length', 0)
        
        content_length = len(content)
        violations = []
        
        if content_length > max_length:
            violations.append(f"Content too long: {content_length} > {max_length}")
        
        if content_length < min_length:
            violations.append(f"Content too short: {content_length} < {min_length}")
        
        passed = len(violations) == 0
        actions = rule.get('enforcement_actions', ['warn']) if not passed else []
        
        return {
            "rule_name": rule_name,
            "passed": passed,
            "message": "; ".join(violations) if violations else "Content length within limits",
            "actions": actions
        }
    
    def _evaluate_ai_analysis(self, rule: Dict, content: str) -> Dict[str, Any]:
        """Evaluate using AI analysis"""
        rule_name = rule.get('name', 'AI Analysis')
        analysis_type = rule.get('analysis_type', 'general')
        threshold = rule.get('threshold', 0.5)
        
        # Use Bedrock for analysis
        analysis_result = self._bedrock_policy_analysis(content, analysis_type)
        
        passed = analysis_result['score'] <= threshold
        actions = rule.get('enforcement_actions', ['review']) if not passed else []
        
        return {
            "rule_name": rule_name,
            "passed": passed,
            "message": f"AI analysis score: {analysis_result['score']:.2f} (threshold: {threshold})",
            "actions": actions,
            "analysis_details": analysis_result
        }
    
    def _bedrock_policy_analysis(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Use Bedrock for policy compliance analysis"""
        analysis_prompt = f"""
        Analyze the following content for {analysis_type} policy compliance.
        Rate the compliance risk from 0.0 (fully compliant) to 1.0 (major violations).
        
        Content: "{content}"
        
        Provide your analysis in this format:
        Score: [0.0-1.0]
        Reasoning: [brief explanation]
        """
        
        try:
            response = self.call_bedrock(analysis_prompt)
            
            # Parse response
            lines = response.strip().split('\n')
            score = 0.0
            reasoning = "Analysis completed"
            
            for line in lines:
                if line.startswith('Score:'):
                    try:
                        score = float(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('Reasoning:'):
                    reasoning = line.split(':', 1)[1].strip()
            
            return {
                "score": min(1.0, max(0.0, score)),
                "reasoning": reasoning,
                "analysis_type": analysis_type
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "reasoning": f"Analysis failed: {str(e)}",
                "analysis_type": analysis_type
            }
    
    def _apply_enforcement_actions(self, actions: List[str], user_id: str):
        """Apply enforcement actions"""
        for action in actions:
            if action == 'warn':
                self._log_warning(user_id)
            elif action == 'block':
                self._log_block(user_id)
            elif action == 'review':
                self._flag_for_review(user_id)
            elif action == 'escalate':
                self._escalate_to_admin(user_id)
    
    def _log_warning(self, user_id: str):
        """Log a warning for the user"""
        self.log_activity(
            "enforcement_warning",
            {"user_id": user_id, "action": "warning_issued"}
        )
    
    def _log_block(self, user_id: str):
        """Log a block action"""
        self.log_activity(
            "enforcement_block",
            {"user_id": user_id, "action": "access_blocked"}
        )
    
    def _flag_for_review(self, user_id: str):
        """Flag content for manual review"""
        self.log_activity(
            "enforcement_review",
            {"user_id": user_id, "action": "flagged_for_review"}
        )
    
    def _escalate_to_admin(self, user_id: str):
        """Escalate to administrator"""
        self.log_activity(
            "enforcement_escalation",
            {"user_id": user_id, "action": "escalated_to_admin"}
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()