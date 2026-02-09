from db_config import get_connection
from datetime import datetime, timedelta
import json
import html


class LandingContent:
    # Class-level cache
    _cached_content = None
    _cache_timestamp = None
    _cache_duration = timedelta(minutes=10)  # Cache for 10 minutes
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
        # Check if cached content is still valid
        now = datetime.now()
        if (LandingContent._cached_content is not None and 
            LandingContent._cache_timestamp is not None and 
            now - LandingContent._cache_timestamp < LandingContent._cache_duration):
            print("✓ Using cached landing content (reduces DB reads)")
            return LandingContent._cached_content
        
        db = get_connection()
        if db is None:
            # If we have old cached content, use it even if expired
            if LandingContent._cached_content is not None:
                print("⚠ Database unavailable, using stale cache")
                return LandingContent._cached_content
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

            content = {
                'headline': headline or 'Social Network Analysis Platform',
                'description': description or 'Analyze social networks, detect communities, track influencers and measure sentiment with our powerful analytics platform.',
                'features': features,
                'pricing': pricing,
                'contact': contact,
                'current_year': str(datetime.now().year)
            }
            
            # Update cache
            LandingContent._cached_content = content
            LandingContent._cache_timestamp = now
            print("✓ Landing content fetched from DB and cached")
            return content
            
        except Exception as e:
            print(f"Error fetching landing content from database: {e}")
            # If we have old cached content, use it even if expired
            if LandingContent._cached_content is not None:
                print("⚠ Using stale cache due to DB error")
                return LandingContent._cached_content
            return LandingContent._get_fallback_content()

    @staticmethod
    def _get_fallback_content():
        """Fallback content when database is unavailable."""
        return {
            'headline': 'Social Network Analysis Platform',
            'description': 'Analyze social networks, detect communities, track influencers and measure sentiment with our powerful analytics platform.',
            'features': [
                {'name': 'Sentiment Analysis', 'description': 'Analyze opinions and track sentiment shifts'},
                {'name': 'Influencer Detection', 'description': 'Identify key influencers in your network'},
                {'name': 'Community Clustering', 'description': 'Detect subgroups and analyze information flows'},
                {'name': 'Real-time Monitoring', 'description': 'Track emergent events with live dashboards'}
            ],
            'pricing': {
                'plans': {
                    'free': {'name': 'Free Trial', 'price': '0', 'period': '/member for first month'},
                    'pro': {'name': 'Paid Subscription', 'price': '49', 'period': '/member/month'}
                }
            },
            'contact': {
                'email': 'support@orbitlink.com',
                'phone': '+1 (555) 123-4567',
                'phone_hours': 'Mon-Fri from 12pm to 6pm',
                'response_time': 'We reply within 24 hours',
                'about_us': 'Any Questions or remarks? Write us a message'
            },
            'current_year': str(datetime.now().year)
        }
    
    @staticmethod
    def clear_cache():
        """Manually clear the landing content cache. Call after content updates."""
        LandingContent._cached_content = None
        LandingContent._cache_timestamp = None
        print("✓ Landing content cache cleared")
    
    @staticmethod
    def get_cache_info():
        """Return cache status information for debugging."""
        if LandingContent._cached_content is None:
            return {"cached": False, "age": None, "expires_in": None}
        
        age = datetime.now() - LandingContent._cache_timestamp if LandingContent._cache_timestamp else None
        return {
            "cached": True,
            "age_seconds": age.total_seconds() if age else None,
            "expires_in_seconds": (LandingContent._cache_duration - age).total_seconds() if age else None
        }
