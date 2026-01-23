#!/usr/bin/env python
"""Comprehensive test to verify sentiment analysis chart generation and retrieval"""
import sys
from services.sentiment_analysis import run_sentiment_analysis
from db_config import get_connection
from datetime import datetime

print("=" * 80)
print("SENTIMENT ANALYSIS CHART TEST")
print("=" * 80)

# Test data
test_comments = [
    {"text": "Amazing product! Love it!", "author_name": "John", "like_count": 100, "published_at": "2025-01-20"},
    {"text": "Not great, disappointed", "author_name": "Jane", "like_count": 50, "published_at": "2025-01-21"},
    {"text": "It's okay, average quality", "author_name": "Bob", "like_count": 30, "published_at": "2025-01-22"},
]

test_user_id = "test_user_sentiment"
test_project_id = "test_project_sentiment"

print("\n[PHASE 1] 生成情感分析（Chart Generation）")
print("-" * 80)
sentiment_result = run_sentiment_analysis(test_comments)

print(f"\n✓ 整體分數: {sentiment_result.get('overall_score')}")
print(f"✓ 標籤計數: {sentiment_result.get('label_counts')}")
print(f"✓ 評論數: {len(sentiment_result.get('top_like_comments', []))}")

pie_chart_data = sentiment_result.get('pie_chart')
word_cloud_data = sentiment_result.get('word_cloud')

print(f"\n圖表生成結果:")
print(f"  Pie Chart: {'✓ 存在' if pie_chart_data else '✗ 缺失'}")
if pie_chart_data:
    print(f"    - 大小: {len(pie_chart_data)} 字節")
    print(f"    - 前50字: {pie_chart_data[:50]}...")
else:
    print(f"    [ERROR] Pie chart 為 None!")

print(f"  Word Cloud: {'✓ 存在' if word_cloud_data else '✗ 缺失'}")
if word_cloud_data:
    print(f"    - 大小: {len(word_cloud_data)} 字節")
    print(f"    - 前50字: {word_cloud_data[:50]}...")
else:
    print(f"    [ERROR] Word cloud 為 None!")

if not pie_chart_data or not word_cloud_data:
    print("\n[FAILED] 圖表生成失敗！")
    sys.exit(1)

print("\n[PHASE 2] 儲存到 MongoDB（Save to Database）")
print("-" * 80)
db = get_connection()
if db is None:
    print("[ERROR] 無法連接到數據庫")
    sys.exit(1)

print(f"✓ 已連接到數據庫")

try:
    # 清理舊的測試數據
    db.analysis_sessions.delete_many({
        "user_id": test_user_id,
        "project_id": test_project_id
    })
    print(f"✓ 清理了舊測試數據")
    
    # 準備文檔
    analysis_data = {
        "sentiment_analysis": sentiment_result,
        "videos_analyzed": 1,
        "total_comments": len(test_comments),
    }
    
    session_doc = {
        "user_id": test_user_id,
        "project_id": test_project_id,
        "channel_url": "https://youtube.com/test",
        "channel_title": "Test Channel",
        "analysis_data": analysis_data,
        "created_at": datetime.utcnow(),
        "last_accessed": datetime.utcnow()
    }
    
    print(f"\n準備保存文檔:")
    print(f"  - user_id: {test_user_id}")
    print(f"  - project_id: {test_project_id}")
    print(f"  - 文檔大小: {len(str(session_doc))} 字節")
    
    # 插入數據庫
    result = db.analysis_sessions.insert_one(session_doc)
    doc_id = result.inserted_id
    print(f"\n✓ 已插入數據庫，文檔ID: {doc_id}")
    
except Exception as e:
    print(f"\n[ERROR] 保存失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[PHASE 3] 從 MongoDB 檢索（Retrieve from Database）")
print("-" * 80)

