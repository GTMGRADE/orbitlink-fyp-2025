"""
ASCII-only CLI test for sentiment analysis model and visuals.
Run: python test_sentiment_analysis.py
"""
import time
import json

print("[INFO] Starting sentiment analysis diagnostics...")
start = time.time()

res = {
    "import": "",
    "download": "",
    "pipeline": "",
    "inference": "",
    "wordcloud": "",
    "pie": "",
}

try:
    from services import sentiment_analysis as sa
    res["import"] = "PASS"
except Exception as e:
    res["import"] = f"FAIL: {e}"

if res["import"].startswith("PASS"):
    try:
        diag = sa.diagnostics()
        res["download"] = diag.get("model_download", "UNKNOWN")
        res["pipeline"] = diag.get("pipeline_infer", "UNKNOWN")
        res["wordcloud"] = diag.get("wordcloud", "UNKNOWN")
        res["pie"] = diag.get("pie_chart", "UNKNOWN")
    except Exception as e:
        res["download"] = f"FAIL: {e}"

# simple inference on sample comments
if res["pipeline"].startswith("OK"):
    comments = [
        {"text": "I love this video!", "author_name": "A", "like_count": 10},
        {"text": "Not good.", "author_name": "B", "like_count": 1},
        {"text": "It is fine.", "author_name": "C", "like_count": 5},
    ]
    try:
        out = sa.run_sentiment_analysis(comments)
        res["inference"] = "PASS" if out.get("overall_score", 0) > 0 else "FAIL: score zero"
        # store brief output
        summary = {
            "overall_score": out.get("overall_score"),
            "label_counts": out.get("label_counts"),
            "has_wordcloud": bool(out.get("word_cloud")),
            "has_pie": bool(out.get("pie_chart")),
            "top_like_comments_len": len(out.get("top_like_comments", [])),
        }
        print("[RESULT]", json.dumps(summary, ensure_ascii=True))
    except Exception as e:
        res["inference"] = f"FAIL: {e}"

print("[SUMMARY]")
for k, v in res.items():
    print(f"- {k}: {v}")
print(f"[INFO] Done in {time.time()-start:.2f}s")
