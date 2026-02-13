# controllers/admin_view_feedback_controller.py
from entity.review import Review

class AdminViewFeedbackController:
    def handle(self) -> dict:
        """
        Return feedback data with reviews list and statistics.

        Boundary responsibilities:
        - check session/admin auth
        - decide UI message if list is empty
        - jsonify/render the response
        """
        reviews = Review.get_all_active_reviews(limit=100)
        stats = Review.get_review_stats()
        
        return {
            'reviews': reviews,
            'stats': stats
        }
