import logging
import json
from entity.website_content_entity import WebsiteContentEntity
from entity.landing_content import LandingContent

logger = logging.getLogger(__name__)

class LandingPageController:
    def get_landing_data(self):
        """
        Fetch dynamic landing page content from database.
        """
        logger.info("Fetching landing page data from database")
        
        try:
            # Fetch Hero Section (page_id 1)
            hero_page = WebsiteContentEntity.get_content(1)
            hero_data = {}
            if hero_page and hero_page.get('content'):
                try:
                    hero_data = json.loads(hero_page['content'])
                except:
                    hero_data = {
                        "headline": "Social Network Analysis Platform",
                        "description": "Analyze social networks, detect communities, track influencers and measure sentiment with our powerful analytics platform."
                    }
            
            # Fetch Features (page_id 2)
            features_page = WebsiteContentEntity.get_content(2)
            features = []
            if features_page and features_page.get('content'):
                try:
                    features = json.loads(features_page['content'])
                except:
                    features = ['Sentiment Analysis', 'Influencer Detection', 'Community Clustering', 'Real-time Monitoring']
            
            # Fetch Pricing (page_id 3)
            pricing_page = WebsiteContentEntity.get_content(3)
            pricing = None
            if pricing_page and pricing_page.get('content'):
                try:
                    pricing = json.loads(pricing_page['content'])
                except:
                    pricing = None
            
            # Fetch Contact (page_id 4)
            contact_page = WebsiteContentEntity.get_content(4)
            contact_email = "support@analyticsplatform.com"
            about_us = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            if contact_page and contact_page.get('content'):
                try:
                    contact_data = json.loads(contact_page['content'])
                    contact_email = contact_data.get('email', contact_email)
                    about_us = contact_data.get('about_us', about_us)
                except:
                    pass
            
            return {
                'page_title': hero_data.get('headline', 'Social Network Analysis Platform'),
                'description': hero_data.get('description', 'Analyze social networks...'),
                'contact_email': contact_email,
                'about_us': about_us,
                'features': features,
                'pricing': pricing,
                'has_data': True
            }
        except Exception as e:
            logger.error(f"Error fetching landing data: {e}")
            # Fallback to defaults
            return {
                'page_title': 'Social Network Analysis Platform',
                'description': 'Analyze social networks, detect communities, track influencers and measure sentiment with our powerful analytics platform.',
                'features': ['Sentiment Analysis', 'Influencer Detection', 'Community Clustering', 'Real-time Monitoring'],
                'has_data': False
            }