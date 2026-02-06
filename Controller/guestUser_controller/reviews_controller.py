# Controller/guestUser_controller/reviews_controller.py (UPDATE)
import logging
from entity.review import Review

logger = logging.getLogger(__name__)

class ReviewsController:
    def get_reviews(self):
        """
        Returns reviews data from database.
        """
        logger.info("Fetching reviews data from database")
        
        # Get reviews from database
        reviews_data = Review.get_all_active_reviews()
        stats = Review.get_review_stats()
        
        return {
            'page_title': 'Customer Reviews - OrbitLink',
            'reviews': reviews_data,
            'average_rating': stats['average_rating'],
            'total_reviews': stats['total_reviews']
        }