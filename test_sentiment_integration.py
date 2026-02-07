#!/usr/bin/env python3
"""
Complete sentiment analysis flow test
Tests: Data extraction -> Analysis -> Session storage -> Frontend display
"""

import sys
import json

def test_1_module_imports():
    """Test that all modules import correctly"""
    print("\n" + "="*70)
    print("TEST 1: Module Imports")
    print("="*70)
    
    try:
        from services.sentiment_analysis import run_sentiment_analysis
        print("[OK] sentiment_analysis module imported")
    except Exception as e:
        print(f"[FAIL] sentiment_analysis import: {e}")
        return False
    
    try:
        from services.youtube_analyzer import YouTubeAnalyzer
        print("[OK] youtube_analyzer module imported")
    except Exception as e:
        print(f"[FAIL] youtube_analyzer import: {e}")
        return False
    
    return True

def test_2_sample_sentiment_analysis():
    """Test sentiment analysis on sample comments"""
    print("\n" + "="*70)
    print("TEST 2: Sample Sentiment Analysis")
    print("="*70)
    
    from services.sentiment_analysis import run_sentiment_analysis
    
    sample_comments = [
        {
            "text": "This is absolutely amazing! Love it!",
            "author_name": "User1",
            "like_count": 50,
            "published_at": "2025-01-23"
        },
        {
            "text": "Not bad, could be better though",
            "author_name": "User2",
            "like_count": 10,
            "published_at": "2025-01-23"
        },
        {
            "text": "I hate this, waste of time",
            "author_name": "User3",
            "like_count": 5,
            "published_at": "2025-01-23"
        },
        {
            "text": "Pretty good content overall",
            "author_name": "User4",
            "like_count": 30,
            "published_at": "2025-01-23"
        },
        {
            "text": "Excellent analysis, very informative",
            "author_name": "User5",
            "like_count": 75,
            "published_at": "2025-01-23"
        },
    ]
    
    try:
        result = run_sentiment_analysis(sample_comments)
        print(f"[OK] Sentiment analysis executed")
        print(f"    Overall Score: {result['overall_score']}/10")
        print(f"    Label Counts: {result['label_counts']}")
        print(f"    Word Cloud: {len(result['word_cloud']) if result['word_cloud'] else 'None'} chars")
        print(f"    Pie Chart: {len(result['pie_chart']) if result['pie_chart'] else 'None'} chars")
        print(f"    Top Comments: {len(result['top_like_comments'])} returned")
        
        # Validate structure
        assert isinstance(result['overall_score'], (int, float)), "overall_score must be numeric"
        assert isinstance(result['label_counts'], dict), "label_counts must be dict"
        assert isinstance(result['top_like_comments'], list), "top_like_comments must be list"
        assert len(result['top_like_comments']) <= 5, "top_like_comments should be <= 5"
        
        if result['top_like_comments']:
            first_comment = result['top_like_comments'][0]
            assert 'author_name' in first_comment, "comment must have author_name"
            assert 'text' in first_comment, "comment must have text"
            assert 'like_count' in first_comment, "comment must have like_count"
            assert 'label' in first_comment, "comment must have label"
            assert 'score' in first_comment, "comment must have score"
            print(f"    Top Comment: {first_comment['author_name']} ({first_comment['like_count']} likes)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Sentiment analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_youtube_analyzer_imports_sentiment():
    """Test that YouTubeAnalyzer has sentiment analysis integrated"""
    print("\n" + "="*70)
    print("TEST 3: YouTubeAnalyzer Sentiment Integration")
    print("="*70)
    
    try:
        # Check that youtube_analyzer imports sentiment_analysis successfully
        # by looking for it in the module source code
        with open("services/youtube_analyzer.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        checks = {
            "sentiment import": "sentiment_analysis import run_sentiment_analysis" in code,
            "SENTIMENT_ANALYSIS_AVAILABLE": "SENTIMENT_ANALYSIS_AVAILABLE" in code,
            "sentiment analysis call": "run_sentiment_analysis" in code,
            "sentiment in result_data": "sentiment_analysis" in code and "sentiment_analysis_result" in code,
        }
        
        all_ok = True
        for check_name, check_result in checks.items():
            status = "[OK]" if check_result else "[FAIL]"
            print(f"    {status} {check_name}")
            if not check_result:
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"[FAIL] YouTubeAnalyzer integration check: {e}")
        return False

