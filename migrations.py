from db_config import get_connection
import mysql.connector

def create_analysis_tables():
    """Create tables for storing YouTube analysis results"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Table for storing analysis jobs
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
        
        # Table for storing influencers data - FIXED: Added backticks around `rank`
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
        
        # Table for storing channel metadata
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
        
        # Table for storing video data
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
        
        conn.commit()
        print("YouTube analysis tables created successfully")
        
    except mysql.connector.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_analysis_tables()