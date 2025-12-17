from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Review:
    stars: str
    message: str
    username: str

    @staticmethod
    def get_reviews_dict_list() -> List[Dict[str, Any]]:
        """Returns sample reviews as a list of dictionaries."""
        return [
            {"stars": "⭐⭐⭐⭐⭐", "message": "Excellent platform for social network analysis!", "username": "User1"},
            {"stars": "⭐⭐⭐⭐⭐", "message": "Great features and easy to use interface.", "username": "User2"},
            {"stars": "⭐⭐⭐⭐", "message": "Very helpful for community detection and analysis.", "username": "User3"},
            {"stars": "⭐⭐⭐⭐⭐", "message": "Best tool for influencer tracking in the market.", "username": "User4"},
            {"stars": "⭐⭐⭐⭐⭐", "message": "Incredible sentiment analysis capabilities.", "username": "User5"},
            {"stars": "⭐⭐⭐⭐", "message": "Solid platform with good documentation.", "username": "User6"},
        ]
