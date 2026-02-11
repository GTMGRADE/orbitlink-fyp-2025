import logging
from entity.landing_content import LandingContent

logger = logging.getLogger(__name__)


class LandingPageController:
    def get_landing_data(self):
        """Return landing content from DB via LandingContent helper."""
        logger.info("Fetching landing page data")
        try:
            data = LandingContent.get_content()
            print(f"[CONTROLLER] data keys: {data.keys()}")
            print(f"[CONTROLLER] pricing from data: {data.get('pricing')}")
            contact = data.get('contact') or {}
            return {
                'page_title': data.get('headline'),
                'description': data.get('description'),
                'features': data.get('features'),
                'pricing': data.get('pricing'),
                'contact_email': contact.get('email'),
                'contact_phone': contact.get('phone'),
                'contact_hours': contact.get('phone_hours'),
                'contact_response_time': contact.get('response_time'),
                'about_us': contact.get('about_us'),
                'has_data': True
            }
        except Exception as e:
            print(f"[CONTROLLER] ERROR: {e}")
            return {
                'page_title': 'Social Network Analysis Platform',
                'description': 'Analyze social networks, detect communities, track influencers and measure sentiment with our powerful analytics platform.',
                'features': [
                    {'name': 'Sentiment Analysis', 'description': 'Analyze opinions and track sentiment shifts over time to understand public perception'},
                    {'name': 'Influencer Detection', 'description': 'Identify key influencers and high-impact accounts driving conversations in your network'},
                    {'name': 'Community Clustering', 'description': 'Detect subgroups and analyze information flows between different community segments'},
                    {'name': 'Real-time Monitoring', 'description': 'Track emergent events with live dashboards and instant alert notifications'}
                ],
                'has_data': False
            }