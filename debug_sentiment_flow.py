#!/usr/bin/env python3
"""
診斷情感分析數據流程
Debug sentiment analysis data flow
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_data_flow():
    """測試從分析到前端的完整數據流"""
    print("\n" + "="*70)
    print(" 情感分析數據流程診斷")
    print("="*70)
    
    # 1. 測試 Session Controller
    print("\n[1] 測試 Session Controller...")
    try:
        from controller.registeredUser_controller.analysis_session_controller import AnalysisSessionController
        print("✓ AnalysisSessionController 導入成功")
        
        # 模擬保存數據
        test_user_id = 1
        test_project_id = 1
        
        controller = AnalysisSessionController(test_user_id, test_project_id)
        
        test_sentiment_data = {
            "overall_score": 7.5,
            "label_counts": {"positive": 50, "neutral": 30, "negative": 20},
            "word_cloud": "base64_test_data_here",
            "pie_chart": "base64_pie_chart_here",
            "top_like_comments": [
                {"author_name": "TestUser1", "like_count": 100, "text": "Great video!", "label": "positive", "score": 9.0}
            ]
        }
        
        test_analysis_data = {
            "sentiment_analysis": test_sentiment_data,
            "total_comments": 100,
            "analysis_type": "video"
        }
        
        success = controller.save_analysis_session(
            "https://youtube.com/test",
            "Test Video",
            test_analysis_data
        )
        
        if success:
            print("✓ 測試數據保存成功")
        else:
            print("✗ 數據保存失敗")
            return False
            
        # 讀取數據
        retrieved = controller.get_current_session()
        if retrieved:
            print("✓ 數據讀取成功")
            
            # 檢查結構
            if "analysis_data" in retrieved:
                print("✓ analysis_data 存在")
                
                if "sentiment_analysis" in retrieved["analysis_data"]:
                    print("✓ sentiment_analysis 存在")
                    sentiment = retrieved["analysis_data"]["sentiment_analysis"]
                    
                    # 驗證關鍵欄位
                    checks = {
                        "overall_score": "overall_score" in sentiment,
                        "word_cloud": "word_cloud" in sentiment,
                        "pie_chart": "pie_chart" in sentiment,
                        "top_like_comments": "top_like_comments" in sentiment
                    }
                    
                    for field, exists in checks.items():
                        status = "✓" if exists else "✗"
                        print(f"  {status} {field}: {exists}")
                    
                    if all(checks.values()):
                        print("\n✓ 所有必要欄位都存在")
                        print(f"  Overall Score: {sentiment.get('overall_score')}")
                        print(f"  Top Comments: {len(sentiment.get('top_like_comments', []))} 個")
                        return True
                    else:
                        print("\n✗ 缺少必要欄位")
                        return False
                else:
                    print("✗ sentiment_analysis 不存在於 analysis_data 中")
                    return False
            else:
                print("✗ analysis_data 不存在")
                return False
        else:
            print("✗ 無法讀取數據")
            return False
            
    except Exception as e:
        print(f"✗ Session Controller 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sentiment_module():
    """測試情感分析模組"""
    print("\n[2] 測試情感分析模組...")
    try:
        from services.sentiment_analysis import run_sentiment_analysis
        print("✓ sentiment_analysis 模組導入成功")
        
        test_comments = [
            {"text": "This is amazing!", "author_name": "User1", "like_count": 50},
            {"text": "Not bad", "author_name": "User2", "like_count": 20},
            {"text": "Terrible", "author_name": "User3", "like_count": 5}
        ]
        
        result = run_sentiment_analysis(test_comments)
        
        print("✓ 情感分析執行成功")
        print(f"  Overall Score: {result.get('overall_score')}")
        print(f"  Word Cloud: {'存在' if result.get('word_cloud') else '不存在'}")
        print(f"  Pie Chart: {'存在' if result.get('pie_chart') else '不存在'}")
        print(f"  Top Comments: {len(result.get('top_like_comments', []))} 個")
        
        return True
        
    except Exception as e:
        print(f"✗ 情感分析模組測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_model_location():
    """檢查模型位置"""
    print("\n[3] 檢查模型位置...")
    
    import pathlib
    home = pathlib.Path.home()
    cache_dir = home / ".cache" / "huggingface" / "hub"
    
    print(f"當前模型緩存位置: {cache_dir}")
    
    if cache_dir.exists():
        models = list(cache_dir.glob("models--*"))
        if models:
            print(f"✓ 找到 {len(models)} 個模型:")
            for model in models:
                print(f"  - {model.name}")
        else:
            print("✗ 沒有找到任何模型")
    else:
        print("✗ 緩存目錄不存在")
    
    # 建議新位置
    project_dir = pathlib.Path(__file__).parent
    suggested_model_dir = project_dir / "models" / "sentiment"
    print(f"\n建議模型位置: {suggested_model_dir}")

if __name__ == "__main__":
    print("\n開始診斷...")
    
    test_sentiment = test_sentiment_module()
    test_flow = test_data_flow()
    check_model_location()
    
    print("\n" + "="*70)
    print(" 診斷總結")
    print("="*70)
    print(f"情感分析模組: {'✓ 正常' if test_sentiment else '✗ 異常'}")
    print(f"數據流程: {'✓ 正常' if test_flow else '✗ 異常'}")
    print("\n如果兩項都正常，問題可能在前端模板或路由參數傳遞。")
