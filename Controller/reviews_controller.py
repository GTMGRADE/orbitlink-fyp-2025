import logging
from entity.unregisteredUser import Review

logger = logging.getLogger(__name__)


class ReviewsController:
    def get_reviews(self):
        """
        Returns reviews data using the entity.
        """
        logger.info("Fetching reviews data")
        
        reviews_data = Review.get_reviews_dict_list()
        
        return {
            'page_title': 'Customer Reviews - OrbitLink',
            'reviews': reviews_data,
            'average_rating': 4.8,  # You can calculate this dynamically
            'total_reviews': len(reviews_data)
        }
