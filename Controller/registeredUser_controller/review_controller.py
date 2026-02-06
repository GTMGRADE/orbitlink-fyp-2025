# Controller/registeredUser_controller/review_controller.py
import logging
from entity.review import Review

logger = logging.getLogger(__name__)

class ReviewController:
    def __init__(self, user_id=None, username=None):
        self.user_id = user_id
        self.username = username
    
    def submit_review(self, rating, comment=None):
        """Submit a new review"""
        try:
            # Validate rating
            rating = int(rating)
            if rating < 1 or rating > 5:
                return False, "Rating must be between 1 and 5 stars"
            
            # Check if user already submitted a review
            existing_review = Review.get_user_review(self.user_id)
            if existing_review:
                return False, "You have already submitted a review"
            
            # Create the review
            review = Review.create_review(
                user_id=self.user_id,
                username=self.username,
                rating=rating,
                comment=comment
            )
            
            if review:
                logger.info(f"Review submitted by user {self.username} (ID: {self.user_id})")
                return True, "Thank you for your review!"
            else:
                return False, "Failed to submit review. Please try again."
                
        except ValueError:
            return False, "Invalid rating value"
        except Exception as e:
            logger.error(f"Error submitting review: {e}")
            return False, "An error occurred while submitting your review"
    
    def get_review_page_data(self):
        """Get data for the review submission page"""
        return {
            'page_title': 'Rate Us - OrbitLink',
            'has_existing_review': Review.get_user_review(self.user_id) is not None
        }