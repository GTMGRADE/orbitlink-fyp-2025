#!/usr/bin/env python
"""Test sentiment analysis chart generation"""
import sys
from services.sentiment_analysis import run_sentiment_analysis

# Test data with sample comments
test_comments = [
    {
        "text": "This is an amazing product! I love it so much!",
        "author_name": "John Doe",
        "like_count": 100,
        "published_at": "2025-01-20"
    },
    {
        "text": "Really disappointed with the quality. Not worth the money.",
        "author_name": "Jane Smith",
        "like_count": 50,
        "published_at": "2025-01-21"
    },
    {
        "text": "It's okay, nothing special. Average product.",
        "author_name": "Bob Johnson",
        "like_count": 30,
        "published_at": "2025-01-22"
    },
    {
        "text": "Excellent service and great customer support!",
        "author_name": "Alice Brown",
        "like_count": 75,
        "published_at": "2025-01-23"
    },
    {
        "text": "Not happy with this purchase. Waste of money.",
        "author_name": "Charlie Wilson",
        "like_count": 20,
        "published_at": "2025-01-24"
    },
]

print("[TEST] Running sentiment analysis on test comments...")
result = run_sentiment_analysis(test_comments)

print(f"\n[RESULTS]")
print(f"  Overall Score: {result.get('overall_score')}")
print(f"  Label Counts: {result.get('label_counts')}")
print(f"  Pie Chart: {bool(result.get('pie_chart'))} (size: {len(result.get('pie_chart', ''))} bytes)" )
print(f"  Word Cloud: {bool(result.get('word_cloud'))} (size: {len(result.get('word_cloud', ''))} bytes)")
print(f"  Top Comments: {len(result.get('top_like_comments', []))}")

for i, comment in enumerate(result.get('top_like_comments', []), 1):
    print(f"    {i}. {comment['author_name']} ({comment['like_count']} likes): {comment['text'][:50]}...")

if result.get('pie_chart') and result.get('word_cloud'):
    print("\n[SUCCESS] Both pie chart and word cloud generated successfully!")
    sys.exit(0)
else:
    print("\n[ERROR] One or both charts failed to generate")
    if not result.get('pie_chart'):
        print("  - Pie chart is missing")
    if not result.get('word_cloud'):
        print("  - Word cloud is missing")
    sys.exit(1)
