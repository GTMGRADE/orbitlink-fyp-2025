# controllers/admin_view_feedback_controller.py
from Entity.feedback_entity import FeedbackEntity

class AdminViewFeedbackController:
    def handle(self) -> list[dict]:
        """
        Return feedback list (empty list if none).

        Boundary responsibilities:
        - check session/admin auth
        - decide UI message if list is empty
        - jsonify/render the response
        """
        return FeedbackEntity.get_all_feedback()
