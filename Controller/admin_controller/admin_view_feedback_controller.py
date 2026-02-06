# controllers/admin_view_feedback_controller.py (UPDATE)
from entity.review import Review

class AdminViewFeedbackController:
    def handle(self) -> dict:
        """
        Return feedback statistics and list.
        """
        reviews = Review.get_all_active_reviews()
        stats = Review.get_review_stats()
        
        return {
            'reviews': reviews,
            'stats': stats
        }