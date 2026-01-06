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
            return True
            
        except Exception as e:
            print(f"Error saving analysis session: {e}")
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
            
            return session
            
        except Exception as e:
            print(f"Error getting analysis session: {e}")
            return None
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