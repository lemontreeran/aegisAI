"""
PromptGuardAgent - Screens GenAI inputs for compliance issues
"""
import re
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent

class PromptGuardAgent(BaseAgent):
    """Agent that screens prompts for compliance violations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        # Load environment variables from .env
        import os
        from dotenv import load_dotenv
        load_dotenv()

        super().__init__("PromptGuardAgent", config)
        self.risk_keywords = [
            "hack", "exploit", "bypass", "jailbreak", "ignore instructions",
            "violence", "harmful", "illegal", "discriminatory", "bias",
            "personal information", "private data", "confidential"
        ]
        # Load policy table name from env or fallback
        table_name = os.getenv("DYNAMODB_POLICIES_TABLE", "aegis-policies")
        self.policy_table = self.dynamodb.Table(table_name)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Screen prompt for compliance issues"""
        prompt = input_data.get('prompt', '')
        user_role = self.user_context.get('role', 'user') if self.user_context else 'user'
        
        # Perform multiple checks
        risk_score = self._calculate_risk_score(prompt)
        policy_violations = self._check_policy_violations(prompt, user_role)
        content_flags = self._detect_harmful_content(prompt)
        
        # Determine overall status
        status = self._determine_status(risk_score, policy_violations, content_flags)
        
        result = {
            "status": status,
            "risk_score": risk_score,
            "confidence": min(95, 70 + (risk_score * 3)),
            "policy_violations": policy_violations,
            "content_flags": content_flags,
            "suggestions": self._generate_suggestions(prompt, policy_violations),
            "processed_at": self._get_timestamp()
        }
        
        # Log the screening activity
        self.log_activity(
            "prompt_screening",
            {
                "prompt_length": len(prompt),
                "risk_score": risk_score,
                "status": status,
                "violations_count": len(policy_violations)
            },
            "success" if status != "ERROR" else "error"
        )
        
        return result
    
    def _calculate_risk_score(self, prompt: str) -> float:
        """Calculate risk score based on content analysis"""
        prompt_lower = prompt.lower()
        risk_score = 0.0
        
        # Check for risk keywords
        for keyword in self.risk_keywords:
            if keyword in prompt_lower:
                risk_score += 1.5
        
        # Check prompt length (very long prompts might be injection attempts)
        if len(prompt) > 2000:
            risk_score += 1.0
        
        # Check for instruction injection patterns
        injection_patterns = [
            r"ignore.*previous.*instructions",
            r"forget.*everything.*above",
            r"new.*instructions.*follow",
            r"system.*prompt.*override"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, prompt_lower):
                risk_score += 2.0
        
        # Use Bedrock for advanced content analysis
        bedrock_analysis = self._bedrock_risk_analysis(prompt)
        risk_score += bedrock_analysis
        
        return min(10.0, risk_score)
    
    def _bedrock_risk_analysis(self, prompt: str) -> float:
        """Use Bedrock to analyze prompt risk"""
        analysis_prompt = f"""
        Analyze the following prompt for potential risks, policy violations, or harmful content.
        Rate the risk level from 0-3 where:
        0 = No risk
        1 = Low risk
        2 = Medium risk  
        3 = High risk
        
        Prompt to analyze: "{prompt}"
        
        Respond with only a number (0-3):
        """
        
        try:
            response = self.call_bedrock(analysis_prompt)
            risk_level = float(response.strip())
            return min(3.0, max(0.0, risk_level))
        except:
            return 0.0
    
    def _check_policy_violations(self, prompt: str, user_role: str) -> List[str]:
        """Check prompt against stored policies"""
        violations = []
        
        try:
            # Get policies from DynamoDB
            response = self.policy_table.scan(
                FilterExpression="attribute_exists(policy_name)"
            )
            
            for policy in response.get('Items', []):
                if self._violates_policy(prompt, policy, user_role):
                    violations.append(policy['policy_name'])
                    
        except Exception as e:
            self.log_activity("policy_check_error", {"error": str(e)}, "error")
        
        return violations
    
    def _violates_policy(self, prompt: str, policy: Dict, user_role: str) -> bool:
        """Check if prompt violates a specific policy"""
        # Check if policy applies to user role
        if user_role not in policy.get('applicable_roles', ['admin', 'analyst', 'user']):
            return False
        
        # Check against policy rules
        rules = policy.get('rules', [])
        for rule in rules:
            if rule.get('type') == 'keyword_block':
                blocked_keywords = rule.get('keywords', [])
                for keyword in blocked_keywords:
                    if keyword.lower() in prompt.lower():
                        return True
        
        return False
    
    def _detect_harmful_content(self, prompt: str) -> List[str]:
        """Detect potentially harmful content patterns"""
        flags = []
        prompt_lower = prompt.lower()
        
        # Violence detection
        violence_keywords = ["kill", "murder", "violence", "attack", "harm", "hurt"]
        if any(keyword in prompt_lower for keyword in violence_keywords):
            flags.append("potential_violence")
        
        # Discrimination detection
        discrimination_keywords = ["racist", "sexist", "discriminate", "stereotype"]
        if any(keyword in prompt_lower for keyword in discrimination_keywords):
            flags.append("potential_discrimination")
        
        # Privacy violation detection
        privacy_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"  # Credit card
        ]
        
        for pattern in privacy_patterns:
            if re.search(pattern, prompt):
                flags.append("potential_privacy_violation")
                break
        
        return flags
    
    def _determine_status(self, risk_score: float, violations: List[str], flags: List[str]) -> str:
        """Determine overall prompt status"""
        if risk_score >= 7.0 or len(violations) >= 2:
            return "BLOCKED"
        elif risk_score >= 4.0 or len(violations) >= 1 or len(flags) >= 1:
            return "WARNING"
        else:
            return "APPROVED"
    
    def _generate_suggestions(self, prompt: str, violations: List[str]) -> List[str]:
        """Generate suggestions for improving the prompt"""
        suggestions = []
        
        if violations:
            suggestions.append("Review and modify content to comply with organizational policies")
        
        if len(prompt) > 2000:
            suggestions.append("Consider shortening the prompt for better processing")
        
        # Use Bedrock to generate contextual suggestions
        if violations or self._calculate_risk_score(prompt) > 3.0:
            bedrock_suggestions = self._get_bedrock_suggestions(prompt)
            if bedrock_suggestions:
                suggestions.extend(bedrock_suggestions)
        
        return suggestions
    
    def _get_bedrock_suggestions(self, prompt: str) -> List[str]:
        """Get improvement suggestions from Bedrock"""
        suggestion_prompt = f"""
        The following prompt has been flagged for potential compliance issues.
        Provide 2-3 specific, actionable suggestions to make it more compliant and appropriate:
        
        Prompt: "{prompt}"
        
        Suggestions:
        """
        
        try:
            response = self.call_bedrock(suggestion_prompt)
            # Parse suggestions from response
            suggestions = [s.strip() for s in response.split('\n') if s.strip() and not s.strip().startswith('Suggestions:')]
            return suggestions[:3]  # Limit to 3 suggestions
        except:
            return []
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
