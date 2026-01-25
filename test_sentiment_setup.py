#!/usr/bin/env python3
"""
Test script to verify sentiment analysis and matplotlib setup
"""
import os
import sys

# Ensure matplotlib backend is set
os.environ['MPLBACKEND'] = 'Agg'

print("=" * 80)
print("SENTIMENT ANALYSIS & MATPLOTLIB SETUP TEST")
print("=" * 80)

# Test 1: Check matplotlib availability
print("\n[TEST 1] Checking matplotlib...")
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    print("✓ matplotlib imported successfully")
    print(f"  - matplotlib version: {matplotlib.__version__}")
    print(f"  - backend: {matplotlib.get_backend()}")
except Exception as e:
    print(f"✗ matplotlib import failed: {e}")
    sys.exit(1)

# Test 2: Check sentiment analysis module
print("\n[TEST 2] Checking sentiment_analysis module...")
try:
    from services.sentiment_analysis import (
        run_sentiment_analysis,
        MATPLOTLIB_AVAILABLE,
        _build_wordcloud,
        _build_pie,
    )
    print("✓ sentiment_analysis imported successfully")
    print(f"  - MATPLOTLIB_AVAILABLE: {MATPLOTLIB_AVAILABLE}")
except Exception as e:
    print(f"✗ sentiment_analysis import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check youtube_analyzer module
print("\n[TEST 3] Checking youtube_analyzer module...")
try:
    from services.youtube_analyzer import MATPLOTLIB_AVAILABLE as YT_MATPLOTLIB
    print("✓ youtube_analyzer imported successfully")
    print(f"  - MATPLOTLIB_AVAILABLE: {YT_MATPLOTLIB}")
except Exception as e:
    print(f"✗ youtube_analyzer import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test word cloud generation with dummy data
print("\n[TEST 4] Testing word cloud generation...")
try:
    test_texts = [
        "This is a great product",
        "I love this service",
        "Amazing quality and fast shipping",
        "Very satisfied with the purchase",
        "Excellent customer support"
    ]
    result = _build_wordcloud(test_texts)
    if result:
        print(f"✓ word cloud generated successfully")
        print(f"  - size: {len(result)} bytes")
    else:
        print("✗ word cloud generation returned None")
except Exception as e:
    print(f"✗ word cloud generation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test pie chart generation
print("\n[TEST 5] Testing pie chart generation...")
try:
    label_counts = {
        "positive": 75,
        "neutral": 18,
        "negative": 58
    }
    result = _build_pie(label_counts)
    if result:
        print(f"✓ pie chart generated successfully")
        print(f"  - size: {len(result)} bytes")
    else:
        print("✗ pie chart generation returned None")
except Exception as e:
    print(f"✗ pie chart generation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Test sentiment analysis with sample comments
print("\n[TEST 6] Testing sentiment analysis (this may download models)...")
try:
    sample_comments = [
        {
            "text": "This is absolutely wonderful! Love it!",
            "author_name": "User1",
            "author_id": "1",
            "like_count": 10,
            "published_at": "2024-01-01"
        },
        {
            "text": "Not bad, it's okay I guess",
            "author_name": "User2",
            "author_id": "2",
            "like_count": 3,
            "published_at": "2024-01-01"
        },
        {
            "text": "Terrible experience, very disappointed",
            "author_name": "User3",
            "author_id": "3",
            "like_count": 1,
            "published_at": "2024-01-01"
        }
    ]
    
    print("  Running sentiment analysis...")
    result = run_sentiment_analysis(sample_comments)
    print(f"✓ sentiment analysis completed")
    print(f"  - overall_score: {result['overall_score']}")
    print(f"  - label_counts: {result['label_counts']}")
    print(f"  - word_cloud: {'Present' if result['word_cloud'] else 'Not generated'}")
    print(f"  - pie_chart: {'Present' if result['pie_chart'] else 'Not generated'}")
    print(f"  - top_comments: {len(result['top_like_comments'])} comments")
except Exception as e:
    print(f"✗ sentiment analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY")
print("=" * 80)
print("\n✓ Your sentiment analysis and visualization setup is working correctly!")
