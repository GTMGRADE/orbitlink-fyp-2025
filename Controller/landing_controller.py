import logging

logger = logging.getLogger(__name__)

class LandingPageController:
    def get_landing_data(self):
        """
        For now, returns static data for the landing page.
        Later can be extended to fetch dynamic content like reviews, stats, etc.
        """
        logger.info("Fetching landing page data")
        return {
            'page_title': 'Social Network Analysis Platform',
            'description': 'Analyze social networks, detect communities, track influencers and measure sentiment with our powerful analytics platform.',
            'features': ['Sentiment Analysis', 'Influencer Detection', 'Community Clustering', 'Real-time Monitoring'],
            'has_data': False  # Placeholder for future dynamic data
        }