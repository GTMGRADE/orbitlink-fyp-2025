from db_config import get_connection
from datetime import datetime
import json
import html


class LandingContent:
    @staticmethod
    def _parse_content(raw):
        if raw is None:
            return None
        if isinstance(raw, str):
            # Unescape HTML entities that may have been introduced, repeat to handle double-escaped values
            try:
                s = raw
                for _ in range(3):
                    s2 = html.unescape(s)
                    if s2 == s:
                        break
                    s = s2
            except Exception:
                s = raw
            try:
                return json.loads(s)
            except Exception:
                return s
        return raw

    @staticmethod
    def get_content():
        """Return structured landing content built from website_content collection.

        Keys: `headline`, `description`, `features` (list of strings), `pricing` (dict), `contact` (dict), `current_year`
        """
        db = get_connection()
        if db is None:
            return LandingContent._get_fallback_content()

        try:
            pages = db['website_content'].find()
            content_map = {p['page_id']: LandingContent._parse_content(p.get('content')) for p in pages}

            # Hero (page_id 1)
            hero = content_map.get(1) or {}
            headline = hero.get('headline') if isinstance(hero, dict) else (hero if isinstance(hero, str) else None)
            description = hero.get('description') if isinstance(hero, dict) else None

            # Features (page_id 2)
            raw_features = content_map.get(2)
            features = []
            if isinstance(raw_features, list):
                for f in raw_features:
                    if isinstance(f, dict) and 'name' in f:
                        # Keep full feature object with name and description
                        features.append(f)
                    elif isinstance(f, str):
                        # If just a string, wrap it in a dict
                        features.append({'name': f, 'description': ''})
            elif isinstance(raw_features, str):
                # If raw string, split by lines and create feature objects
                features = [{'name': s.strip(), 'description': ''} for s in raw_features.split('\n') if s.strip()]

            # Pricing (page_id 3)
            raw_pricing = content_map.get(3)
            pricing = {}
            if isinstance(raw_pricing, dict):
                # Start with entire pricing object to preserve 'included' and other fields
                pricing = raw_pricing.copy()
                # Transform 'plans' array into a dict with id/name as keys
                if 'plans' in raw_pricing and isinstance(raw_pricing['plans'], list):
                    plans_dict = {}
                    for plan in raw_pricing['plans']:
                        pid = plan.get('id') or plan.get('name')
                        if pid:
                            plans_dict[pid] = {'name': plan.get('name'), 'price': plan.get('price'), 'period': plan.get('period')}
                    pricing['plans'] = plans_dict

            # Contact (page_id 4)
            contact = content_map.get(4) or {}

            return {
                'headline': headline or 'Social Network Analysis Platform',
                'description': description or 'Analyze social networks, detect communities, track influencers and measure sentiment with our powerful analytics platform.',
                'features': features,
                'pricing': pricing,
                'contact': contact,
                'current_year': str(datetime.now().year)
            }
        except Exception as e:
            print(f"Error fetching landing content from database: {e}")
            return LandingContent._get_fallback_content()

    @staticmethod
    def _get_fallback_content():
        return {
            'headline': 'Social Network Analysis Platform',
            'description': 'Analyze social networks, detect communities, track influencers and measure sentiment with our powerful analytics platform.',
            'features': ['Sentiment Analysis', 'Influencer Detection', 'Community Clustering', 'Real-time Monitoring'],
            'pricing': {'free': {'name': 'Free Trial', 'price': '0', 'period': '/member for first month'}, 'pro': {'name': 'Paid Subscription', 'price': '49', 'period': '/member/month'}},
            'contact': {'email': 'support@orbitlink.com', 'phone': '+1 (555) 123-4567', 'phone_hours': 'Mon-Fri from 12pm to 6pm', 'response_time': 'We reply within 24 hours', 'about_us': 'Any Questions or remarks? Write us a message'},
            'current_year': str(datetime.now().year)
        }