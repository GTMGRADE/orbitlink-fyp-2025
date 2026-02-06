# upload_to_mysql.py
import pandas as pd
import mysql.connector
from db_config import get_connection
import sys
from pathlib import Path

def upload_community_data_to_mysql(
    project_id: int,
    consolidated_csv_path: str = "CommunityCSV/consolidated_community_analysis.csv",
    communities_df: pd.DataFrame = None,
    channel_url: str = None,
    channel_id: str = None,
    modularity: float = None
):
    """
    Upload YouTube community detection results to MySQL database.
    
    Args:
        project_id: The project ID from your projects table
        consolidated_csv_path: Path to the consolidated CSV file
        communities_df: DataFrame with community statistics
        channel_url: YouTube channel URL analyzed
        channel_id: YouTube channel ID
        modularity: Modularity score from community detection
    """
    
    connection = get_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # 1. Load consolidated comments data
        print("📥 Loading consolidated CSV...")
        comments_df = pd.read_csv(consolidated_csv_path)
        
        print(f"Found {len(comments_df)} comments to upload")
        
        # 2. Upload comments
        print("⬆️  Uploading comments to database...")
        insert_comment_sql = """
            INSERT INTO youtube_comments 
            (project_id, video_id, comment_id, thread_id, author_channel_id, 
             author_display_name, is_reply, parent_comment_id, parent_author_id,
             like_count, total_reply_count, community_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                community_id = VALUES(community_id),
                like_count = VALUES(like_count)
        """
        
        comment_count = 0
        for _, row in comments_df.iterrows():
            cursor.execute(insert_comment_sql, (
                project_id,
                row.get('video_id'),
                row.get('comment_id'),
                row.get('thread_id'),
                row.get('author_channel_id'),
                row.get('author_display_name'),
                bool(row.get('is_reply', False)),
                row.get('parent_comment_id'),
                row.get('parent_author_id'),
                int(row.get('like_count', 0)),
                int(row.get('total_reply_count', 0)),
                int(row['community_id']) if pd.notna(row.get('community_id')) else None
            ))
            comment_count += 1
            
            if comment_count % 100 == 0:
                print(f"  Uploaded {comment_count}/{len(comments_df)} comments...")
        
        connection.commit()
        print(f"✅ Uploaded {comment_count} comments")
        
        # 3. Upload communities
        if communities_df is not None:
            print("⬆️  Uploading community statistics...")
            insert_community_sql = """
                INSERT INTO youtube_communities
                (project_id, community_id, size, density, total_comments, total_likes,
                 total_replies_given, total_replies_received, internal_connections,
                 avg_comments_per_user, top_contributor_name, top_contributor_id,
                 top_contributor_subs)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    size = VALUES(size),
                    density = VALUES(density),
                    total_comments = VALUES(total_comments)
            """
            
            for _, row in communities_df.iterrows():
                cursor.execute(insert_community_sql, (
                    project_id,
                    int(row['community_id']),
                    int(row['size']),
                    float(row['density']),
                    int(row['total_comments']),
                    int(row['total_likes']),
                    int(row['total_replies_given']),
                    int(row['total_replies_received']),
                    int(row['internal_connections']),
                    float(row['avg_comments_per_user']),
                    row['top_contributor'],
                    row['top_contributor_id'],
                    str(row.get('top_contributor_subs', 'unavailable'))
                ))
            
            connection.commit()
            print(f"✅ Uploaded {len(communities_df)} communities")
        
        # 4. Upload community members
        print("⬆️  Calculating and uploading community members...")
        member_stats = comments_df.groupby(['author_channel_id', 'community_id']).agg({
            'author_display_name': 'first',
            'comment_id': 'count',
            'like_count': 'sum'
        }).reset_index()
        
        member_stats.columns = ['author_channel_id', 'community_id', 'author_display_name', 
                                'comment_count', 'likes_received']
        
        insert_member_sql = """
            INSERT INTO youtube_community_members
            (project_id, community_id, author_channel_id, author_display_name,
             comment_count, likes_received)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                community_id = VALUES(community_id),
                comment_count = VALUES(comment_count),
                likes_received = VALUES(likes_received)
        """
        
        for _, row in member_stats.iterrows():
            if pd.notna(row['community_id']):
                cursor.execute(insert_member_sql, (
                    project_id,
                    int(row['community_id']),
                    row['author_channel_id'],
                    row['author_display_name'],
                    int(row['comment_count']),
                    int(row['likes_received'])
                ))
        
        connection.commit()
        print(f"✅ Uploaded {len(member_stats)} community members")
        
        # 5. Upload metadata
        print("⬆️  Uploading analysis metadata...")
        insert_metadata_sql = """
            INSERT INTO youtube_analysis_metadata
            (project_id, channel_id, channel_url, total_videos_analyzed,
             total_comments, total_users, total_communities, modularity_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_metadata_sql, (
            project_id,
            channel_id,
            channel_url,
            comments_df['video_id'].nunique(),
            len(comments_df),
            comments_df['author_channel_id'].nunique(),
            communities_df['community_id'].nunique() if communities_df is not None else 0,
            float(modularity) if modularity is not None else None
        ))
        
        connection.commit()
        print("✅ Uploaded analysis metadata")
        
        print("\n" + "="*70)
        print("🎉 ALL DATA SUCCESSFULLY UPLOADED TO MYSQL!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading data: {e}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()


def query_community_data(project_id: int):
    """Query and display uploaded community data."""
    connection = get_connection()
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    # Get analysis summary
    cursor.execute("""
        SELECT * FROM youtube_analysis_metadata 
        WHERE project_id = %s 
        ORDER BY analysis_date DESC 
        LIMIT 1
    """, (project_id,))
    
    metadata = cursor.fetchone()
    if metadata:
        print("\n" + "="*70)
        print("YOUTUBE ANALYSIS SUMMARY")
        print("="*70)
        print(f"Channel URL: {metadata['channel_url']}")
        print(f"Videos Analyzed: {metadata['total_videos_analyzed']}")
        print(f"Total Comments: {metadata['total_comments']}")
        print(f"Total Users: {metadata['total_users']}")
        print(f"Communities Found: {metadata['total_communities']}")
        print(f"Modularity Score: {metadata['modularity_score']}")
        print(f"Analysis Date: {metadata['analysis_date']}")
    
    # Get top communities
    cursor.execute("""
        SELECT community_id, size, density, total_comments, total_likes,
               top_contributor_name
        FROM youtube_communities
        WHERE project_id = %s
        ORDER BY size DESC
        LIMIT 5
    """, (project_id,))
    
    communities = cursor.fetchall()
    if communities:
        print(f"\nTop 5 Communities:")
        print("-"*70)
        for comm in communities:
            print(f"Community {comm['community_id']}: {comm['size']} members, "
                  f"{comm['total_comments']} comments, "
                  f"Top: {comm['top_contributor_name']}")
    
    cursor.close()
    connection.close()


if __name__ == "__main__":
    # Example usage:
    # 1. First create the tables using youtube_community_schema.sql
    # 2. Then run this script
    
    print("YouTube Community Data Upload Utility")
    print("="*70)
    
    # Get project ID (you should have this from your projects table)
    project_id = input("Enter Project ID: ").strip()
    
    if not project_id.isdigit():
        print("❌ Invalid project ID")
        sys.exit(1)
    
    project_id = int(project_id)
    
    # Check if consolidated CSV exists
    csv_path = "CommunityCSV/consolidated_community_analysis.csv"
    if not Path(csv_path).exists():
        print(f"❌ File not found: {csv_path}")
        print("Please run the community detection notebook first!")
        sys.exit(1)
    
    # Upload data
    success = upload_community_data_to_mysql(
        project_id=project_id,
        consolidated_csv_path=csv_path,
        # Note: You'll need to pass communities_df, channel_url, etc. from your notebook
        # or load them from the CSV/saved variables
    )
    
    if success:
        # Display summary
        query_community_data(project_id)
