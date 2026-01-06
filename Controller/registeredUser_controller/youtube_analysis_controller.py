# controller/registeredUser_controller/youtube_analysis_controller.py
import os
import json
from datetime import datetime
from services.youtube_analyzer import YouTubeAnalyzer
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
    
    def analyze_channel(self, channel_url):
        """Analyze YouTube channel and save results"""
        # Run analysis with progress updates
        result = self.analyze_channel_with_progress(channel_url)
        
        if 'error' in result:
            return {'success': False, 'error': result['error']}
        
        return {
            'success': True,
            'data': result['data']
        }
    
    def analyze_channel_with_progress(self, channel_url, progress_callback=None):
        """Analyze YouTube channel with progress updates"""
        try:
            # Resolve channel
            if progress_callback:
                progress_callback('Resolving channel URL...', 10)
            
            channel_id = self.analyzer.resolve_channel_id(channel_url)
            
            # Get channel metadata
            if progress_callback:
                progress_callback('Fetching channel information...', 20)
            
            channel_metadata = self.analyzer.get_channel_metadata(channel_id)
            if not channel_metadata:
                return {'error': 'Could not fetch channel metadata'}
            
            # Get recent videos
            if progress_callback:
                progress_callback('Collecting recent videos...', 30)
            
            videos_data = self.analyzer.get_channel_videos(channel_id, max_videos=30)
            
            if len(videos_data) == 0:
                return {'error': 'No videos found for analysis'}
            
            # Analyze comments from each video
            all_comments = []
            all_edges = []
            
            for i, video in enumerate(videos_data):
                if progress_callback:
                    progress = 30 + (i / len(videos_data)) * 50
                    progress_callback(f'Analyzing video {i+1}/{len(videos_data)}...', progress)
                
                comments, edges = self.analyzer.analyze_comments(video['video_id'], channel_id, max_comments=2000)
                all_comments.extend(comments)
                all_edges.extend(edges)
                
                # Add video ID to comments for tracking
                for comment in comments[-len(comments):]:
                    comment['video_id'] = video['video_id']
            
            # Calculate influencer scores
            if progress_callback:
                progress_callback('Calculating influencer scores...', 90)
            
            influencers = self.analyzer.calculate_influencer_scores(all_comments, all_edges, videos_data)
            
            # Prepare result data
            result_data = {
                'success': True,
                'channel_metadata': channel_metadata,
                'videos_analyzed': len(videos_data),
                'total_comments': len(all_comments),
                'influencers': influencers[:20],
                'analysis_time': datetime.now().isoformat()
            }
            
            # Save results
            self.save_analysis_result(channel_url, result_data)
            
            if progress_callback:
                progress_callback('Analysis complete!', 100)
            
            return {
                'success': True,
                'data': result_data
            }
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def save_analysis_result(self, channel_url, result):
        """Save analysis results to database"""
        conn = get_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Create analysis table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS youtube_analysis (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    project_id INT NOT NULL,
                    channel_url VARCHAR(500) NOT NULL,
                    channel_title VARCHAR(255),
                    analysis_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            
            # Insert analysis result
            cursor.execute("""
                INSERT INTO youtube_analysis (user_id, project_id, channel_url, channel_title, analysis_data)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                self.user_id,
                self.project_id,
                channel_url,
                result['channel_metadata']['title'],
                json.dumps(result)
            ))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error saving analysis: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def get_recent_analyses(self, limit=5):
        """Get recent analyses for this project"""
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, channel_url, channel_title, created_at 
                FROM youtube_analysis 
                WHERE user_id = %s AND project_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (self.user_id, self.project_id, limit))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Error fetching analyses: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_analysis_by_id(self, analysis_id):
        """Get specific analysis by ID"""
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM youtube_analysis 
                WHERE id = %s AND user_id = %s AND project_id = %s
            """, (analysis_id, self.user_id, self.project_id))
            
            result = cursor.fetchone()
            if result and result['analysis_data']:
                result['analysis_data'] = json.loads(result['analysis_data'])
            
            return result
            
        except Exception as e:
            print(f"Error fetching analysis: {e}")
            return None
        finally:
            cursor.close()
            conn.close()