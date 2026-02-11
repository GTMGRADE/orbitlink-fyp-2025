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
                result = json.loads(s)
                print(f"[PARSE_CONTENT_SUCCESS] Parsed JSON,  keys: {result.keys() if isinstance(result, dict) else type(result)}")
                return result
            except Exception as e:
                print(f"[PARSE_CONTENT_FAIL] Could not parse as JSON: {str(e)[:60]}..., returning raw string")
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
            print("[CACHE] Using cached landing content (reduces DB reads)")
            return LandingContent._cached_content
        
        db = get_connection()
        if db is None:
            # If we have old cached content, use it even if expired
            if LandingContent._cached_content is not None:
                print("[WARNING] Database unavailable, using stale cache")
                return LandingContent._cached_content
            return LandingContent._get_fallback_content()

        try:
            pages_list = list(db['website_content'].find())
            pages = {p['page_id']: p for p in pages_list}

            # Hero (page_id 1)
            page1 = pages.get(1) or {}
            if page1.get('content_type') == 'separate_fields' or page1.get('headline'):
                # New separate fields format
                headline = page1.get('headline', '')
                description = page1.get('description', '')
            else:
                # Old JSON format
                hero = LandingContent._parse_content(page1.get('content')) or {}
                headline = hero.get('headline') if isinstance(hero, dict) else (hero if isinstance(hero, str) else '')
                description = hero.get('description') if isinstance(hero, dict) else ''

            # Features (page_id 2)
            page2 = pages.get(2) or {}
            features = []
            if page2.get('content_type') == 'separate_fields' or page2.get('features'):
                # New separate fields format
                raw_features = page2.get('features', [])
                for f in raw_features:
                    if isinstance(f, dict):
                        features.append(f)
                    elif isinstance(f, str):
                        features.append({'name': f, 'description': ''})
            else:
                # Old JSON format
                raw_features = LandingContent._parse_content(page2.get('content'))
                if isinstance(raw_features, list):
                    for f in raw_features:
                        if isinstance(f, dict) and 'name' in f:
                            features.append(f)
                        elif isinstance(f, str):
                            features.append({'name': f, 'description': ''})
                elif isinstance(raw_features, str):
                    features = [{'name': s.strip(), 'description': ''} for s in raw_features.split('\n') if s.strip()]
            
            # Pricing (page_id 3)
            page3 = pages.get(3) or {}
            pricing = {}
            
            if page3.get('content_type') == 'separate_fields' or page3.get('plan_name'):
                # New separate fields format
                print("[PRICING_DEBUG] Using SEPARATE FIELDS format")
                pricing = {
                    'plans': {
                        'free': {
                            'name': page3.get('plan_name', 'Free Trial'),
                            'price': page3.get('plan_price', '0'),
                            'period': page3.get('plan_period', '/member/month')
                        }
                    },
                    'included': page3.get('features', [])
                }
                print(f"[PRICING_DEBUG] Built pricing from separate fields: {pricing}")
            else:
                # Old JSON format
                raw_pricing = LandingContent._parse_content(page3.get('content'))
                if isinstance(raw_pricing, dict):
                    pricing = raw_pricing.copy()
                    print(f"[PRICING_DEBUG] Using JSON format (old)")
                    if 'plans' in raw_pricing:
                        if isinstance(raw_pricing['plans'], list):
                            plans_dict = {}
                            for plan in raw_pricing['plans']:
                                pid = plan.get('id') or plan.get('name')
                                if pid:
                                    plans_dict[pid] = {'name': plan.get('name'), 'price': plan.get('price'), 'period': plan.get('period')}
                            pricing['plans'] = plans_dict
                        elif isinstance(raw_pricing['plans'], dict):
                            pricing['plans'] = raw_pricing['plans']

            # Contact (page_id 4)
            page4 = pages.get(4) or {}
            if page4.get('content_type') == 'separate_fields' or page4.get('email'):
                # New separate fields format
                contact = {
                    'email': page4.get('email', 'support@orbitlink.com'),
                    'phone': page4.get('phone', '+1 (555) 123-4567'),
                    'phone_hours': page4.get('phone_hours', 'Mon-Fri from 12pm to 6pm'),
                    'response_time': page4.get('response_time', 'We reply within 24 hours'),
                    'about_us': page4.get('about_us', 'Any Questions or remarks? Write us a message')
                }
            else:
                # Old JSON format
                raw_contact = LandingContent._parse_content(page4.get('content')) or {}
                contact = raw_contact if isinstance(raw_contact, dict) else {}

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
            print("[OK] Landing content fetched from DB and cached")
            return content
            
        except Exception as e:
            print(f"Error fetching landing content from database: {e}")
            # If we have old cached content, use it even if expired
            if LandingContent._cached_content is not None:
                print("[WARNING] Using stale cache due to DB error")
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
        print("[OK] Landing content cache cleared")
    
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
