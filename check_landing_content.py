"""Check current landing page content in database"""
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
    
    # Check current content
    current = db['website_content'].find_one({'page_id': 1})
    if current:
        print("Current content in database:")
        print(f"Page ID: {current.get('page_id')}")
        content = json.loads(current['content'])
        print(f"\nHeadline: {content.get('headline')}")
        print(f"\nDescription: {content.get('description')}")
    else:
        print("No content found for page_id 1")

if __name__ == '__main__':
    main()
