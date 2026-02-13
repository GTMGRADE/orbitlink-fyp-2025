import logging
from db_config import get_connection
from datetime import datetime, timedelta
from bson import ObjectId

logger = logging.getLogger(__name__)

class MockPaymentController:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def activate_subscription(self):
        """Activate subscription for user (mark as subscribed)"""
        try:
            db = get_connection()
            if db is None:
                return False, "Database connection error"
            
            # Convert user_id to ObjectId
            try:
                query_id = ObjectId(self.user_id)
            except:
                query_id = self.user_id
            
            # Update user to mark as having active subscription
            result = db.users.update_one(
                {"_id": query_id},
                {"$set": {
                    "subscription_active": True,
                    "subscription_activated_at": datetime.utcnow(),
                    "subscription_type": "paid",
                    "free_trial_ends": datetime.utcnow() + timedelta(days=30)  # 30-day trial
                }}
            )
            
            if result.modified_count > 0:
                logger.info(f"Subscription activated for user: {self.user_id}")
                return True, "Subscription activated successfully"
            else:
                return False, "Failed to activate subscription"
                
        except Exception as e:
            logger.error(f"Error activating subscription: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_payment_page_data(self):
        """Get data for payment page"""
        return {
            'page_title': 'Activate Your Subscription - OrbitLink',
            'hero_text': 'Complete your subscription to access all features',
            'subscription_details': {
                'first_month_free': True,
                'monthly_price': 49,
                'currency': 'USD',
                'features': [
                    'Full access to all features',
                    'Upload your own datasets',
                    'Run sentiment analysis, influencer detection',
                    'Create network visualizations',
                    'Export results (CSV, PNG, PDF)',
                    'Data backup & enhanced security'
                ]
            }
        }
    
    def get_user_subscription_status(self):
        """Check if user already has active subscription"""
        try:
            db = get_connection()
            if db is None:
                return False
            
            # Convert user_id to ObjectId
            try:
                query_id = ObjectId(self.user_id)
            except:
                query_id = self.user_id
            
            user = db.users.find_one(
                {"_id": query_id},
                {"subscription_active": 1}
            )
            
            return user.get('subscription_active', False) if user else False
            
        except Exception as e:
            logger.error(f"Error checking subscription status: {str(e)}")
            return False
    
    def get_user_data(self):
        """Get user data for email sending"""
        try:
            db = get_connection()
            if db is None:
                return None
            
            # Convert user_id to ObjectId
            try:
                query_id = ObjectId(self.user_id)
            except:
                query_id = self.user_id
            
            user = db.users.find_one(
                {"_id": query_id},
                {"username": 1, "email": 1}
            )
            
            if user:
                return {
                    'username': user.get('username'),
                    'email': user.get('email')
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None