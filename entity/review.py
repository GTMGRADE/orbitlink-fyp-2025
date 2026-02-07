# entity/review.py
from datetime import datetime
from db_config import get_connection
from bson import ObjectId

class Review:
    def __init__(self, review_id=None, user_id=None, username=None, rating=None, 
                 comment=None, created_at=None, status='active'):
        self.review_id = review_id
        self.user_id = user_id
        self.username = username
        self.rating = rating
        self.comment = comment
        self.created_at = created_at
        self.status = status
    
    @staticmethod
    def create_review(user_id, username, rating, comment=None):
        """Create a new review in the database"""
        db = get_connection()
        if db is None:
            return None
        
        review_data = {
            "user_id": user_id,
            "username": username,
            "rating": rating,
            "comment": comment or "",
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        try:
            result = db.reviews.insert_one(review_data)
            return Review(
                review_id=str(result.inserted_id),
                user_id=user_id,
                username=username,
                rating=rating,
                comment=comment,
                created_at=review_data["created_at"]
            )
        except Exception as e:
            print(f"Error creating review: {e}")
            return None
    
    @staticmethod
    def get_all_active_reviews(limit=50):
        """Get all active reviews sorted by most recent"""
        db = get_connection()
        if db is None:
            return []
        
        try:
            reviews = list(db.reviews.find(
                {"status": "active"}
            ).sort("created_at", -1).limit(limit))
            
            formatted_reviews = []
            for review in reviews:
                formatted_reviews.append({
                    'id': str(review['_id']),
                    'user_id': review.get('user_id'),
                    'username': review.get('username', 'Anonymous'),
                    'rating': review.get('rating', 5),
                    'stars': '★' * review.get('rating', 5) + '☆' * (5 - review.get('rating', 5)),
                    'comment': review.get('comment', ''),
                    'date': review.get('created_at').strftime('%Y/%b/%d') if review.get('created_at') else 'N/A'
                })
            return formatted_reviews
        except Exception as e:
            print(f"Error fetching reviews: {e}")
            return []
    
    @staticmethod
    def get_review_stats():
        """Get review statistics for admin dashboard"""
        db = get_connection()
        if db is None:
            return {'average_rating': 0, 'total_reviews': 0, 'positive_percentage': 0}
        
        try:
            # Get all active reviews
            reviews = list(db.reviews.find({"status": "active"}))
            
            if not reviews:
                return {'average_rating': 0, 'total_reviews': 0, 'positive_percentage': 0}
            
            total_reviews = len(reviews)
            total_rating = sum(review.get('rating', 0) for review in reviews)
            average_rating = round(total_rating / total_reviews, 1)
            
            # Calculate positive feedback percentage (4-5 stars)
            positive_reviews = sum(1 for review in reviews if review.get('rating', 0) >= 4)
            positive_percentage = round((positive_reviews / total_reviews) * 100) if total_reviews > 0 else 0
            
            return {
                'average_rating': average_rating,
                'total_reviews': total_reviews,
                'positive_percentage': positive_percentage
            }
        except Exception as e:
            print(f"Error calculating review stats: {e}")
            return {'average_rating': 0, 'total_reviews': 0, 'positive_percentage': 0}
    
    @staticmethod
    def get_user_review(user_id):
        """Check if user has already submitted a review"""
        db = get_connection()
        if db is None:
            return None
        
        try:
            review = db.reviews.find_one({
                "user_id": user_id,
                "status": "active"
            })
            return review
        except Exception as e:
            print(f"Error fetching user review: {e}")
            return None