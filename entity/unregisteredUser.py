class Review:
    def __init__(self, id, username, rating, message, date):
        self.id = id
        self.username = username
        self.rating = rating
        self.message = message
        self.date = date
    
    @staticmethod
    def get_hardcoded_reviews():
        """Returns hardcoded reviews for prototype phase"""
        return [
            Review(
                id=1,
                username='username',
                rating=5,
                message='This app makes social network analysis much easier to understand. The visualisations are clean and very helpful.',
                date='2024-01-15'
            ),
            Review(
                id=2,
                username='username',
                rating=5,
                message='Really useful for analysing sentiment and identifying key influencers. The dashboard layout is simple and easy to navigate.',
                date='2024-01-20'
            ),
            Review(
                id=3,
                username='username',
                rating=5,
                message='Uploading data and running analysis is straightforward. Good tool for both beginners and advanced users.',
                date='2024-02-05'
            ),
            Review(
                id=4,
                username='username',
                rating=4,
                message='I like how the app shows trends and communities clearly. It helped me gain insights faster than manual analysis.',
                date='2024-02-10'
            ),
            Review(
                id=5,
                username='username',
                rating=5,
                message='The features are well-organised and practical for real projects. Progress indicators also make long analyses less confusing.',
                date='2024-02-15'
            ),
            Review(
                id=6,
                username='username',
                rating=5,
                message='Overall a solid platform for social media data analysis. Would recommend it for research and business insights.',
                date='2024-02-20'
            )
        ]
    
    @staticmethod
    def get_reviews_dict_list():
        """Returns reviews as list of dictionaries for easier template rendering"""
        reviews = Review.get_hardcoded_reviews()
        return [
            {
                'id': review.id,
                'username': review.username,
                'rating': review.rating,
                'stars': '★' * review.rating + '☆' * (5 - review.rating),
                'message': review.message,
                'date': review.date
            }
            for review in reviews
        ]
