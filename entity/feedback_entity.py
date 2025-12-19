from datetime import datetime

class FeedbackEntity:
    """
    TEMPORARY feedback entity.

    Later will be connected to your MySQL feedback table.
    """

    def __init__(self, feedback_id: int, user_email: str,
                 rating: int, comment: str, created_at: datetime):
        self.feedback_id = feedback_id
        self.user_email = user_email
        self.rating = rating
        self.comment = comment
        self.created_at = created_at

    def to_dict(self) -> dict:
        """
        Convert feedback to a dict for JSON responses.
        """
        return {
            "id": self.feedback_id,
            "user_email": self.user_email,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def get_all_feedback(cls) -> list[dict]:
        """
        Get all feedback entries.

        TEMPORARY:
          - Returns a hardcoded list.
        LATER:
          - Replace with real SELECT * FROM feedback ... on MySQL.
        """
        dummy_list = [
            cls(
                feedback_id=1,
                user_email="user1@example.com",
                rating=5,
                comment="Great platform, very easy to use!",
                created_at=datetime(2025, 5, 6, 12, 0, 0),
            ),
            cls(
                feedback_id=2,
                user_email="user2@example.com",
                rating=3,
                comment="Useful, but UI can be improved.",
                created_at=datetime(2025, 6, 8, 15, 30, 0),
            ),
        ]

        return [f.to_dict() for f in dummy_list]
