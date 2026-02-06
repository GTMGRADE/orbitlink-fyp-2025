#!/usr/bin/env python3
"""
Direct model downloader for sentiment analysis.
This script downloads the BERT sentiment model directly to HuggingFace cache.
"""

import os
import sys

def main():
    print("[MODEL_DOWNLOAD] Starting sentiment model download...")
    print("[MODEL_DOWNLOAD] This will download ~600MB of model files.")
    
    try:
        from huggingface_hub import snapshot_download
        print("[OK] huggingface_hub imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import huggingface_hub: {e}")
        return False
    
    try:
        print("[MODEL_DOWNLOAD] Downloading nlptown/bert-base-multilingual-uncased-sentiment...")
        cache_dir = snapshot_download(
            "nlptown/bert-base-multilingual-uncased-sentiment",
            cache_dir=None,  # Use default HuggingFace cache (~/.cache/huggingface/hub/)
        )
        print(f"[SUCCESS] Model downloaded to: {cache_dir}")
        return True
    except Exception as e:
        print(f"[ERROR] Model download failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
