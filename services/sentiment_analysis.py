import base64
import warnings
import os
from pathlib import Path
from io import BytesIO
from typing import Optional, Dict, List

warnings.filterwarnings("ignore")

_MODEL_CACHE = {
    "pipeline": None,
    "wordcloud": None,
    "model_dir": None,
}

# 設定模型保存到專案資料夾
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "models" / "sentiment_bert"

def ensure_model_download() -> Optional[str]:
    """下載 Hugging Face 模型到專案的 models 資料夾
    Returns local path if successful, else None.
    """
    try:
        from huggingface_hub import snapshot_download
        
        # 創建模型目錄
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        
        path = snapshot_download(
            repo_id="nlptown/bert-base-multilingual-uncased-sentiment",
            cache_dir=str(MODEL_DIR),
            resume_download=True,
        )
        _MODEL_CACHE["model_dir"] = path
        return path
    except Exception as e:
        return None


def _get_pipeline():
    """Load transformers pipeline once and warm it up."""
    if _MODEL_CACHE["pipeline"] is not None:
        return _MODEL_CACHE["pipeline"]

    import torch
    from transformers import pipeline

    device = 0 if torch.cuda.is_available() else -1
    # Try explicit download first to avoid lazy fetch at first inference
    local_dir = ensure_model_download()
    model_id_or_path = local_dir or "nlptown/bert-base-multilingual-uncased-sentiment"
    try:
        pipe = pipeline(
            "sentiment-analysis",
            model=model_id_or_path,
            device=device,
        )
    except Exception as e:
        raise

    # Warm up to trigger model/tokenizer download and cache
    try:
        _ = pipe("This is great")
    except Exception as e:
        pass

    _MODEL_CACHE["pipeline"] = pipe
    return pipe


def _get_wordcloud():
    if _MODEL_CACHE["wordcloud"] is None:
        from wordcloud import WordCloud
        _MODEL_CACHE["wordcloud"] = WordCloud(width=800, height=400, background_color="white")
    return _MODEL_CACHE["wordcloud"]


def preload_sentiment_resources():
    """Ensure models and resources are downloaded before analysis."""
    try:
        ensure_model_download()
        _get_pipeline()
        _get_wordcloud()
    except Exception as e:
        pass


def _label_to_score(label: str) -> float:
    label = label.lower()
    if "star" in label:
        try:
            stars = int(label.split()[0])
            return stars * 2.0  # map 1-5 stars to 2-10 score
        except Exception:
            return 0.0
    if "positive" in label:
        return 8.0
    if "neutral" in label:
        return 5.0
    if "negative" in label:
        return 2.0
    return 0.0


def _label_to_bucket(label: str) -> str:
    label = label.lower()
    if "positive" in label or "4" in label or "5" in label:
        return "positive"
    if "neutral" in label or "3" in label:
        return "neutral"
    return "negative"


def _build_wordcloud(texts):
    if not texts:
        return None
    try:
        # Import matplotlib only when needed to avoid circular imports
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        
        wc = _get_wordcloud()
        wc.generate(" ".join(texts))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png", dpi=120, bbox_inches="tight", facecolor="white")
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)
        return encoded
    except Exception as e:
        return None


def _build_pie(label_counts):
    total = sum(label_counts.values())
    if total == 0:
        return None
    labels = ["Positive", "Neutral", "Negative"]
    sizes = [label_counts.get("positive", 0), label_counts.get("neutral", 0), label_counts.get("negative", 0)]
    colors = ["#2ecc71", "#f1c40f", "#e74c3c"]
    try:
        # Import matplotlib only when needed
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
        ax.axis("equal")
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format="png", dpi=120, bbox_inches="tight", facecolor="white")
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)
        return encoded
    except Exception as e:
        return None


def run_sentiment_analysis(comments):
    """Return overall score, word cloud, and top liked comments."""
    if not comments:
        return {
            "overall_score": 0,
            "label_counts": {"positive": 0, "neutral": 0, "negative": 0},
            "word_cloud": None,
            "pie_chart": None,
            "top_like_comments": [],
        }

    pipe = _get_pipeline()

    texts = []
    for c in comments:
        text = (c.get("text") or "").strip()
        if text:
            texts.append(text)
    if not texts:
        return {
            "overall_score": 0,
            "label_counts": {"positive": 0, "neutral": 0, "negative": 0},
            "word_cloud": None,
            "pie_chart": None,
            "top_like_comments": [],
        }

    try:
        predictions = pipe(texts, batch_size=16, truncation=True)
    except Exception as e:
        raise

    label_counts = {"positive": 0, "neutral": 0, "negative": 0}
    scores = []
    enriched = []

    for comment, pred in zip(comments, predictions):
        label = pred.get("label", "neutral")
        bucket = _label_to_bucket(label)
        score = _label_to_score(label)
        label_counts[bucket] += 1
        scores.append(score)
        enriched.append({
            "text": comment.get("text", ""),
            "author_name": comment.get("author_name", "Unknown"),
            "like_count": comment.get("like_count", 0),
            "published_at": comment.get("published_at"),
            "label": bucket,
            "score": score,
        })

    overall_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    word_cloud = _build_wordcloud(texts)
    pie_chart = _build_pie(label_counts)

    top_like_comments = sorted(enriched, key=lambda x: x.get("like_count", 0), reverse=True)[:5]

    result = {
        "overall_score": overall_score,
        "label_counts": label_counts,
        "word_cloud": word_cloud,
        "pie_chart": pie_chart,
        "top_like_comments": top_like_comments,
    }
    
    return result


# Preload at import time to ensure resources are ready
preload_sentiment_resources()


def diagnostics() -> Dict[str, str]:
    """Return a simple diagnostics map for troubleshooting."""
    status: Dict[str, str] = {}
    try:
        md = ensure_model_download()
        status["model_download"] = "OK" if md else "SKIPPED"
    except Exception as e:
        status["model_download"] = f"ERROR: {e}"
    try:
        pipe = _get_pipeline()
        _ = pipe(["test", "good", "bad"])
        status["pipeline_infer"] = "OK"
    except Exception as e:
        status["pipeline_infer"] = f"ERROR: {e}"
    try:
        wc = _get_wordcloud()
        _ = wc.generate("hello world")
        status["wordcloud"] = "OK"
    except Exception as e:
        status["wordcloud"] = f"ERROR: {e}"
    try:
        img = _build_pie({"positive": 1, "neutral": 1, "negative": 1})
        status["pie_chart"] = "OK" if img else "EMPTY"
    except Exception as e:
        status["pie_chart"] = f"ERROR: {e}"
    return status
