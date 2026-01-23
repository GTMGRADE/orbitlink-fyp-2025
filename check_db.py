from db_config import get_connection

def check_database():
    """Check database contents"""
    connection = get_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        print("\n=== USERS ===")
        cursor.execute("SELECT * FROM users")
        for user in cursor.fetchall():
            print(f"ID: {user['id']}, Email: {user['email']}, Username: {user['username']}, Role: {user['role']}, Status: {user['status']}")
        
        print("\n=== PROJECTS ===")
        cursor.execute("SELECT * FROM projects")
        for project in cursor.fetchall():
            print(f"ID: {project['id']}, User: {project['user_id']}, Name: {project['name']}, Archived: {project['archived']}")
        
        print("\n=== YOUTUBE ANALYSIS ===")
        cursor.execute("SELECT * FROM youtube_analysis")
        for analysis in cursor.fetchall():
            print(f"ID: {analysis['id']}, User: {analysis['user_id']}, Project: {analysis['project_id']}, Channel: {analysis['channel_title']}")
        
        cursor.close()
        connection.close()
    else:
        print("Failed to connect to database")

if __name__ == "__main__":
    check_database()
