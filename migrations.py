# from db_config import get_connection
# import mysql.connector

# def create_analysis_tables():
#     """Create tables for storing YouTube analysis results"""
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     try:
#         # Table for storing analysis jobs
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS youtube_analysis_jobs (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 user_id INT NOT NULL,
#                 channel_url VARCHAR(500) NOT NULL,
#                 channel_id VARCHAR(100),
#                 channel_name VARCHAR(255),
#                 status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
#                 progress INT DEFAULT 0,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 started_at TIMESTAMP NULL,
#                 completed_at TIMESTAMP NULL,
#                 result_data JSON,
#                 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
#             )
#         """)
        
#         # Table for storing influencers data - FIXED: Added backticks around `rank`
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS youtube_influencers (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 analysis_job_id INT NOT NULL,
#                 `rank` INT NOT NULL,
#                 author_id VARCHAR(100),
#                 author_name VARCHAR(255),
#                 total_score DECIMAL(5,2),
#                 engagement_score DECIMAL(5,2),
#                 network_score DECIMAL(5,2),
#                 quality_score DECIMAL(5,2),
#                 consistency_score DECIMAL(5,2),
#                 activity_score DECIMAL(5,2),
#                 responsiveness_score DECIMAL(5,2),
#                 total_comments INT,
#                 total_likes INT,
#                 replies_received INT,
#                 unique_videos INT,
#                 indegree INT,
#                 outdegree INT,
#                 channel_owner_replies INT,
#                 thread_starts INT,
#                 avg_sentiment DECIMAL(5,3),
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (analysis_job_id) REFERENCES youtube_analysis_jobs(id) ON DELETE CASCADE
#             )
#         """)
        
#         # Table for storing channel metadata
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS youtube_channel_metadata (
#                 analysis_job_id INT PRIMARY KEY,
#                 channel_title VARCHAR(255),
#                 description TEXT,
#                 subscriber_count INT,
#                 video_count INT,
#                 view_count BIGINT,
#                 country VARCHAR(100),
#                 engagement_rate DECIMAL(5,2),
#                 profile_image_url VARCHAR(500),
#                 topics JSON,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (analysis_job_id) REFERENCES youtube_analysis_jobs(id) ON DELETE CASCADE
#             )
#         """)
        
#         # Table for storing video data
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS youtube_videos_analysis (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 analysis_job_id INT NOT NULL,
#                 video_id VARCHAR(100),
#                 title VARCHAR(500),
#                 views INT,
#                 likes INT,
#                 comments INT,
#                 like_rate DECIMAL(5,2),
#                 comment_rate DECIMAL(5,2),
#                 published_at DATETIME,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                 FOREIGN KEY (analysis_job_id) REFERENCES youtube_analysis_jobs(id) ON DELETE CASCADE
#             )
#         """)
        
#         conn.commit()
#         print("YouTube analysis tables created successfully")
        
#     except mysql.connector.Error as e:
#         print(f"Error creating tables: {e}")
#         conn.rollback()
#     finally:
#         cursor.close()
#         conn.close()

# if __name__ == "__main__":
#     create_analysis_tables()

# migrations/add_analysis_sessions.py
from db_config import get_connection
import mysql.connector

def create_analysis_tables():
    """Create tables for storing YouTube analysis results and analysis sessions"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Table for storing analysis sessions (NEW)
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
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_project (user_id, project_id)
            )
        """)
        
        print("✅ analysis_sessions table created successfully")
        
        # Add index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_project 
            ON analysis_sessions (user_id, project_id)
        """)
        
        print("✅ Index created for analysis_sessions table")
        
        # Table for storing analysis jobs (EXISTING)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_analysis_jobs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                channel_url VARCHAR(500) NOT NULL,
                channel_id VARCHAR(100),
                channel_name VARCHAR(255),
                status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
                progress INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP NULL,
                completed_at TIMESTAMP NULL,
                result_data JSON,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        print("✅ youtube_analysis_jobs table created successfully")
        
        # Table for storing influencers data - FIXED: Added backticks around `rank` (EXISTING)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_influencers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                analysis_job_id INT NOT NULL,
                `rank` INT NOT NULL,
                author_id VARCHAR(100),
                author_name VARCHAR(255),
                total_score DECIMAL(5,2),
                engagement_score DECIMAL(5,2),
                network_score DECIMAL(5,2),
                quality_score DECIMAL(5,2),
                consistency_score DECIMAL(5,2),
                activity_score DECIMAL(5,2),
                responsiveness_score DECIMAL(5,2),
                total_comments INT,
                total_likes INT,
                replies_received INT,
                unique_videos INT,
                indegree INT,
                outdegree INT,
                channel_owner_replies INT,
                thread_starts INT,
                avg_sentiment DECIMAL(5,3),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_job_id) REFERENCES youtube_analysis_jobs(id) ON DELETE CASCADE
            )
        """)
        
        print("✅ youtube_influencers table created successfully")
        
        # Table for storing channel metadata (EXISTING)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_channel_metadata (
                analysis_job_id INT PRIMARY KEY,
                channel_title VARCHAR(255),
                description TEXT,
                subscriber_count INT,
                video_count INT,
                view_count BIGINT,
                country VARCHAR(100),
                engagement_rate DECIMAL(5,2),
                profile_image_url VARCHAR(500),
                topics JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_job_id) REFERENCES youtube_analysis_jobs(id) ON DELETE CASCADE
            )
        """)
        
        print("✅ youtube_channel_metadata table created successfully")
        
        # Table for storing video data (EXISTING)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_videos_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                analysis_job_id INT NOT NULL,
                video_id VARCHAR(100),
                title VARCHAR(500),
                views INT,
                likes INT,
                comments INT,
                like_rate DECIMAL(5,2),
                comment_rate DECIMAL(5,2),
                published_at DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_job_id) REFERENCES youtube_analysis_jobs(id) ON DELETE CASCADE
            )
        """)
        
        print("✅ youtube_videos_analysis table created successfully")
        
        # Add foreign key relationship between analysis_sessions and youtube_analysis_jobs (OPTIONAL)
        # This would require adding analysis_job_id to analysis_sessions table
        # Let's check if we need to add this column first
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'analysis_sessions' 
            AND COLUMN_NAME = 'analysis_job_id'
        """)
        
        has_analysis_job_id = cursor.fetchone()[0] > 0
        
        if not has_analysis_job_id:
            cursor.execute("""
                ALTER TABLE analysis_sessions 
                ADD COLUMN analysis_job_id INT NULL,
                ADD FOREIGN KEY (analysis_job_id) REFERENCES youtube_analysis_jobs(id) ON DELETE SET NULL
            """)
            print("✅ Added analysis_job_id column and foreign key to analysis_sessions")
        
        conn.commit()
        print("\n🎉 All analysis tables created/updated successfully!")
        
    except mysql.connector.Error as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_analysis_tables()