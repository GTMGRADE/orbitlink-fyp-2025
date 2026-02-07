"""Revert landing page description to original Lorem ipsum text"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_config import get_connection
import json

def main():
    db = get_connection()
    if db is None:
        print("❌ Could not connect to database")
        return
    
    # New SNA-focused description
    original_description = "Uncover hidden patterns in social networks through advanced graph analysis. Map relationships, identify influential nodes, and visualize community structures in YouTube ecosystems. Make strategic decisions backed by network science and community detection insights."
    
    # Update page_id 1 (hero section) with new text
    result = db['website_content'].update_one(
        {'page_id': 1},
        {'$set': {'content': json.dumps({
            'headline': 'Analyze Social Networks with Smart Analytics',
            'description': original_description
        })}},
        upsert=True
    )
    
    print(f"✅ Updated landing page with new SNA-focused description")
    print(f"   Matched: {result.matched_count}, Modified: {result.modified_count}")
    
    # Also update features (page_id 2) - change Real-time Monitoring to Predictive Analysis
    features = [
        {'name': 'Sentiment Analysis', 'description': 'Analyze opinions and track sentiment shifts over time to understand public perception'},
        {'name': 'Influencer Detection', 'description': 'Identify key influencers and high-impact accounts driving conversations in your network'},
        {'name': 'Community Clustering', 'description': 'Detect subgroups and analyze information flows between different community segments'},
        {'name': 'Predictive Analysis', 'description': 'Forecast trends and anticipate network behavior with advanced predictive modeling'}
    ]
    
    result2 = db['website_content'].update_one(
        {'page_id': 2},
        {'$set': {'content': json.dumps(features)}},
        upsert=True
    )
    
    print(f"✅ Updated features - changed to Predictive Analysis")
    print(f"   Matched: {result2.matched_count}, Modified: {result2.modified_count}")

if __name__ == '__main__':
    main()
