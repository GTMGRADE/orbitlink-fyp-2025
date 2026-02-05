"""
Seed script to initialize website_content collection in MongoDB
"""
import json
from db_config import get_connection

def seed_website_content():
    """Initialize website content in MongoDB"""
    db = get_connection()
    if db is None:
        print("Error: Could not connect to database")
        return False
    
    try:
        collection = db['website_content']
        
        # Check if collection already has data
        existing_count = collection.count_documents({})
        if existing_count > 0:
            print(f"Collection already has {existing_count} documents. Skipping seed.")
            return True
        
        # Define website content pages
        pages = [
            {
                "page_id": 1,
                "title": "Hero Section",
                "content": json.dumps({
                    "headline": "Analyze Social Networks with Smart Analytics",
                    "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
                })
            },
            {
                "page_id": 2,
                "title": "Key Features",
                "content": json.dumps([
                    {
                        "name": "Sentiment Analysis",
                        "description": "Analyze opinions and track sentiment shifts over time to understand public perception",
                        "icon": "📊"
                    },
                    {
                        "name": "Influencer Detection",
                        "description": "Identify key influencers and high-impact accounts driving conversations in your network",
                        "icon": "👑"
                    },
                    {
                        "name": "Community Clustering",
                        "description": "Detect subgroups and analyze information flows between different community segments",
                        "icon": "🔄"
                    },
                    {
                        "name": "Real-time Monitoring",
                        "description": "Track emergent events with live dashboards and instant alert notifications",
                        "icon": "⚡"
                    }
                ])
            },
            {
                "page_id": 3,
                "title": "Pricing",
                "content": json.dumps({
                    "plans": [
                        {"id": "free", "name": "Free Trial", "price": "0", "period": "/member for first month"},
                        {"id": "pro", "name": "Paid Subscription", "price": "49", "period": "/member/month"}
                    ],
                    "included": [
                        "Full access to all features for 30 days",
                        "Upload your own datasets",
                        "Run sentiment analysis, influencer detection",
                        "Create network visualizations",
                        "Export results (CSV, PNG, PDF)",
                        "Data backup & enhanced security"
                    ]
                })
            },
            {
                "page_id": 4,
                "title": "Contact Section",
                "content": json.dumps({
                    "email": "support@orbitlink.com",
                    "phone": "+1 (555) 123-4567",
                    "phone_hours": "Mon-Fri from 12pm to 6pm",
                    "response_time": "We reply within 24 hours",
                    "about_us": "Any Questions or remarks? Write us a message"
                })
            }
        ]
        
        # Insert pages
        result = collection.insert_many(pages)
        print(f"✓ Successfully seeded {len(result.inserted_ids)} website content pages")
        
        # Display what was inserted
        for page in collection.find():
            print(f"  - Page {page['page_id']}: {page['title']}")
        
        return True
        
    except Exception as e:
        print(f"Error seeding content: {e}")
        return False

if __name__ == "__main__":
    print("Starting website content seed...")
    success = seed_website_content()
    if success:
        print("✓ Seed completed successfully!")
    else:
        print("✗ Seed failed")
