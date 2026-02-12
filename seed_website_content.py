"""
Seed script to initialize website_content collection in MongoDB
Uses separate fields format (not JSON content field)
"""
from db_config import get_connection
from entity.landing_content import LandingContent

def seed_website_content():
    """Initialize website content in MongoDB using separate fields"""
    db = get_connection()
    if db is None:
        print("Error: Could not connect to database")
        return False
    
    try:
        collection = db['website_content']
        
        # Page 1 - Hero Section
        page1 = {
            'page_id': 1,
            'page_name': 'Hero Section',
            'headline': 'Social Network Analysis Platform',
            'description': 'Analyze social networks, detect communities, track influencers and measure sentiment with our powerful analytics platform.',
            'content_type': 'separate_fields',
            'content': '{}'
        }
        
        # Page 2 - Features Section
        page2 = {
            'page_id': 2,
            'page_name': 'Features Section',
            'features': [
                {
                    'name': 'Sentiment Analysis',
                    'description': 'Analyze opinions and track sentiment shifts over time to understand public perception'
                },
                {
                    'name': 'Influencer Detection',
                    'description': 'Identify key influencers and high-impact accounts driving conversations in your network'
                },
                {
                    'name': 'Community Clustering',
                    'description': 'Detect subgroups and analyze information flows between different community segments'
                },
                {
                    'name': 'Real-time Monitoring',
                    'description': 'Track emergent events with live dashboards and instant alert notifications'
                }
            ],
            'content_type': 'separate_fields',
            'content': '{}'
        }
        
        # Page 3 - Pricing Section
        page3 = {
            'page_id': 3,
            'page_name': 'Pricing Section',
            'plan_name': 'Free Trial',
            'plan_price': '0',
            'plan_period': '/member for first month',
            'features': [
                'Full access to all features for 30 days',
                'Upload your own datasets',
                'Run sentiment analysis, influencer detection',
                'Create network visualizations',
                'Export results (CSV, PNG, PDF)',
                'Data backup & enhanced security'
            ],
            'content_type': 'separate_fields',
            'content': '{}'
        }
        
        # Page 4 - Contact Section
        page4 = {
            'page_id': 4,
            'page_name': 'Contact Section',
            'email': 'support@orbitlink.com',
            'phone': '',
            'phone_hours': '',
            'response_time': 'We reply within 24 hours',
            'content_type': 'separate_fields',
            'content': '{}'
        }
        
        # Update/insert all pages
        for page in [page1, page2, page3, page4]:
            result = collection.update_one(
                {'page_id': page['page_id']},
                {'$set': page},
                upsert=True
            )
            status = 'inserted' if result.upserted_id else 'updated'
            print(f"  Page {page['page_id']} ({page['page_name']}): {status}")
        
        # Clear cache so changes are visible
        LandingContent.clear_cache()
        print("\n✓ Cache cleared")
        
        return True
        
    except Exception as e:
        print(f"Error seeding content: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Seeding website content with separate fields format...\n")
    success = seed_website_content()
    if success:
        print("\n✓ Seed completed successfully!")
    else:
        print("\n✗ Seed failed")
