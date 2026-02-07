import sys
import unittest
from datetime import datetime
from services.sentiment_analysis import run_sentiment_analysis

class TestSentimentWorkflow(unittest.TestCase):
    def setUp(self):
        # Create 10 dummy comments with varying likes
        self.comments = []
        for i in range(10):
            self.comments.append({
                "text": f"This is comment number {i}. It has some sentiment.",
                "author_name": f"User{i}",
                "like_count": i * 10,  # Likes: 0, 10, 20, ..., 90
                "published_at": datetime.now().isoformat(),
                # These fields are expected by sentiment_analysis.py, 
                # although youtube_analyzer passes more fields, these are critical for display
            })
        
        # Add a specific high-like comment
        self.comments.append({
            "text": "This is the most liked comment! Amazing video!",
            "author_name": "SuperFan",
            "like_count": 999,
            "published_at": datetime.now().isoformat()
        })
        
        # Add another high-like comment
        self.comments.append({
            "text": "Second most liked comment. Great job.",
            "author_name": "FanTwo",
            "like_count": 888,
            "published_at": datetime.now().isoformat()
        })

    def test_top_comments_extraction(self):
        print("\n[TEST] Running full sentiment analysis flow...")
        
        # 1. Run Analysis
        result = run_sentiment_analysis(self.comments)
        
        # 2. Check Result Structure
        self.assertIn('overall_score', result)
        self.assertIn('label_counts', result)
        self.assertIn('word_cloud', result)
        self.assertIn('pie_chart', result)
        self.assertIn('top_like_comments', result)
        
        print(f"[OK] Result structure valid")
        print(f"Overall Score: {result['overall_score']}")
        
        # 3. Verify Chart Generation
        if result['word_cloud']:
            print(f"[OK] Word cloud generated ({len(result['word_cloud'])} chars)")
        else:
            print("[FAIL] Word cloud not generated")
            
        if result['pie_chart']:
            print(f"[OK] Pie chart generated ({len(result['pie_chart'])} chars)")
        else:
            print("[FAIL] Pie chart not generated")

        # 4. Verify Top 5 Comments Logic
        top_comments = result['top_like_comments']
        
        print("\n--- TOP 5 COMMENTS RETURNED ---")
        for i, c in enumerate(top_comments):
            print(f"{i+1}. {c['author_name']} - Likes: {c['like_count']} - Score: {c['score']}")
            
        # Check count
        self.assertEqual(len(top_comments), 5)
        
        # Check order (should be descending by likes)
        self.assertEqual(top_comments[0]['author_name'], "SuperFan")
        self.assertEqual(top_comments[0]['like_count'], 999)
        
        self.assertEqual(top_comments[1]['author_name'], "FanTwo")
        self.assertEqual(top_comments[1]['like_count'], 888)
        
        self.assertEqual(top_comments[2]['author_name'], "User9")
        self.assertEqual(top_comments[2]['like_count'], 90)
        
        # Verify fields passed through
        self.assertIn('text', top_comments[0])
        self.assertIn('score', top_comments[0])
        self.assertIn('label', top_comments[0])
        
        print("\n[SUCCESS] Top 5 comments extraction verified!")

if __name__ == '__main__':
    unittest.main()
