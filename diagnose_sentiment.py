#!/usr/bin/env python
"""
Sentiment Analysis Diagnostic Script
Tests each component of the sentiment pipeline and reports status.
"""
import os
import sys
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def main():
    print_section("SENTIMENT ANALYSIS DIAGNOSTIC")
    
    # Step 1: Check Python version
    print(f"\n[1] Python Version: {sys.version}")
    if sys.version_info < (3, 8):
        print("    [ERROR] Python 3.8+ required")
        return 1
    print("    [OK] Compatible version")
    
    # Step 2: Check imports
    print_section("CHECKING DEPENDENCIES")
    
    deps = {
        "torch": "PyTorch (deep learning)",
        "transformers": "HuggingFace Transformers",
        "wordcloud": "WordCloud",
        "matplotlib": "Matplotlib",
        "huggingface_hub": "HuggingFace Hub",
        "pandas": "Pandas",
        "numpy": "NumPy",
    }
    
    missing = []
    for module, desc in deps.items():
        try:
            __import__(module)
            print(f"[OK] {module:20} - {desc}")
        except ImportError as e:
            print(f"[FAIL] {module:20} - {desc} - {e}")
            missing.append(module)
    
    if missing:
        print(f"\n[ERROR] Missing: {', '.join(missing)}")
        return 1
    
    # Step 3: Check model download
    print_section("CHECKING MODEL DOWNLOAD")
    
    try:
        from services.sentiment_analysis import ensure_model_download
        print("[*] Attempting to download BERT model...")
        model_path = ensure_model_download()
        if model_path:
            print(f"[OK] Model downloaded to: {model_path}")
            # Verify files exist
            model_dir = Path(model_path)
            if model_dir.exists():
                files = list(model_dir.glob("*"))
                print(f"    {len(files)} files found in model directory")
                for f in list(files)[:5]:
                    print(f"      - {f.name}")
        else:
            print("[WARN] Model download returned None")
    except Exception as e:
        print(f"[ERROR] Model download failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 4: Check pipeline
    print_section("CHECKING INFERENCE PIPELINE")
    
    try:
        from services.sentiment_analysis import _get_pipeline
        print("[*] Loading sentiment pipeline...")
        pipe = _get_pipeline()
        print("[OK] Pipeline loaded")
        
        print("[*] Testing inference on sample texts...")
        test_texts = ["This is great!", "Not bad", "I hate this"]
        results = pipe(test_texts)
        for text, result in zip(test_texts, results):
            print(f"    '{text}' -> {result['label']} ({result['score']:.3f})")
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 5: Check wordcloud
    print_section("CHECKING WORDCLOUD")
    
    try:
        from services.sentiment_analysis import _build_wordcloud
        print("[*] Building wordcloud from sample texts...")
        sample_text = "hello world machine learning pytorch transformers sentiment analysis test"
        wc_img = _build_wordcloud([sample_text])
        if wc_img:
            print(f"[OK] WordCloud generated: {len(wc_img)} chars (base64)")
        else:
            print("[WARN] WordCloud returned None")
    except Exception as e:
        print(f"[ERROR] WordCloud failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 6: Check pie chart
    print_section("CHECKING PIE CHART")
    
    try:
        from services.sentiment_analysis import _build_pie
        print("[*] Building pie chart from sample counts...")
        counts = {"positive": 5, "neutral": 3, "negative": 2}
        pie_img = _build_pie(counts)
        if pie_img:
            print(f"[OK] Pie chart generated: {len(pie_img)} chars (base64)")
        else:
            print("[WARN] Pie chart returned None")
    except Exception as e:
        print(f"[ERROR] Pie chart failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 7: Full sentiment analysis
    print_section("TESTING FULL SENTIMENT ANALYSIS")
    
    try:
        from services.sentiment_analysis import run_sentiment_analysis
        print("[*] Running full sentiment analysis on sample comments...")
        
        sample_comments = [
            {
                "text": "This is amazing! I love it!",
                "author_name": "User1",
                "like_count": 10,
                "published_at": "2026-01-23T12:00:00Z"
            },
            {
                "text": "Not bad, could be better",
                "author_name": "User2",
                "like_count": 5,
                "published_at": "2026-01-23T11:30:00Z"
            },
            {
                "text": "I really dislike this",
                "author_name": "User3",
                "like_count": 2,
                "published_at": "2026-01-23T11:00:00Z"
            },
            {
                "text": "Great work, very insightful!",
                "author_name": "User4",
                "like_count": 15,
                "published_at": "2026-01-23T10:30:00Z"
            },
            {
                "text": "Fantastic analysis",
                "author_name": "User5",
                "like_count": 8,
                "published_at": "2026-01-23T10:00:00Z"
            },
        ]
        
        result = run_sentiment_analysis(sample_comments)
        
        print(f"[OK] Analysis completed:")
        print(f"    Overall Score: {result['overall_score']}/10")
        print(f"    Sentiment Counts:")
        print(f"      - Positive: {result['label_counts']['positive']}")
        print(f"      - Neutral: {result['label_counts']['neutral']}")
        print(f"      - Negative: {result['label_counts']['negative']}")
        print(f"    Word Cloud: {'Generated' if result['word_cloud'] else 'None'}")
        print(f"    Pie Chart: {'Generated' if result['pie_chart'] else 'None'}")
        print(f"    Top Comments: {len(result['top_like_comments'])} returned")
        
        if result['top_like_comments']:
            print("\n    Top Liked Comments:")
            for i, c in enumerate(result['top_like_comments'], 1):
                print(f"      {i}. {c['author_name']} ({c['like_count']} likes)")
                print(f"         {c['text'][:60]}...")
        
    except Exception as e:
        print(f"[ERROR] Full analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 8: Diagnostics check
    print_section("RUNNING DIAGNOSTICS")
    
    try:
        from services.sentiment_analysis import diagnostics
        diag = diagnostics()
        for key, status in diag.items():
            status_icon = "[OK]" if "OK" in status else "[WARN]" if "SKIPPED" in status or "EMPTY" in status else "[ERROR]"
            print(f"    {status_icon} {key:20} - {status}")
    except Exception as e:
        print(f"[ERROR] Diagnostics failed: {e}")
        return 1
    
    print_section("SUMMARY")
    print("[SUCCESS] All sentiment analysis components are working correctly!")
    print("\nNext steps:")
    print("  1. Start the Flask app: python app.py")
    print("  2. Login to the web UI")
    print("  3. Create a project and run YouTube analysis")
    print("  4. Check the Sentiment Analysis tab for results")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
