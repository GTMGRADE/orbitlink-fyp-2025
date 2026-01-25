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
<<<<<<< HEAD
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Create analysis_sessions table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    project_id INT NOT NULL,
                    channel_url VARCHAR(500) NOT NULL,
                    channel_title VARCHAR(255) NOT NULL,
                    analysis_data JSON,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            
            # Check if session already exists for this project
            cursor.execute("""
                SELECT id FROM analysis_sessions 
                WHERE user_id = %s AND project_id = %s
            """, (self.user_id, self.project_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing session
                cursor.execute("""
                    UPDATE analysis_sessions 
                    SET channel_url = %s, channel_title = %s, analysis_data = %s,
                        last_accessed = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (channel_url, channel_title, json.dumps(analysis_data), existing[0]))
            else:
                # Create new session
                cursor.execute("""
                    INSERT INTO analysis_sessions (user_id, project_id, channel_url, channel_title, analysis_data)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.user_id, self.project_id, channel_url, channel_title, json.dumps(analysis_data)))
            
            conn.commit()
=======
        db = get_connection()
        if db is None:
            return False
        
        try:
            from datetime import datetime
            
            # Verify sentiment_analysis is in the data
            if 'sentiment_analysis' in analysis_data:
                sa = analysis_data['sentiment_analysis']
                print(f"[SESSION_CONTROLLER] Saving sentiment analysis with pie_chart: {bool(sa.get('pie_chart'))}, word_cloud: {bool(sa.get('word_cloud'))}")
            
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
                print(f"[SESSION_CONTROLLER] Updated existing session for project {self.project_id}")
            else:
                # Create new session
                session_doc["created_at"] = datetime.utcnow()
                db.analysis_sessions.insert_one(session_doc)
                print(f"[SESSION_CONTROLLER] Created new session for project {self.project_id}")
            
>>>>>>> development
            return True
            
        except Exception as e:
            print(f"Error saving analysis session: {e}")
<<<<<<< HEAD
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def get_current_session(self):
        """Get current analysis session for this project"""
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM analysis_sessions 
                WHERE user_id = %s AND project_id = %s
                ORDER BY last_accessed DESC LIMIT 1
            """, (self.user_id, self.project_id))
            
            session = cursor.fetchone()
            if session and session['analysis_data']:
                session['analysis_data'] = json.loads(session['analysis_data'])
=======
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
                
                # Log sentiment data in session
                if 'analysis_data' in session and 'sentiment_analysis' in session['analysis_data']:
                    sa = session['analysis_data']['sentiment_analysis']
                    print(f"[SESSION_CONTROLLER] Retrieved session with sentiment analysis")
                    print(f"[SESSION_CONTROLLER]   pie_chart: {bool(sa.get('pie_chart'))}")
                    print(f"[SESSION_CONTROLLER]   word_cloud: {bool(sa.get('word_cloud'))}")
                    if sa.get('pie_chart'):
                        print(f"[SESSION_CONTROLLER]   pie_chart size: {len(sa.get('pie_chart', ''))} bytes")
                    if sa.get('word_cloud'):
                        print(f"[SESSION_CONTROLLER]   word_cloud size: {len(sa.get('word_cloud', ''))} bytes")
>>>>>>> development
            
            return session
            
        except Exception as e:
            print(f"Error getting analysis session: {e}")
            return None
<<<<<<< HEAD
        finally:
            cursor.close()
            conn.close()
    
    def clear_session(self):
        """Clear analysis session for this project"""
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM analysis_sessions 
                WHERE user_id = %s AND project_id = %s
            """, (self.user_id, self.project_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error clearing analysis session: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
=======
    
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
>>>>>>> development
