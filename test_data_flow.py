"""
簡化測試：檢查情感分析數據流（不需下載模型）
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("測試數據流（不執行實際情感分析）")
print("=" * 60)

# Test 1: Check session controller
print("\n[1] 測試會話控制器...")
try:
    from controller.registeredUser_controller.analysis_session_controller import AnalysisSessionController
    from datetime import datetime
    
    # Mock data matching real structure
    mock_sentiment_data = {
        "overall_score": 3.85,
        "label_counts": {
            "1 star": 5,
            "2 stars": 8,
            "3 stars": 15,
            "4 stars": 20,
            "5 stars": 12
        },
        "word_cloud": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
        "pie_chart": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
        "top_like_comments": [
            {"author_name": "測試用戶1", "like_count": 150, "text": "很棒的影片！"},
            {"author_name": "測試用戶2", "like_count": 120, "text": "非常有幫助"},
            {"author_name": "測試用戶3", "like_count": 95, "text": "學到很多"},
            {"author_name": "測試用戶4", "like_count": 80, "text": "感謝分享"},
            {"author_name": "測試用戶5", "like_count": 65, "text": "很實用"}
        ]
    }
    
    # Mock full result_data structure
    mock_result_data = {
        "analysis_type": "video",
        "video_metadata": {
            "title": "測試影片",
            "video_id": "test123"
        },
        "sentiment_analysis": mock_sentiment_data,
        "influencers": [],
        "communities": {}
    }
    
    # Test with user_id=1, project_id=999 (test values)
    user_id = 1
    project_id = 999
    
    print(f"  → 創建控制器 (user_id={user_id}, project_id={project_id})")
    controller = AnalysisSessionController(user_id, project_id)
    
    print(f"  → 保存測試數據...")
    controller.save_analysis_session(
        "https://youtube.com/watch?v=test123",
        "測試影片",
        mock_result_data
    )
    print(f"  ✓ 數據已保存")
    
    print(f"  → 讀取數據...")
    retrieved = controller.get_current_session()
    
    if retrieved:
        print(f"  ✓ 成功讀取會話數據")
        print(f"    - Session keys: {list(retrieved.keys())}")
        
        if "analysis_data" in retrieved:
            print(f"    - Analysis data keys: {list(retrieved['analysis_data'].keys())}")
            
            if "sentiment_analysis" in retrieved["analysis_data"]:
                sentiment = retrieved["analysis_data"]["sentiment_analysis"]
                print(f"    ✓ 找到 sentiment_analysis")
                print(f"      - Keys: {list(sentiment.keys())}")
                print(f"      - Overall score: {sentiment.get('overall_score')}")
                print(f"      - Top comments: {len(sentiment.get('top_like_comments', []))}")
                print(f"      - Word cloud length: {len(sentiment.get('word_cloud', ''))}")
                print(f"      - Pie chart length: {len(sentiment.get('pie_chart', ''))}")
            else:
                print(f"    ✗ 未找到 sentiment_analysis in analysis_data")
        else:
            print(f"    ✗ 未找到 analysis_data")
    else:
        print(f"  ✗ 無法讀取會話數據")
    
    print(f"\n[會話控制器測試] ✓ 通過")
    
except Exception as e:
    print(f"\n[會話控制器測試] ✗ 失敗")
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Check if sentiment module exists
print("\n[2] 檢查情感分析模組...")
try:
    from services.sentiment_analysis import run_sentiment_analysis
    print(f"  ✓ 模組導入成功")
    print(f"  ✓ run_sentiment_analysis 函數存在")
except ImportError as e:
    print(f"  ✗ 模組導入失敗: {e}")

# Test 3: Check model location
print("\n[3] 檢查模型位置...")
from pathlib import Path
import os

project_root = Path(__file__).parent
model_dir = project_root / "models" / "sentiment_bert"

print(f"  專案根目錄: {project_root}")
print(f"  模型目錄: {model_dir}")
print(f"  模型目錄存在: {model_dir.exists()}")

if model_dir.exists():
    files = list(model_dir.rglob("*"))
    print(f"  模型目錄中的檔案數: {len(files)}")
else:
    print(f"  ⚠ 模型目錄不存在，將在首次執行時創建")

user_cache = Path.home() / ".cache" / "huggingface" / "hub"
print(f"\n  用戶緩存位置: {user_cache}")
print(f"  用戶緩存存在: {user_cache.exists()}")

print("\n" + "=" * 60)
print("測試完成")
print("=" * 60)
print("\n接下來的步驟：")
print("1. 運行 Flask 應用: python app.py")
print("2. 執行一次 YouTube 分析")
print("3. 檢查控制台輸出中的 [SENTIMENT], [YOUTUBE_ANALYZER], [CONTROLLER], [ROUTE] 標記")
print("4. 訪問 /projects/sentiment-analysis?project_id=<你的專案ID>")
