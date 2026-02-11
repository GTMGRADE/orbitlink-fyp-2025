# services/predictive_analysis.py
from datetime import datetime, timedelta
from db_config import get_connection
import statistics

class PredictiveAnalysisService:
    """Service for generating predictive insights based on historical analysis data"""
    
    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id
    
    def get_predictions(self):
        """Generate predictions based on historical YouTube analysis data"""
        print(f"[PREDICTIVE] Getting predictions for user={self.user_id}, project={self.project_id}")
        db = get_connection()
        if db is None:
            print(f"[PREDICTIVE] Database connection failed")
            return self._get_default_predictions()
        
        try:
            # Fetch all analyses for this project, sorted by date
            analyses = list(db.youtube_analysis.find(
                {"user_id": self.user_id, "project_id": self.project_id}
            ).sort("created_at", 1))  # Ascending order (oldest first)
            
            print(f"[PREDICTIVE] Found {len(analyses)} analyses for project {self.project_id}")
            
            if len(analyses) < 1:
                print(f"[PREDICTIVE] No analyses found, returning default predictions")
                return self._get_default_predictions()
            
            # Extract metrics from analyses
            metrics = []
            for analysis in analyses:
                data = analysis.get('analysis_data', {})
                metrics.append({
                    'date': analysis.get('created_at'),
                    'total_comments': data.get('total_comments', 0),
                    'videos_analyzed': data.get('videos_analyzed', 0),
                    'sentiment_score': data.get('sentiment_analysis', {}).get('overall_score', 0),
                    'influencers_count': len(data.get('influencers', [])),
                    'communities_count': data.get('community_detection', {}).get('num_communities', 0),
                    'analysis_type': data.get('analysis_type', 'unknown')
                })
            
            print(f"[PREDICTIVE] Extracted metrics from {len(metrics)} analyses")
            
            # Calculate trends and predictions
            engagement_trend = self._calculate_engagement_trend(metrics)
            sentiment_trend = self._calculate_sentiment_trend(metrics)
            growth_prediction = self._calculate_growth_prediction(metrics)
            upcoming_predictions = self._generate_upcoming_predictions(metrics, engagement_trend, sentiment_trend)
            
            print(f"[PREDICTIVE] Successfully generated predictions")
            
            return {
                'success': True,
                'has_data': True,
                'historical_count': len(analyses),
                'engagement_forecast': engagement_trend,
                'sentiment_trends': sentiment_trend,
                'growth_prediction': growth_prediction,
                'upcoming_predictions': upcoming_predictions,
                'last_analysis': analyses[-1].get('created_at').isoformat() if analyses else None
            }
            
        except Exception as e:
            print(f"[PREDICTIVE] Error generating predictions: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_predictions()
    
    def _calculate_engagement_trend(self, metrics):
        """Calculate engagement trend from historical data"""
        if len(metrics) < 2:
            return {
                'trend': 'stable',
                'percentage': 0,
                'confidence': 50,
                'description': 'Insufficient data for trend analysis'
            }
        
        # Calculate average comment count change
        comment_counts = [m['total_comments'] for m in metrics if m['total_comments'] > 0]
        
        if len(comment_counts) < 2:
            return {
                'trend': 'stable',
                'percentage': 0,
                'confidence': 50,
                'description': 'Not enough engagement data'
            }
        
        # Calculate percentage change from first to last
        first_avg = statistics.mean(comment_counts[:max(1, len(comment_counts)//3)])
        last_avg = statistics.mean(comment_counts[-max(1, len(comment_counts)//3):])
        
        if first_avg > 0:
            percentage_change = ((last_avg - first_avg) / first_avg) * 100
        else:
            percentage_change = 0
        
        # Determine trend
        if percentage_change > 10:
            trend = 'increasing'
            description = f'Engagement growing by approximately {abs(percentage_change):.1f}%'
        elif percentage_change < -10:
            trend = 'decreasing'
            description = f'Engagement declining by approximately {abs(percentage_change):.1f}%'
        else:
            trend = 'stable'
            description = 'Engagement levels remaining consistent'
        
        # Confidence based on data points
        confidence = min(50 + (len(metrics) * 10), 95)
        
        return {
            'trend': trend,
            'percentage': round(percentage_change, 1),
            'confidence': confidence,
            'description': description
        }
    
    def _calculate_sentiment_trend(self, metrics):
        """Calculate sentiment trend from historical data"""
        sentiment_scores = [m['sentiment_score'] for m in metrics]
        
        if len(sentiment_scores) < 2:
            return {
                'current_score': 0.0,
                'trend': 'neutral',
                'forecast': 0.0,
                'confidence': 50,
                'description': 'Insufficient data for sentiment prediction'
            }
        
        # Calculate average sentiment
        avg_sentiment = statistics.mean(sentiment_scores)
        
        # Calculate trend
        first_half = statistics.mean(sentiment_scores[:len(sentiment_scores)//2])
        second_half = statistics.mean(sentiment_scores[len(sentiment_scores)//2:])
        
        sentiment_change = second_half - first_half
        
        if sentiment_change > 0.05:
            trend = 'improving'
            forecast = min(second_half + sentiment_change, 1.0)
            description = 'Sentiment trending positive'
        elif sentiment_change < -0.05:
            trend = 'declining'
            forecast = max(second_half + sentiment_change, -1.0)
            description = 'Sentiment trending negative'
        else:
            trend = 'stable'
            forecast = second_half
            description = 'Sentiment remaining consistent'
        
        confidence = min(60 + (len(metrics) * 8), 92)
        
        return {
            'current_score': round(avg_sentiment, 2),
            'trend': trend,
            'forecast': round(forecast, 2),
            'confidence': confidence,
            'description': description
        }
    
    def _calculate_growth_prediction(self, metrics):
        """Predict growth rate based on historical data"""
        if len(metrics) < 2:
            return {
                'rate': 0,
                'timeframe': '30 days',
                'confidence': 45,
                'description': 'Need more data for growth prediction'
            }
        
        # Calculate average metrics growth
        comment_growth = []
        for i in range(1, len(metrics)):
            if metrics[i-1]['total_comments'] > 0:
                growth = ((metrics[i]['total_comments'] - metrics[i-1]['total_comments']) 
                         / metrics[i-1]['total_comments']) * 100
                comment_growth.append(growth)
        
        if not comment_growth:
            avg_growth = 0
        else:
            avg_growth = statistics.mean(comment_growth)
        
        # Project 30-day growth
        projected_growth = avg_growth * 2  # Rough projection
        
        confidence = min(55 + (len(metrics) * 7), 88)
        
        if projected_growth > 15:
            description = f'Strong growth expected: +{abs(projected_growth):.0f}% in 30 days'
        elif projected_growth > 5:
            description = f'Moderate growth expected: +{abs(projected_growth):.0f}% in 30 days'
        elif projected_growth < -5:
            description = f'Potential decline: {projected_growth:.0f}% in 30 days'
        else:
            description = 'Steady state expected with minimal change'
        
        return {
            'rate': round(projected_growth, 1),
            'timeframe': '30 days',
            'confidence': confidence,
            'description': description
        }
    
    def _generate_upcoming_predictions(self, metrics, engagement_trend, sentiment_trend):
        """Generate upcoming predictions for different timeframes"""
        predictions = []
        
        # Next week prediction
        engagement_pct = engagement_trend['percentage']
        predictions.append({
            'timeframe': 'Next Week',
            'prediction': f'{abs(engagement_pct):.0f}% {"increase" if engagement_pct > 0 else "decrease"} in engagement expected',
            'confidence': engagement_trend['confidence'],
            'type': 'engagement'
        })
        
        # 2 weeks prediction
        if len(metrics) >= 2:
            predictions.append({
                'timeframe': 'Next 2 Weeks',
                'prediction': 'Peak activity on weekends' if len(metrics) >= 3 else 'Consistent activity pattern expected',
                'confidence': 75 if len(metrics) >= 3 else 65,
                'type': 'pattern'
            })
        
        # Monthly prediction
        sentiment_forecast = sentiment_trend['forecast']
        sentiment_current = sentiment_trend['current_score']
        sentiment_delta = sentiment_forecast - sentiment_current
        
        predictions.append({
            'timeframe': 'Next Month',
            'prediction': f'Sentiment trending {"positive" if sentiment_delta > 0 else "negative"} ({sentiment_delta:+.2f})',
            'confidence': sentiment_trend['confidence'],
            'type': 'sentiment'
        })
        
        return predictions
    
    def _get_default_predictions(self):
        """Return default predictions when no data is available"""
        return {
            'success': True,
            'has_data': False,
            'historical_count': 0,
            'engagement_forecast': {
                'trend': 'unknown',
                'percentage': 0,
                'confidence': 0,
                'description': 'Run YouTube analyses to enable predictions'
            },
            'sentiment_trends': {
                'current_score': 0.0,
                'trend': 'unknown',
                'forecast': 0.0,
                'confidence': 0,
                'description': 'No sentiment data available'
            },
            'growth_prediction': {
                'rate': 0,
                'timeframe': '30 days',
                'confidence': 0,
                'description': 'Insufficient historical data for growth prediction'
            },
            'upcoming_predictions': [
                {
                    'timeframe': 'Getting Started',
                    'prediction': 'Run multiple YouTube analyses to build your prediction model',
                    'confidence': 100,
                    'type': 'instruction'
                }
            ],
            'last_analysis': None
        }
