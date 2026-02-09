# controller/registeredUser_controller/youtube_analysis_controller.py
import os
import json
from datetime import datetime
from services.youtube_analyzer import YouTubeAnalyzer
from controller.registeredUser_controller.analysis_session_controller import AnalysisSessionController
from db_config import get_connection

class YouTubeAnalysisController:
    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id
        
        # Load YouTube API key from environment
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key not found in environment variables")
        
        self.analyzer = YouTubeAnalyzer(self.api_key)
    
    def analyze_youtube(self, input_url, progress_callback=None):
        """Analyze YouTube channel or video and save results"""
        try:
            # Run analysis with auto-detection
            result = self.analyzer.analyze(input_url, progress_callback)
            
            if result['success']:
                # Save results to database
                self.save_analysis_result(input_url, result['data'])
                
                # Save to session storage for immediate access
                self.save_to_session_storage(input_url, result['data'])
            
            return result
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def analyze_channel(self, channel_url, progress_callback=None):
        """Legacy method for channel analysis (backward compatibility)"""
        return self.analyzer.analyze_channel(channel_url, progress_callback)
    
    def analyze_video(self, video_url, progress_callback=None):
        """Legacy method for video analysis"""
        return self.analyzer.analyze_video(video_url, progress_callback)
    
    def save_analysis_result(self, input_url, result):
        """Save analysis results to database with project-specific storage"""
        db = get_connection()
        if db is None:
            return
        
        try:
            # Get title based on analysis type
            if result.get('analysis_type') == 'video':
                title = result.get('video_metadata', {}).get('title', 'Video Analysis')
                channel_title = result.get('video_metadata', {}).get('channel_title', 'Unknown')
            else:
                title = result.get('channel_metadata', {}).get('title', 'Channel Analysis')
                channel_title = title
            
            # Insert analysis result with project_id using MongoDB
            analysis_doc = {
                "user_id": self.user_id,
                "project_id": self.project_id,
                "channel_url": input_url,
                "channel_title": channel_title,
                "analysis_data": result,
                "created_at": datetime.utcnow()
            }
            
            db.youtube_analysis.insert_one(analysis_doc)
            print(f"Analysis saved to database for project_id: {self.project_id}")
            
        except Exception as e:
            print(f"Error saving analysis to database: {e}")
            import traceback
            traceback.print_exc()
    
    def save_to_session_storage(self, input_url, result_data):
        """Save analysis to session storage for immediate frontend access"""
        try:
            session_controller = AnalysisSessionController(self.user_id, self.project_id)
            
            # Get title based on analysis type
            if result_data.get('analysis_type') == 'video':
                title = result_data.get('video_metadata', {}).get('title', 'Video Analysis')
            else:
                title = result_data.get('channel_metadata', {}).get('title', 'Channel Analysis')
            
            session_controller.save_analysis_session(
                input_url,
                title,
                result_data
            )
            print(f"[CONTROLLER] Analysis saved to session storage for project_id: {self.project_id}")
        except Exception as e:
            print(f"[CONTROLLER] Error saving to session storage: {e}")
            import traceback
            traceback.print_exc()
    
    def get_recent_analyses(self, limit=5):
        """Get recent analyses for this specific project"""
        db = get_connection()
        if db is None:
            return []
        
        try:
            analyses = list(db.youtube_analysis.find(
                {"user_id": self.user_id, "project_id": self.project_id}
            ).sort("created_at", -1).limit(limit))
            
            # Convert ObjectId to string
            for analysis in analyses:
                analysis['id'] = str(analysis['_id'])
                del analysis['_id']
            
            print(f"Fetched {len(analyses)} analyses for project_id: {self.project_id}")
            return analyses
            
        except Exception as e:
            print(f"Error fetching analyses: {e}")
            return []
    
    def get_analysis_by_id(self, analysis_id):
        """Get specific analysis by ID, ensuring it belongs to this project"""
        db = get_connection()
        if db is None:
            return None
        
        try:
            from bson import ObjectId
            
            # Convert string ID to ObjectId
            try:
                query_id = ObjectId(analysis_id)
            except:
                query_id = analysis_id
            
            result = db.youtube_analysis.find_one({
                "_id": query_id,
                "user_id": self.user_id,
                "project_id": self.project_id
            })
            
            if result:
                result['id'] = str(result['_id'])
                del result['_id']
                print(f"Retrieved analysis {analysis_id} for project_id: {self.project_id}")
            
            return result
            
        except Exception as e:
            print(f"Error fetching analysis: {e}")
            return None
    
    def get_current_analysis_session(self):
        """Get current analysis session for this project"""
        try:
            session_controller = AnalysisSessionController(self.user_id, self.project_id)
            session_data = session_controller.get_current_session()
            if session_data:
                print(f"Retrieved session data for project_id: {self.project_id}")
            return session_data
        except Exception as e:
            print(f"Error getting session data: {e}")
            return None
    
    def clear_analysis_session(self):
        """Clear analysis session for this project"""
        try:
            session_controller = AnalysisSessionController(self.user_id, self.project_id)
            session_controller.clear_session()
            print(f"Cleared session data for project_id: {self.project_id}")
        except Exception as e:
            print(f"Error clearing session data: {e}")
    
    def get_all_project_analyses(self):
        """Get all analyses for this project (for project overview)"""
        db = get_connection()
        if db is None:
            return []
        
        try:
            analyses = list(db.youtube_analysis.find(
                {"user_id": self.user_id, "project_id": self.project_id}
            ).sort("created_at", -1))
            
            # Convert ObjectId to string and extract summary data
            for analysis in analyses:
                analysis['id'] = str(analysis['_id'])
                del analysis['_id']
                
                # Extract summary information from analysis_data
                if 'analysis_data' in analysis:
                    data = analysis['analysis_data']
                    analysis['videos_analyzed'] = data.get('videos_analyzed')
                    analysis['total_comments'] = data.get('total_comments')
            
            print(f"Fetched all {len(analyses)} analyses for project_id: {self.project_id}")
            return analyses
            
        except Exception as e:
            print(f"Error fetching all analyses: {e}")
            return []
