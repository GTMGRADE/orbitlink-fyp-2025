-- YouTube Community Analysis Database Schema

-- 1. Store YouTube comments with community assignments
CREATE TABLE IF NOT EXISTS youtube_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    video_id VARCHAR(50) NOT NULL,
    comment_id VARCHAR(100) NOT NULL UNIQUE,
    thread_id VARCHAR(100),
    author_channel_id VARCHAR(100) NOT NULL,
    author_display_name VARCHAR(255),
    is_reply BOOLEAN DEFAULT FALSE,
    parent_comment_id VARCHAR(100),
    parent_author_id VARCHAR(100),
    like_count INT DEFAULT 0,
    total_reply_count INT DEFAULT 0,
    community_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_video (video_id),
    INDEX idx_author (author_channel_id),
    INDEX idx_community (community_id)
);

-- 2. Store detected communities
CREATE TABLE IF NOT EXISTS youtube_communities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    community_id INT NOT NULL,
    size INT DEFAULT 0,
    density DECIMAL(5, 4) DEFAULT 0,
    total_comments INT DEFAULT 0,
    total_likes INT DEFAULT 0,
    total_replies_given INT DEFAULT 0,
    total_replies_received INT DEFAULT 0,
    internal_connections INT DEFAULT 0,
    avg_comments_per_user DECIMAL(10, 2) DEFAULT 0,
    top_contributor_name VARCHAR(255),
    top_contributor_id VARCHAR(100),
    top_contributor_subs VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_project_community (project_id, community_id)
);

-- 3. Store community members
CREATE TABLE IF NOT EXISTS youtube_community_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    community_id INT NOT NULL,
    author_channel_id VARCHAR(100) NOT NULL,
    author_display_name VARCHAR(255),
    comment_count INT DEFAULT 0,
    replies_given INT DEFAULT 0,
    replies_received INT DEFAULT 0,
    likes_received INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_member (project_id, author_channel_id)
);

-- 4. Store network analysis metadata
CREATE TABLE IF NOT EXISTS youtube_analysis_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    channel_id VARCHAR(100),
    channel_url TEXT,
    total_videos_analyzed INT DEFAULT 0,
    total_comments INT DEFAULT 0,
    total_users INT DEFAULT 0,
    total_communities INT DEFAULT 0,
    modularity_score DECIMAL(5, 4),
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