try:
    retrieved_doc = db.analysis_sessions.find_one({
        "user_id": test_user_id,
        "project_id": test_project_id
    })
    
    if not retrieved_doc:
        print("[ERROR] 文檔不存在！")
        sys.exit(1)
    
    print(f"✓ 找到文檔")
    print(f"  - 文檔ID: {retrieved_doc['_id']}")
    print(f"  - 建立時間: {retrieved_doc.get('created_at')}")
    
    # 檢查 analysis_data
    analysis_data = retrieved_doc.get('analysis_data')
    if not analysis_data:
        print("[ERROR] 缺少 analysis_data！")
        sys.exit(1)
    
    print(f"\n✓ 找到 analysis_data")
    print(f"  - 鍵值: {list(analysis_data.keys())}")
    
    # 檢查 sentiment_analysis
    retrieved_sentiment = analysis_data.get('sentiment_analysis')
    if not retrieved_sentiment:
        print("[ERROR] 缺少 sentiment_analysis！")
        sys.exit(1)
    
    print(f"\n✓ 找到 sentiment_analysis")
    print(f"  - 鍵值: {list(retrieved_sentiment.keys())}")
    
    # 檢查圖表
    retrieved_pie = retrieved_sentiment.get('pie_chart')
    retrieved_wordcloud = retrieved_sentiment.get('word_cloud')
    
    print(f"\n檢索到的圖表:")
    print(f"  Pie Chart: {'✓ 存在' if retrieved_pie else '✗ 缺失'}")
    if retrieved_pie:
        print(f"    - 大小: {len(retrieved_pie)} 字節")
        print(f"    - 前50字: {retrieved_pie[:50]}...")
    else:
        print(f"    [ERROR] Pie chart 為 None!")
    
    print(f"  Word Cloud: {'✓ 存在' if retrieved_wordcloud else '✗ 缺失'}")
    if retrieved_wordcloud:
        print(f"    - 大小: {len(retrieved_wordcloud)} 字節")
        print(f"    - 前50字: {retrieved_wordcloud[:50]}...")
    else:
        print(f"    [ERROR] Word cloud 為 None!")
    
    # 驗證數據完整性
    print(f"\n[PHASE 4] 驗證數據完整性（Data Integrity）")
    print("-" * 80)
    
    if retrieved_pie == pie_chart_data:
        print(f"✓ Pie chart 數據完整")
    else:
        print(f"✗ Pie chart 數據不匹配！")
        print(f"  原始大小: {len(pie_chart_data)}")
        print(f"  檢索大小: {len(retrieved_pie) if retrieved_pie else 'None'}")
        sys.exit(1)
    
    if retrieved_wordcloud == word_cloud_data:
        print(f"✓ Word cloud 數據完整")
    else:
        print(f"✗ Word cloud 數據不匹配！")
        print(f"  原始大小: {len(word_cloud_data)}")
        print(f"  檢索大小: {len(retrieved_wordcloud) if retrieved_wordcloud else 'None'}")
        sys.exit(1)
    
    print(f"\n[PHASE 5] 驗證 Flask 路由取得數據（Route Retrieval）")
    print("-" * 80)
    
    # 模擬路由檢索邏輯
    from Controller.registeredUser_controller.analysis_session_controller import AnalysisSessionController
    
    session_controller = AnalysisSessionController(test_user_id, test_project_id)
    session_data = session_controller.get_current_session()
    
    if not session_data:
        print("[ERROR] 路由無法檢索會話數據！")
        sys.exit(1)
    
    print(f"✓ 路由成功檢索會話數據")
    
    route_sentiment = session_data.get("analysis_data", {}).get("sentiment_analysis")
    if not route_sentiment:
        print("[ERROR] 路由無法取得 sentiment_analysis！")
        sys.exit(1)
    
    print(f"✓ 路由成功取得 sentiment_analysis")
    
    route_pie = route_sentiment.get('pie_chart')
    route_wordcloud = route_sentiment.get('word_cloud')
    
    print(f"\n路由檢索的圖表:")
    print(f"  Pie Chart: {'✓ 存在' if route_pie else '✗ 缺失'}")
    if route_pie:
        print(f"    - 大小: {len(route_pie)} 字節")
    
    print(f"  Word Cloud: {'✓ 存在' if route_wordcloud else '✗ 缺失'}")
    if route_wordcloud:
        print(f"    - 大小: {len(route_wordcloud)} 字節")
    
    if not route_pie or not route_wordcloud:
        print(f"\n[FAILED] 路由無法正確檢索圖表！")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("[SUCCESS] 所有測試通過！圖表被正確生成、儲存和檢索")
    print("=" * 80)
    print("\n問題排查:")
    print("  ✓ 圖表生成: 工作正常")
    print("  ✓ 數據庫保存: 工作正常")
    print("  ✓ 數據檢索: 工作正常")
    print("  ✓ 路由檢索: 工作正常")
    print("\n如果頁面仍然看不到圖表，問題可能在:")
    print("  - Flask 模板渲染")
    print("  - HTML 基64 編碼格式")
    print("  - 瀏覽器緩存")
    print("=" * 80)
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n[ERROR] 檢索失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