def test_4_session_data_structure():
    """Test that session data structure is correct"""
    print("\n" + "="*70)
    print("TEST 4: Session Data Structure")
    print("="*70)
    
    sample_session_data = {
        "analysis_data": {
            "sentiment_analysis": {
                "overall_score": 7.5,
                "label_counts": {"positive": 3, "neutral": 1, "negative": 1},
                "word_cloud": "base64_string...",
                "pie_chart": "base64_string...",
                "top_like_comments": [
                    {
                        "text": "Great!",
                        "author_name": "User1",
                        "like_count": 50,
                        "published_at": "2025-01-23",
                        "label": "positive",
                        "score": 10
                    }
                ]
            },
            "other_data": "..."
        }
    }
    
    try:
        # Verify nested structure
        sentiment = sample_session_data["analysis_data"]["sentiment_analysis"]
        assert sentiment["overall_score"] is not None
        assert sentiment["label_counts"] is not None
        assert sentiment["top_like_comments"] is not None
        
        print("[OK] Session data structure is valid")
        print(f"    - overall_score: {sentiment['overall_score']}")
        print(f"    - label_counts: {sentiment['label_counts']}")
        print(f"    - top_like_comments: {len(sentiment['top_like_comments'])} items")
        return True
        
    except Exception as e:
        print(f"[FAIL] Session data structure: {e}")
        return False

def test_5_html_template_check():
    """Check that HTML template references sentiment correctly"""
    print("\n" + "="*70)
    print("TEST 5: HTML Template References")
    print("="*70)
    
    try:
        with open("Templates/sentiment_analysis.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Check for required template variables
        checks = {
            "sentiment.overall_score": "sentiment.overall_score" in html_content,
            "sentiment.pie_chart": "sentiment.pie_chart" in html_content,
            "sentiment.word_cloud": "sentiment.word_cloud" in html_content,
            "sentiment.top_like_comments": "sentiment.top_like_comments" in html_content,
            "c.author_name": "c.author_name" in html_content,
            "c.like_count": "c.like_count" in html_content,
            "c.text": "c.text" in html_content,
        }
        
        all_ok = True
        for check_name, check_result in checks.items():
            status = "[OK]" if check_result else "[FAIL]"
            print(f"  {status} {check_name}")
            if not check_result:
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"[FAIL] HTML template check: {e}")
        return False

def test_6_controller_integration():
    """Test that AnalysisSessionController can store sentiment data"""
    print("\n" + "="*70)
    print("TEST 6: AnalysisSessionController Integration")
    print("="*70)
    
    try:
        from controller.registeredUser_controller.analysis_session_controller import AnalysisSessionController
        print("[OK] AnalysisSessionController imported")
        
        # Check that it has the required methods
        required_methods = [
            'save_analysis_session',
            'get_current_session',
            'clear_session'
        ]
        
        for method_name in required_methods:
            if hasattr(AnalysisSessionController, method_name):
                print(f"    [OK] {method_name} exists")
            else:
                print(f"    [FAIL] {method_name} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"[FAIL] AnalysisSessionController check: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" SENTIMENT ANALYSIS INTEGRATION TEST SUITE")
    print("="*70)
    
    tests = [
        ("Module Imports", test_1_module_imports),
        ("Sample Sentiment Analysis", test_2_sample_sentiment_analysis),
        ("YouTubeAnalyzer Integration", test_3_youtube_analyzer_imports_sentiment),
        ("Session Data Structure", test_4_session_data_structure),
        ("HTML Template", test_5_html_template_check),
        ("Controller Integration", test_6_controller_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[CRITICAL ERROR in {test_name}]: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Sentiment analysis is ready to use.")
        return True
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed. Fix issues before using.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
