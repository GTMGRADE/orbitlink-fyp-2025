# controller/registeredUser_controller/analysis_session_controller.py
import json
from datetime import datetime
from db_config import get_connection

class AnalysisSessionController:
    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id
    
    def save_analysis_session(self, channel_url, channel_title, analysis_data):
        """Save analysis session so it persists across page refreshes"""
        db = get_connection()
        if db is None:
            return False
        
        try:
            from datetime import datetime
            
            # Check if session already exists for this project
            existing = db.analysis_sessions.find_one({
                "user_id": self.user_id,
                "project_id": self.project_id
            })
            
            session_doc = {
                "user_id": self.user_id,
                "project_id": self.project_id,
                "channel_url": channel_url,
                "channel_title": channel_title,
                "analysis_data": analysis_data,
                "last_accessed": datetime.utcnow()
            }
            
            if existing:
                # Update existing session
                db.analysis_sessions.update_one(
                    {"_id": existing["_id"]},
                    {"$set": session_doc}
                )
            else:
                # Create new session
                session_doc["created_at"] = datetime.utcnow()
                db.analysis_sessions.insert_one(session_doc)
            
            return True
            
        except Exception as e:
            print(f"Error saving analysis session: {e}")
            return False
    
    def get_current_session(self):
        """Get current analysis session for this project"""
        db = get_connection()
        if db is None:
            return None
        
        try:
            session = db.analysis_sessions.find_one(
                {"user_id": self.user_id, "project_id": self.project_id},
                sort=[("last_accessed", -1)]
            )
            
            if session:
                session['id'] = str(session['_id'])
                del session['_id']
            
            return session
            
        except Exception as e:
            print(f"Error getting analysis session: {e}")
            return None
    
    def clear_session(self):
        """Clear analysis session for this project"""
        db = get_connection()
        if db is None:
            return False
        
        try:
            result = db.analysis_sessions.delete_many({
                "user_id": self.user_id,
                "project_id": self.project_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error clearing analysis session: {e}")
            return False