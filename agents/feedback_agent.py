"""
FeedbackAgent - Collects user feedback anonymously and stores it in DynamoDB
"""
import json
import uuid
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent

class FeedbackAgent(BaseAgent):
    """Agent that collects and analyzes user feedback"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("FeedbackAgent", config)
        self.feedback_table = self.dynamodb.Table('aegis-feedback')
        self.analytics_table = self.dynamodb.Table('aegis-feedback-analytics')
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user feedback submission"""
        feedback_type = input_data.get('feedback_type', 'general')
        feedback_content = input_data.get('feedback_content', '')
        rating = input_data.get('rating', None)
        category = input_data.get('category', 'general')
        
        # Create feedback entry
        feedback_entry = self._create_feedback_entry(
            feedback_type, feedback_content, rating, category, input_data
        )
        
        # Store feedback
        storage_result = self._store_feedback(feedback_entry)
        
        # Analyze feedback sentiment and themes
        analysis_result = self._analyze_feedback(feedback_entry)
        
        # Update analytics
        self._update_analytics(feedback_entry, analysis_result)
        
        result = {
            "feedback_id": feedback_entry['feedback_id'],
            "stored": storage_result,
            "analysis": analysis_result,
            "acknowledgment": self._generate_acknowledgment(feedback_type, rating),
            "processed_at": self._get_timestamp()
        }
        
        # Log feedback activity
        self.log_activity(
            "feedback_collected",
            {
                "feedback_type": feedback_type,
                "category": category,
                "rating": rating,
                "sentiment": analysis_result.get('sentiment', 'neutral'),
                "anonymous": input_data.get('anonymous', True)
            }
        )
        
        return result
    
    def _create_feedback_entry(self, feedback_type: str, content: str, rating: int, category: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive feedback entry"""
        feedback_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Determine if feedback should be anonymous
        anonymous = input_data.get('anonymous', True)
        
        feedback_entry = {
            "feedback_id": feedback_id,
            "timestamp": timestamp.isoformat(),
            "feedback_type": feedback_type,
            "category": category,
            "content": content,
            "rating": rating,
            "anonymous": anonymous,
            "session_id": self.session_id if not anonymous else None,
            "user_context": self._sanitize_user_context() if not anonymous else None,
            "metadata": {
                "content_length": len(content),
                "submission_method": input_data.get('submission_method', 'web'),
                "user_agent": input_data.get('user_agent', 'unknown'),
                "platform": input_data.get('platform', 'web')
            }
        }
        
        return feedback_entry
    
    def _sanitize_user_context(self) -> Dict[str, Any]:
        """Sanitize user context for feedback storage"""
        if not self.user_context:
            return None
        
        # Only include non-sensitive information
        sanitized = {
            "user_role": self.user_context.get('role'),
            "user_type": self.user_context.get('user_type', 'standard'),
            "experience_level": self.user_context.get('experience_level', 'unknown')
        }
        
        return sanitized
    
    def _store_feedback(self, feedback_entry: Dict[str, Any]) -> bool:
        """Store feedback in DynamoDB"""
        try:
            # Convert datetime objects to strings for DynamoDB
            dynamodb_entry = json.loads(json.dumps(feedback_entry, default=str))
            
            self.feedback_table.put_item(Item=dynamodb_entry)
            return True
            
        except Exception as e:
            self.log_activity(
                "feedback_storage_error",
                {"error": str(e), "feedback_id": feedback_entry['feedback_id']},
                "error"
            )
            return False
    
    def _analyze_feedback(self, feedback_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze feedback content for sentiment and themes"""
        content = feedback_entry.get('content', '')
        rating = feedback_entry.get('rating')
        
        # Sentiment analysis
        sentiment_analysis = self._analyze_sentiment(content, rating)
        
        # Theme extraction
        themes = self._extract_themes(content)
        
        # Priority assessment
        priority = self._assess_priority(feedback_entry, sentiment_analysis, themes)
        
        # AI-powered analysis
        ai_analysis = self._ai_feedback_analysis(content, feedback_entry.get('feedback_type'))
        
        return {
            "sentiment": sentiment_analysis,
            "themes": themes,
            "priority": priority,
            "ai_insights": ai_analysis,
            "actionable": self._is_actionable(content, themes),
            "category_confidence": self._validate_category(content, feedback_entry.get('category'))
        }
    
    def _analyze_sentiment(self, content: str, rating: int = None) -> Dict[str, Any]:
        """Analyze sentiment of feedback content"""
        try:
            from textblob import TextBlob
            
            blob = TextBlob(content)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Adjust sentiment based on rating if provided
            if rating is not None:
                if rating <= 2:
                    sentiment_label = "negative"
                    polarity = min(polarity, -0.1)  # Ensure negative polarity
                elif rating >= 4:
                    sentiment_label = "positive"
                    polarity = max(polarity, 0.1)   # Ensure positive polarity
                else:
                    sentiment_label = "neutral"
            else:
                if polarity > 0.1:
                    sentiment_label = "positive"
                elif polarity < -0.1:
                    sentiment_label = "negative"
                else:
                    sentiment_label = "neutral"
            
            return {
                "label": sentiment_label,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "confidence": abs(polarity) + 0.3  # Base confidence
            }
            
        except Exception:
            # Fallback sentiment analysis based on rating
            if rating is not None:
                if rating <= 2:
                    return {"label": "negative", "polarity": -0.5, "subjectivity": 0.5, "confidence": 0.7}
                elif rating >= 4:
                    return {"label": "positive", "polarity": 0.5, "subjectivity": 0.5, "confidence": 0.7}
            
            return {"label": "neutral", "polarity": 0.0, "subjectivity": 0.5, "confidence": 0.5}
    
    def _extract_themes(self, content: str) -> List[str]:
        """Extract themes from feedback content"""
        content_lower = content.lower()
        themes = []
        
        # Define theme keywords
        theme_keywords = {
            "usability": ["easy", "difficult", "confusing", "intuitive", "user-friendly", "interface"],
            "performance": ["slow", "fast", "speed", "performance", "lag", "responsive"],
            "accuracy": ["accurate", "wrong", "correct", "mistake", "error", "precise"],
            "features": ["feature", "functionality", "capability", "option", "tool"],
            "design": ["design", "layout", "appearance", "visual", "ui", "ux"],
            "reliability": ["reliable", "stable", "crash", "bug", "issue", "problem"],
            "support": ["help", "support", "documentation", "guide", "assistance"],
            "security": ["security", "privacy", "safe", "secure", "protection"],
            "integration": ["integration", "compatibility", "connect", "sync", "api"]
        }
        
        # Check for theme keywords
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                themes.append(theme)
        
        # Use AI for additional theme extraction
        ai_themes = self._ai_theme_extraction(content)
        themes.extend(ai_themes)
        
        # Remove duplicates and limit
        return list(set(themes))[:5]
    
    def _ai_theme_extraction(self, content: str) -> List[str]:
        """Use AI to extract themes from feedback"""
        theme_prompt = f"""
        Analyze the following user feedback and identify the main themes or topics.
        Return only the theme names, one per line, maximum 3 themes.
        
        Feedback: "{content}"
        
        Themes:
        """
        
        try:
            response = self.call_bedrock(theme_prompt)
            themes = [theme.strip() for theme in response.split('\n') if theme.strip()]
            return themes[:3]
        except:
            return []
    
    def _assess_priority(self, feedback_entry: Dict[str, Any], sentiment: Dict[str, Any], themes: List[str]) -> str:
        """Assess priority level of feedback"""
        rating = feedback_entry.get('rating', 3)
        sentiment_label = sentiment.get('label', 'neutral')
        
        # High priority conditions
        if rating <= 2 and sentiment_label == 'negative':
            return "high"
        
        if any(theme in ['security', 'reliability', 'accuracy'] for theme in themes):
            return "high"
        
        # Medium priority conditions
        if rating <= 3 or sentiment_label == 'negative':
            return "medium"
        
        if any(theme in ['usability', 'performance', 'features'] for theme in themes):
            return "medium"
        
        # Default to low priority
        return "low"
    
    def _ai_feedback_analysis(self, content: str, feedback_type: str) -> Dict[str, Any]:
        """Use AI to provide deeper feedback analysis"""
        analysis_prompt = f"""
        Analyze this user feedback and provide insights:
        
        Feedback Type: {feedback_type}
        Content: "{content}"
        
        Provide analysis in this format:
        Key Issues: [list main issues mentioned]
        Suggestions: [actionable suggestions based on feedback]
        Impact: [potential impact if not addressed]
        """
        
        try:
            response = self.call_bedrock(analysis_prompt)
            
            # Parse the response
            lines = response.strip().split('\n')
            analysis = {
                "key_issues": [],
                "suggestions": [],
                "impact": "Unknown"
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('Key Issues:'):
                    current_section = 'key_issues'
                    content_part = line.split(':', 1)[1].strip()
                    if content_part:
                        analysis['key_issues'].append(content_part)
                elif line.startswith('Suggestions:'):
                    current_section = 'suggestions'
                    content_part = line.split(':', 1)[1].strip()
                    if content_part:
                        analysis['suggestions'].append(content_part)
                elif line.startswith('Impact:'):
                    analysis['impact'] = line.split(':', 1)[1].strip()
                elif line and current_section:
                    analysis[current_section].append(line)
            
            return analysis
            
        except Exception as e:
            return {
                "key_issues": ["Analysis unavailable"],
                "suggestions": ["Manual review recommended"],
                "impact": "Unknown",
                "error": str(e)
            }
    
    def _is_actionable(self, content: str, themes: List[str]) -> bool:
        """Determine if feedback is actionable"""
        content_lower = content.lower()
        
        # Check for actionable keywords
        actionable_keywords = [
            "should", "could", "would", "suggest", "recommend", "improve",
            "add", "remove", "change", "fix", "update", "enhance"
        ]
        
        has_actionable_language = any(keyword in content_lower for keyword in actionable_keywords)
        has_specific_themes = bool(themes)
        has_sufficient_length = len(content.split()) >= 5
        
        return has_actionable_language and has_specific_themes and has_sufficient_length
    
    def _validate_category(self, content: str, assigned_category: str) -> float:
        """Validate if the assigned category matches the content"""
        # Simple keyword-based validation
        category_keywords = {
            "bug_report": ["bug", "error", "crash", "broken", "issue", "problem"],
            "feature_request": ["feature", "add", "new", "enhancement", "improvement"],
            "usability": ["difficult", "confusing", "hard", "easy", "intuitive"],
            "performance": ["slow", "fast", "speed", "performance", "lag"],
            "general": ["feedback", "comment", "suggestion", "opinion"]
        }
        
        content_lower = content.lower()
        assigned_keywords = category_keywords.get(assigned_category, [])
        
        if not assigned_keywords:
            return 0.5  # Unknown category
        
        matches = sum(1 for keyword in assigned_keywords if keyword in content_lower)
        confidence = min(1.0, matches / len(assigned_keywords) + 0.3)
        
        return confidence
    
    def _update_analytics(self, feedback_entry: Dict[str, Any], analysis_result: Dict[str, Any]):
        """Update feedback analytics"""
        try:
            timestamp = datetime.utcnow()
            analytics_entry = {
                "analytics_id": f"analytics_{timestamp.strftime('%Y%m%d')}",
                "date": timestamp.strftime('%Y-%m-%d'),
                "feedback_type": feedback_entry.get('feedback_type'),
                "category": feedback_entry.get('category'),
                "sentiment": analysis_result.get('sentiment', {}).get('label'),
                "rating": feedback_entry.get('rating'),
                "themes": analysis_result.get('themes', []),
                "priority": analysis_result.get('priority'),
                "actionable": analysis_result.get('actionable'),
                "updated_at": timestamp.isoformat()
            }
            
            # Store or update analytics
            self.analytics_table.put_item(Item=analytics_entry)
            
        except Exception as e:
            self.log_activity(
                "analytics_update_error",
                {"error": str(e)},
                "error"
            )
    
    def _generate_acknowledgment(self, feedback_type: str, rating: int = None) -> str:
        """Generate appropriate acknowledgment message"""
        if rating is not None:
            if rating <= 2:
                return "Thank you for your feedback. We take your concerns seriously and will review them promptly."
            elif rating >= 4:
                return "Thank you for your positive feedback! We're glad you're having a good experience."
            else:
                return "Thank you for your feedback. Your input helps us improve our services."
        
        acknowledgments = {
            "bug_report": "Thank you for reporting this issue. Our team will investigate and work on a resolution.",
            "feature_request": "Thank you for your suggestion. We'll consider this for future development.",
            "usability": "Thank you for your usability feedback. We're always working to improve the user experience.",
            "general": "Thank you for taking the time to provide feedback. Your input is valuable to us."
        }
        
        return acknowledgments.get(feedback_type, "Thank you for your feedback.")
    
    def get_feedback_analytics(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get feedback analytics with optional filtering"""
        try:
            if filters:
                # Apply filters (simplified for demo)
                response = self.feedback_table.scan()
            else:
                response = self.feedback_table.scan()
            
            feedback_items = response.get('Items', [])
            
            # Calculate analytics
            total_feedback = len(feedback_items)
            
            # Rating distribution
            ratings = [item.get('rating') for item in feedback_items if item.get('rating')]
            rating_avg = sum(ratings) / len(ratings) if ratings else 0
            
            # Sentiment distribution
            sentiments = {}
            themes = {}
            categories = {}
            
            for item in feedback_items:
                # Count sentiments (would need to re-analyze or store analysis results)
                category = item.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            return {
                "total_feedback": total_feedback,
                "average_rating": round(rating_avg, 2),
                "rating_distribution": self._calculate_rating_distribution(ratings),
                "category_distribution": categories,
                "generated_at": self._get_timestamp()
            }
            
        except Exception as e:
            self.log_activity(
                "analytics_retrieval_error",
                {"error": str(e)},
                "error"
            )
            return {}
    
    def _calculate_rating_distribution(self, ratings: List[int]) -> Dict[str, int]:
        """Calculate distribution of ratings"""
        distribution = {str(i): 0 for i in range(1, 6)}
        
        for rating in ratings:
            if 1 <= rating <= 5:
                distribution[str(rating)] += 1
        
        return distribution
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.utcnow().isoformat()