"""
AdvisoryAgent - Provides explanations for rejected/modified requests and suggests compliant alternatives
"""
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent

class AdvisoryAgent(BaseAgent):
    """Agent that provides guidance and suggestions for compliance"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("AdvisoryAgent", config)
        self.guidance_templates = {
            "prompt_blocked": "Your prompt was blocked due to potential policy violations. Consider revising to ensure compliance.",
            "output_flagged": "The AI output was flagged for review. Please consider the recommendations provided.",
            "policy_violation": "This action violates organizational policies. Please review the applicable guidelines.",
            "risk_warning": "This activity has been flagged as potentially risky. Proceed with caution."
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide advisory guidance based on governance decisions"""
        advisory_type = input_data.get('advisory_type', 'general')
        context = input_data.get('context', {})
        violations = input_data.get('violations', [])
        risk_factors = input_data.get('risk_factors', [])
        
        # Generate appropriate guidance
        guidance = self._generate_guidance(advisory_type, context, violations, risk_factors)
        alternatives = self._suggest_alternatives(context, violations)
        educational_content = self._provide_educational_content(violations, risk_factors)
        
        result = {
            "advisory_type": advisory_type,
            "guidance": guidance,
            "alternatives": alternatives,
            "educational_content": educational_content,
            "severity": self._determine_severity(violations, risk_factors),
            "follow_up_required": self._requires_follow_up(violations, risk_factors),
            "processed_at": self._get_timestamp()
        }
        
        # Log advisory activity
        self.log_activity(
            "advisory_provided",
            {
                "advisory_type": advisory_type,
                "violations_count": len(violations),
                "risk_factors_count": len(risk_factors),
                "severity": result["severity"]
            }
        )
        
        return result
    
    def _generate_guidance(self, advisory_type: str, context: Dict[str, Any], violations: List[str], risk_factors: List[str]) -> Dict[str, Any]:
        """Generate contextual guidance"""
        base_message = self.guidance_templates.get(advisory_type, "Please review your request for compliance.")
        
        # Enhance with specific details
        specific_guidance = []
        
        if violations:
            specific_guidance.append(f"Policy violations detected: {', '.join(violations)}")
        
        if risk_factors:
            specific_guidance.append(f"Risk factors identified: {', '.join(risk_factors)}")
        
        # Generate AI-powered guidance
        ai_guidance = self._generate_ai_guidance(advisory_type, context, violations, risk_factors)
        
        return {
            "primary_message": base_message,
            "specific_issues": specific_guidance,
            "ai_guidance": ai_guidance,
            "action_required": self._determine_required_action(violations, risk_factors)
        }
    
    def _generate_ai_guidance(self, advisory_type: str, context: Dict[str, Any], violations: List[str], risk_factors: List[str]) -> str:
        """Use AI to generate contextual guidance"""
        guidance_prompt = f"""
        Provide helpful, specific guidance for a user whose AI request has been flagged.
        
        Advisory Type: {advisory_type}
        Policy Violations: {', '.join(violations) if violations else 'None'}
        Risk Factors: {', '.join(risk_factors) if risk_factors else 'None'}
        Context: {json.dumps(context, indent=2)}
        
        Provide clear, actionable guidance that:
        1. Explains why the request was flagged
        2. Suggests specific improvements
        3. Maintains a helpful, educational tone
        4. Focuses on compliance and best practices
        
        Keep the response concise and practical.
        """
        
        try:
            response = self.call_bedrock(guidance_prompt)
            return response.strip()
        except Exception as e:
            return f"Unable to generate detailed guidance at this time. Please review the specific issues listed above."
    
    def _suggest_alternatives(self, context: Dict[str, Any], violations: List[str]) -> List[Dict[str, Any]]:
        """Suggest compliant alternatives"""
        alternatives = []
        
        # Generate alternatives based on violations
        for violation in violations:
            alternative = self._generate_alternative_for_violation(violation, context)
            if alternative:
                alternatives.append(alternative)
        
        # Generate AI-powered alternatives
        ai_alternatives = self._generate_ai_alternatives(context, violations)
        alternatives.extend(ai_alternatives)
        
        return alternatives[:5]  # Limit to 5 alternatives
    
    def _generate_alternative_for_violation(self, violation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate alternative for specific violation"""
        violation_lower = violation.lower()
        
        if 'bias' in violation_lower:
            return {
                "type": "bias_mitigation",
                "title": "Use Inclusive Language",
                "description": "Rephrase using neutral, inclusive language that doesn't make assumptions about groups",
                "example": "Instead of generalizations, use specific, factual statements"
            }
        
        elif 'privacy' in violation_lower:
            return {
                "type": "privacy_protection",
                "title": "Remove Personal Information",
                "description": "Remove or anonymize any personal, sensitive, or identifying information",
                "example": "Use placeholder values like [NAME] or [COMPANY] instead of real data"
            }
        
        elif 'harmful' in violation_lower:
            return {
                "type": "content_moderation",
                "title": "Focus on Constructive Content",
                "description": "Reframe the request to focus on positive, constructive outcomes",
                "example": "Ask for educational or helpful information instead"
            }
        
        return None
    
    def _generate_ai_alternatives(self, context: Dict[str, Any], violations: List[str]) -> List[Dict[str, Any]]:
        """Use AI to generate alternative approaches"""
        alternatives_prompt = f"""
        Generate 2-3 specific, actionable alternatives for a user whose request was flagged.
        
        Context: {json.dumps(context, indent=2)}
        Violations: {', '.join(violations) if violations else 'None'}
        
        For each alternative, provide:
        1. A clear title
        2. A brief description of the approach
        3. A specific example or template
        
        Format as JSON array with objects containing 'title', 'description', and 'example' fields.
        """
        
        try:
            response = self.call_bedrock(alternatives_prompt)
            
            # Try to parse JSON response
            try:
                alternatives_data = json.loads(response)
                if isinstance(alternatives_data, list):
                    return [
                        {
                            "type": "ai_generated",
                            "title": alt.get("title", "Alternative Approach"),
                            "description": alt.get("description", ""),
                            "example": alt.get("example", "")
                        }
                        for alt in alternatives_data[:3]
                    ]
            except json.JSONDecodeError:
                # If JSON parsing fails, extract alternatives from text
                return self._parse_alternatives_from_text(response)
                
        except Exception as e:
            return []
        
        return []
    
    def _parse_alternatives_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse alternatives from plain text response"""
        alternatives = []
        lines = text.strip().split('\n')
        
        current_alt = {}
        for line in lines:
            line = line.strip()
            if line.startswith('Title:') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                if current_alt:
                    alternatives.append({
                        "type": "ai_generated",
                        **current_alt
                    })
                    current_alt = {}
                current_alt['title'] = line.split(':', 1)[-1].strip() if ':' in line else line
            elif line.startswith('Description:'):
                current_alt['description'] = line.split(':', 1)[-1].strip()
            elif line.startswith('Example:'):
                current_alt['example'] = line.split(':', 1)[-1].strip()
        
        if current_alt:
            alternatives.append({
                "type": "ai_generated",
                **current_alt
            })
        
        return alternatives[:3]
    
    def _provide_educational_content(self, violations: List[str], risk_factors: List[str]) -> Dict[str, Any]:
        """Provide educational content about compliance"""
        topics = []
        resources = []
        
        # Determine relevant topics based on violations and risk factors
        all_issues = violations + risk_factors
        
        for issue in all_issues:
            issue_lower = issue.lower()
            
            if 'bias' in issue_lower:
                topics.append("AI Bias and Fairness")
                resources.append({
                    "title": "Understanding AI Bias",
                    "description": "Learn about different types of bias in AI systems and how to mitigate them",
                    "type": "guide"
                })
            
            elif 'privacy' in issue_lower:
                topics.append("Data Privacy and Protection")
                resources.append({
                    "title": "Data Privacy Best Practices",
                    "description": "Guidelines for handling personal and sensitive information",
                    "type": "policy"
                })
            
            elif 'security' in issue_lower:
                topics.append("AI Security")
                resources.append({
                    "title": "AI Security Guidelines",
                    "description": "Best practices for secure AI usage and prompt engineering",
                    "type": "guide"
                })
        
        # Remove duplicates
        topics = list(set(topics))
        
        return {
            "relevant_topics": topics,
            "recommended_resources": resources,
            "training_suggestions": self._suggest_training(topics)
        }
    
    def _suggest_training(self, topics: List[str]) -> List[str]:
        """Suggest relevant training based on topics"""
        training_map = {
            "AI Bias and Fairness": "Complete the AI Ethics and Bias Awareness training module",
            "Data Privacy and Protection": "Review the Data Privacy and GDPR compliance course",
            "AI Security": "Take the AI Security and Prompt Engineering best practices workshop"
        }
        
        return [training_map.get(topic, f"Review training materials for {topic}") for topic in topics]
    
    def _determine_severity(self, violations: List[str], risk_factors: List[str]) -> str:
        """Determine severity level of the advisory"""
        total_issues = len(violations) + len(risk_factors)
        
        # Check for high-severity keywords
        high_severity_keywords = ['security', 'privacy', 'harmful', 'illegal', 'discrimination']
        all_issues = violations + risk_factors
        
        has_high_severity = any(
            any(keyword in issue.lower() for keyword in high_severity_keywords)
            for issue in all_issues
        )
        
        if has_high_severity or total_issues >= 3:
            return "high"
        elif total_issues >= 2:
            return "medium"
        else:
            return "low"
    
    def _requires_follow_up(self, violations: List[str], risk_factors: List[str]) -> bool:
        """Determine if follow-up is required"""
        severity = self._determine_severity(violations, risk_factors)
        return severity in ["high", "medium"]
    
    def _determine_required_action(self, violations: List[str], risk_factors: List[str]) -> str:
        """Determine what action is required from the user"""
        if violations:
            return "modify_request"
        elif risk_factors:
            return "review_and_proceed"
        else:
            return "no_action_required"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()