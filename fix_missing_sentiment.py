#!/usr/bin/env python3
"""
Fix missing sentiment analysis for existing YouTube analyses
This script re-runs sentiment analysis on stored analyses that are missing it
"""

from db_config import get_connection
from services.sentiment_analysis import run_sentiment_analysis
from datetime import datetime
import sys

def fix_missing_sentiment():
    """Find and fix analyses with missing sentiment data"""
    db = get_connection()
    if db is None:
        print("❌ Failed to connect to database")
        return False
    
    try:
        # Find all analyses
        print("🔍 Searching for analyses with missing sentiment data...")
        analyses = list(db.youtube_analysis.find({}))
        
        print(f"📊 Found {len(analyses)} total analyses")
        
        fixed_count = 0
        for analysis in analyses:
            analysis_id = analysis['_id']
            channel_title = analysis.get('channel_title', 'Unknown')
            analysis_data = analysis.get('analysis_data', {})
            
            # Check if sentiment analysis is missing or empty
            sentiment = analysis_data.get('sentiment_analysis')
            needs_fix = False
            
            if sentiment is None:
                print(f"\n⚠️  '{channel_title}' - No sentiment data found")
                needs_fix = True
            elif sentiment.get('overall_score', 0) == 0:
                print(f"\n⚠️  '{channel_title}' - Empty sentiment data (score=0)")
                needs_fix = True
            elif not sentiment.get('word_cloud'):
                print(f"\n⚠️  '{channel_title}' - Missing visualizations")
                needs_fix = True
            else:
                print(f"✅ '{channel_title}' - Sentiment OK")
                continue
            
            if needs_fix:
                # Extract comments from the analysis data
                comments = []
                
                # Try to find comments in various possible locations
                if 'influencers' in analysis_data:
                    # This is the newer format - we need to reconstruct comments
                    # For now, we'll mark this as needs manual intervention
                    print(f"   ⚠️  This analysis uses newer format - comments not directly accessible")
                    print(f"   💡 Recommendation: Re-run the analysis for this channel/video")
                    continue
                
                # Try analysis_sessions collection
                session = db.analysis_sessions.find_one({
                    'user_id': analysis['user_id'],
                    'project_id': analysis['project_id']
                })
                
                if session and 'analysis_data' in session:
                    session_data = session['analysis_data']
                    
                    # Try to extract comments from session data
                    # Comments might be in different formats
                    if isinstance(session_data.get('comments'), list):
                        comments = session_data['comments']
                    
                if not comments:
                    print(f"   ⚠️  No comments found - cannot regenerate sentiment")
                    print(f"   💡 Recommendation: Re-run the analysis for this channel/video")
                    continue
                
                # Re-run sentiment analysis
                print(f"   🔄 Re-running sentiment analysis on {len(comments)} comments...")
                try:
                    new_sentiment = run_sentiment_analysis(comments)
                    
                    # Update the analysis
                    analysis_data['sentiment_analysis'] = new_sentiment
                    
                    db.youtube_analysis.update_one(
                        {'_id': analysis_id},
                        {'$set': {
                            'analysis_data': analysis_data,
                            'updated_at': datetime.utcnow()
                        }}
                    )
                    
                    # Also update session if exists
                    if session:
                        session_data['sentiment_analysis'] = new_sentiment
                        db.analysis_sessions.update_one(
                            {'_id': session['_id']},
                            {'$set': {
                                'analysis_data': session_data,
                                'last_accessed': datetime.utcnow()
                            }}
                        )
                    
                    print(f"   ✅ Fixed! New score: {new_sentiment['overall_score']}/10")
                    fixed_count += 1
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    import traceback
                    traceback.print_exc()
        
        print(f"\n{'='*60}")
        print(f"✅ Fixed {fixed_count} analyses")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def list_analyses():
    """List all analyses with their sentiment status"""
    db = get_connection()
    if db is None:
        print("❌ Failed to connect to database")
        return
    
    try:
        analyses = list(db.youtube_analysis.find({}).sort('created_at', -1))
        
        print(f"\n{'='*80}")
        print(f"YOUTUBE ANALYSES - SENTIMENT STATUS")
        print(f"{'='*80}")
        
        for i, analysis in enumerate(analyses, 1):
            channel_title = analysis.get('channel_title', 'Unknown')
            created_at = analysis.get('created_at', 'Unknown')
            analysis_data = analysis.get('analysis_data', {})
            sentiment = analysis_data.get('sentiment_analysis', {})
            
            score = sentiment.get('overall_score', 0)
            has_wordcloud = bool(sentiment.get('word_cloud'))
            has_pie = bool(sentiment.get('pie_chart'))
            
            status = "✅" if score > 0 and has_wordcloud else "❌"
            
            print(f"\n{i}. {status} {channel_title}")
            print(f"   Created: {created_at}")
            print(f"   Score: {score}/10")
            print(f"   Word Cloud: {'Yes' if has_wordcloud else 'No'}")
            print(f"   Pie Chart: {'Yes' if has_pie else 'No'}")
        
        print(f"\n{'='*80}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_analyses()
    else:
        print(f"\n{'='*60}")
        print(f"FIX MISSING SENTIMENT ANALYSIS")
        print(f"{'='*60}\n")
        
        success = fix_missing_sentiment()
        
        if success:
            print("\n💡 Tip: Run 'python fix_missing_sentiment.py list' to see all analyses")
        
        sys.exit(0 if success else 1)
