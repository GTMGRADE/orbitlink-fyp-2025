#!/usr/bin/env python
"""Test full sentiment analysis flow including MongoDB storage"""
import sys
import json
from services.sentiment_analysis import run_sentiment_analysis
from db_config import get_connection
from datetime import datetime

# Test data
test_comments = [
    {"text": "Amazing product! Love it!", "author_name": "John", "like_count": 100, "published_at": "2025-01-20"},
    {"text": "Not great, disappointed", "author_name": "Jane", "like_count": 50, "published_at": "2025-01-21"},
    {"text": "It's okay, average quality", "author_name": "Bob", "like_count": 30, "published_at": "2025-01-22"},
    {"text": "Excellent service!", "author_name": "Alice", "like_count": 75, "published_at": "2025-01-23"},
    {"text": "Waste of money", "author_name": "Charlie", "like_count": 20, "published_at": "2025-01-24"},
]

print("[TEST] Step 1: Running sentiment analysis...")
sentiment_result = run_sentiment_analysis(test_comments)

print(f"\n[TEST] Step 2: Checking sentiment result...")
print(f"  Overall Score: {sentiment_result.get('overall_score')}")
print(f"  Pie Chart: {bool(sentiment_result.get('pie_chart'))} ({len(sentiment_result.get('pie_chart', ''))} bytes)")
print(f"  Word Cloud: {bool(sentiment_result.get('word_cloud'))} ({len(sentiment_result.get('word_cloud', ''))} bytes)")

print(f"\n[TEST] Step 3: Saving to MongoDB...")
db = get_connection()
if db is not None:
    # Create a test session document
    test_user_id = "test_user_123"
    test_project_id = "test_project_456"
    
    session_doc = {
        "user_id": test_user_id,
        "project_id": test_project_id,
        "channel_url": "https://youtube.com/test",
        "channel_title": "Test Channel",
        "analysis_data": {
            "sentiment_analysis": sentiment_result,
            "videos_analyzed": 1,
            "total_comments": len(test_comments),
        },
        "created_at": datetime.utcnow(),
        "last_accessed": datetime.utcnow()
    }
    
    # Insert into database
    result = db.analysis_sessions.insert_one(session_doc)
    doc_id = result.inserted_id
    print(f"  Inserted document with ID: {doc_id}")
    
    print(f"\n[TEST] Step 4: Retrieving from MongoDB...")
    retrieved_doc = db.analysis_sessions.find_one({"_id": doc_id})
    
    if retrieved_doc:
        print(f"  Document found!")
        retrieved_sentiment = retrieved_doc.get('analysis_data', {}).get('sentiment_analysis')
        
        if retrieved_sentiment:
            print(f"  Retrieved sentiment keys: {list(retrieved_sentiment.keys())}")
            print(f"  Pie Chart: {bool(retrieved_sentiment.get('pie_chart'))} ({len(retrieved_sentiment.get('pie_chart', ''))} bytes)")
            print(f"  Word Cloud: {bool(retrieved_sentiment.get('word_cloud'))} ({len(retrieved_sentiment.get('word_cloud', ''))} bytes)")
            
            # Verify data integrity
            if (retrieved_sentiment.get('pie_chart') == sentiment_result.get('pie_chart') and
                retrieved_sentiment.get('word_cloud') == sentiment_result.get('word_cloud')):
                print(f"\n[SUCCESS] Data integrity verified!")
                sys.exit(0)
            else:
                print(f"\n[ERROR] Data mismatch!")
                sys.exit(1)
        else:
            print(f"  ERROR: No sentiment data in retrieved document")
            sys.exit(1)
    else:
        print(f"  ERROR: Document not found")
        sys.exit(1)
else:
    print(f"  ERROR: Could not connect to database")
    sys.exit(1)
