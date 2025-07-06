"""
OutputAuditorAgent - Reviews GenAI outputs for bias and fairness
"""
import json
import re
from typing import Dict, Any, List
from textblob import TextBlob
from .base_agent import BaseAgent

class OutputAuditorAgent(BaseAgent):
    """Agent that audits AI outputs for bias, fairness, and compliance"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("OutputAuditorAgent", config)
        self.bias_indicators = [
            "always", "never", "all", "none", "every", "typical",
            "naturally", "obviously", "clearly", "definitely"
        ]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Audit AI output for bias and compliance issues"""
        output_text = input_data.get('output', '')
        context = input_data.get('context', {})
        
        # Perform comprehensive audit
        bias_score = self._calculate_bias_score(output_text)
        toxicity_score = self._calculate_toxicity_score(output_text)
        fairness_score = self._calculate_fairness_score(output_text)
        sentiment_analysis = self._analyze_sentiment(output_text)
        policy_violations = self._check_output_policies(output_text)
        
        # Generate overall assessment
        overall_score = self._calculate_overall_score(bias_score, toxicity_score, fairness_score)
        recommendations = self._generate_recommendations(output_text, bias_score, toxicity_score, policy_violations)
        
        result = {
            "bias_score": bias_score,
            "toxicity_score": toxicity_score,
            "fairness_score": fairness_score,
            "overall_score": overall_score,
            "sentiment": sentiment_analysis,
            "policy_violations": policy_violations,
            "recommendations": recommendations,
            "audit_status": self._determine_audit_status(overall_score, policy_violations),
            "processed_at": self._get_timestamp()
        }
        
        # Log audit activity
        self.log_activity(
            "output_audit",
            {
                "output_length": len(output_text),
                "bias_score": bias_score,
                "toxicity_score": toxicity_score,
                "overall_score": overall_score,
                "violations_count": len(policy_violations)
            }
        )
        
        return result
    
    def _calculate_bias_score(self, text: str) -> float:
        """Calculate bias score based on language patterns"""
        bias_score = 0.0
        text_lower = text.lower()
        
        # Check for absolute language (bias indicator)
        absolute_count = sum(1 for indicator in self.bias_indicators if indicator in text_lower)
        bias_score += absolute_count * 0.5
        
        # Check for gender bias patterns
        gender_bias_patterns = [
            r'\b(he|she)\s+(always|never|typically)',
            r'\b(men|women)\s+(are|tend to|usually)',
            r'\b(male|female)\s+(dominated|oriented)'
        ]
        
        for pattern in gender_bias_patterns:
            if re.search(pattern, text_lower):
                bias_score += 1.0
        
        # Check for racial/ethnic bias indicators
        racial_terms = ["race", "ethnic", "cultural", "nationality"]
        stereotype_words = ["typical", "characteristic", "natural", "inherent"]
        
        for racial_term in racial_terms:
            for stereotype in stereotype_words:
                if racial_term in text_lower and stereotype in text_lower:
                    bias_score += 1.5
        
        # Use Bedrock for advanced bias detection
        bedrock_bias = self._bedrock_bias_analysis(text)
        bias_score += bedrock_bias
        
        return min(10.0, bias_score)
    
    def _bedrock_bias_analysis(self, text: str) -> float:
        """Use Bedrock to detect subtle bias"""
        bias_prompt = f"""
        Analyze the following text for potential bias, including:
        - Gender bias
        - Racial or ethnic bias  
        - Age bias
        - Socioeconomic bias
        - Cultural bias
        
        Rate the bias level from 0-3:
        0 = No detectable bias
        1 = Minimal bias
        2 = Moderate bias
        3 = Significant bias
        
        Text to analyze: "{text}"
        
        Respond with only a number (0-3):
        """
        
        try:
            response = self.call_bedrock(bias_prompt)
            bias_level = float(response.strip())
            return min(3.0, max(0.0, bias_level))
        except:
            return 0.0
    
    def _calculate_toxicity_score(self, text: str) -> float:
        """Calculate toxicity score"""
        toxicity_score = 0.0
        text_lower = text.lower()
        
        # Basic toxicity indicators
        toxic_keywords = [
            "hate", "stupid", "idiot", "moron", "disgusting",
            "terrible", "awful", "horrible", "pathetic", "worthless"
        ]
        
        for keyword in toxic_keywords:
            if keyword in text_lower:
                toxicity_score += 1.0
        
        # Check for aggressive language patterns
        aggressive_patterns = [
            r'\b(you\s+are|you\'re)\s+(wrong|stupid|crazy)',
            r'\b(shut\s+up|go\s+away|get\s+lost)',
            r'\b(i\s+hate|i\s+despise|i\s+can\'t\s+stand)'
        ]
        
        for pattern in aggressive_patterns:
            if re.search(pattern, text_lower):
                toxicity_score += 2.0
        
        # Use Bedrock for toxicity analysis
        bedrock_toxicity = self._bedrock_toxicity_analysis(text)
        toxicity_score += bedrock_toxicity
        
        return min(10.0, toxicity_score)
    
    def _bedrock_toxicity_analysis(self, text: str) -> float:
        """Use Bedrock to analyze toxicity"""
        toxicity_prompt = f"""
        Analyze the following text for toxic content including:
        - Hate speech
        - Harassment
        - Threats
        - Offensive language
        - Discriminatory content
        
        Rate toxicity from 0-3:
        0 = Not toxic
        1 = Mildly toxic
        2 = Moderately toxic
        3 = Highly toxic
        
        Text: "{text}"
        
        Respond with only a number (0-3):
        """
        
        try:
            response = self.call_bedrock(toxicity_prompt)
            toxicity_level = float(response.strip())
            return min(3.0, max(0.0, toxicity_level))
        except:
            return 0.0
    
    def _calculate_fairness_score(self, text: str) -> float:
        """Calculate fairness score (higher is better)"""
        fairness_score = 8.0  # Start with high fairness
        text_lower = text.lower()
        
        # Check for inclusive language
        inclusive_indicators = [
            "everyone", "all people", "regardless of", "inclusive",
            "diverse", "equitable", "fair", "balanced"
        ]
        
        inclusive_count = sum(1 for indicator in inclusive_indicators if indicator in text_lower)
        fairness_score += inclusive_count * 0.5
        
        # Penalize exclusive language
        exclusive_indicators = [
            "only", "just", "merely", "simply", "obviously",
            "naturally", "of course", "clearly"
        ]
        
        exclusive_count = sum(1 for indicator in exclusive_indicators if indicator in text_lower)
        fairness_score -= exclusive_count * 0.3
        
        return max(0.0, min(10.0, fairness_score))
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the output"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                sentiment_label = "positive"
            elif polarity < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            return {
                "polarity": polarity,
                "subjectivity": subjectivity,
                "label": sentiment_label
            }
        except:
            return {
                "polarity": 0.0,
                "subjectivity": 0.0,
                "label": "neutral"
            }
    
    def _check_output_policies(self, text: str) -> List[str]:
        """Check output against content policies"""
        violations = []
        
        try:
            policy_table = self.dynamodb.Table('aegis-policies')
            response = policy_table.scan(
                FilterExpression="attribute_exists(policy_name) AND policy_type = :type",
                ExpressionAttributeValues={':type': 'output_content'}
            )
            
            for policy in response.get('Items', []):
                if self._violates_output_policy(text, policy):
                    violations.append(policy['policy_name'])
                    
        except Exception as e:
            self.log_activity("output_policy_check_error", {"error": str(e)}, "error")
        
        return violations
    
    def _violates_output_policy(self, text: str, policy: Dict) -> bool:
        """Check if output violates a specific policy"""
        rules = policy.get('rules', [])
        text_lower = text.lower()
        
        for rule in rules:
            if rule.get('type') == 'prohibited_content':
                prohibited_terms = rule.get('terms', [])
                for term in prohibited_terms:
                    if term.lower() in text_lower:
                        return True
            
            elif rule.get('type') == 'required_disclaimer':
                required_phrases = rule.get('phrases', [])
                for phrase in required_phrases:
                    if phrase.lower() not in text_lower:
                        return True
        
        return False
    
    def _calculate_overall_score(self, bias_score: float, toxicity_score: float, fairness_score: float) -> float:
        """Calculate overall audit score"""
        # Weighted combination (lower is better for bias/toxicity, higher for fairness)
        weighted_score = (
            (10 - bias_score) * 0.4 +
            (10 - toxicity_score) * 0.4 +
            fairness_score * 0.2
        )
        return round(weighted_score, 2)
    
    def _generate_recommendations(self, text: str, bias_score: float, toxicity_score: float, violations: List[str]) -> List[str]:
        """Generate recommendations for improving the output"""
        recommendations = []
        
        if bias_score > 5.0:
            recommendations.append("Consider using more inclusive and balanced language")
            recommendations.append("Avoid absolute statements and generalizations")
        
        if toxicity_score > 3.0:
            recommendations.append("Review content for potentially offensive or harmful language")
            recommendations.append("Consider a more respectful and constructive tone")
        
        if violations:
            recommendations.append("Ensure compliance with organizational content policies")
        
        # Get Bedrock recommendations
        if bias_score > 3.0 or toxicity_score > 2.0:
            bedrock_recs = self._get_bedrock_recommendations(text)
            recommendations.extend(bedrock_recs)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _get_bedrock_recommendations(self, text: str) -> List[str]:
        """Get improvement recommendations from Bedrock"""
        rec_prompt = f"""
        The following AI-generated text has been flagged for potential bias or toxicity issues.
        Provide 2-3 specific recommendations to improve the content:
        
        Text: "{text}"
        
        Recommendations:
        """
        
        try:
            response = self.call_bedrock(rec_prompt)
            recommendations = [r.strip() for r in response.split('\n') if r.strip() and not r.strip().startswith('Recommendations:')]
            return recommendations[:3]
        except:
            return []
    
    def _determine_audit_status(self, overall_score: float, violations: List[str]) -> str:
        """Determine audit status based on scores"""
        if overall_score >= 8.0 and not violations:
            return "APPROVED"
        elif overall_score >= 6.0 and len(violations) <= 1:
            return "REVIEW_RECOMMENDED"
        else:
            return "REVISION_REQUIRED"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()