# db_config.py
import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import Error
import sys

load_dotenv()

def get_connection():
    """Get database connection"""
    try:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")

        connection = mysql.connector.connect(
            host=db_host,
            port=int(db_port) if db_port else 3306,
            user=db_user,
            password=db_password,
            database=db_name,
            autocommit=False  # Explicit transaction control
        )

        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Create database and tables if they don't exist"""
    try:
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")

        # First connect without database to create it if needed
        connection = mysql.connector.connect(
            host=db_host,
            port=int(db_port) if db_port else 3306,
            user=db_user,
            password=db_password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'active'
                )
            """)
            print("✓ users table created/verified")
            
            # Create projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    last_opened DATE,
                    archived BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            print("✓ projects table created/verified")
            
            # Create youtube_analysis table
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
            print("✓ youtube_analysis table created/verified")
            
            # Create indexes for better performance
            try:
                cursor.execute("""
                    CREATE INDEX idx_youtube_analysis_user_project 
                    ON youtube_analysis (user_id, project_id)
                """)
                print("✓ Index created: idx_youtube_analysis_user_project")
            except:
                print("✓ Index already exists: idx_youtube_analysis_user_project")
            
            try:
                cursor.execute("""
                    CREATE INDEX idx_youtube_analysis_created_at 
                    ON youtube_analysis (created_at DESC)
                """)
                print("✓ Index created: idx_youtube_analysis_created_at")
            except:
                print("✓ Index already exists: idx_youtube_analysis_created_at")
            
            # Check if we need to add new columns to existing tables
            try:
                # Check if youtube_analysis table exists and has all columns
                cursor.execute("SHOW COLUMNS FROM youtube_analysis")
                existing_columns = [col[0] for col in cursor.fetchall()]
                required_columns = ['id', 'user_id', 'project_id', 'channel_url', 
                                  'channel_title', 'analysis_data', 'created_at']
                
                for col in required_columns:
                    if col not in existing_columns:
                        print(f"⚠ Warning: Column '{col}' missing from youtube_analysis table")
            except:
                pass
            
            connection.commit()
            print("\n✅ Database initialization completed successfully!")
            
    except Error as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def check_database_status():
    """Check database connection and table status"""
    conn = get_connection()
    if not conn:
        print("❌ Database connection failed")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check all required tables exist
        tables = ['users', 'projects', 'youtube_analysis']
        for table in tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if cursor.fetchone():
                print(f"✓ {table} table exists")
            else:
                print(f"❌ {table} table missing")
                return False
        
        # Check youtube_analysis table structure
        cursor.execute("DESCRIBE youtube_analysis")
        columns = cursor.fetchall()
        print(f"\n📊 youtube_analysis table has {len(columns)} columns")
        
        # Print column names
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        return True
        
    except Error as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Initialize database on import (safer approach)
# Comment this out if you want manual control
# init_db()

if __name__ == "__main__":
    # Command line interface for database management
    import argparse
    
    parser = argparse.ArgumentParser(description='Database management utilities')
    parser.add_argument('--init', action='store_true', help='Initialize database and tables')
    parser.add_argument('--check', action='store_true', help='Check database status')
    parser.add_argument('--reset', action='store_true', help='Reset database (WARNING: deletes all data)')
    
    args = parser.parse_args()
    
    if args.init:
        print("🚀 Initializing database...")
        init_db()
    elif args.check:
        print("🔍 Checking database status...")
        check_database_status()
    elif args.reset:
        confirm = input("⚠️ WARNING: This will DELETE ALL DATA. Type 'YES' to confirm: ")
        if confirm == 'YES':
            print("🗑️ Resetting database...")
            # Note: This is a simple reset - in production you'd want backup first
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            cursor = conn.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {os.getenv('DB_NAME')}")
            cursor.execute(f"CREATE DATABASE {os.getenv('DB_NAME')}")
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Database reset. Now run --init to recreate tables.")
        else:
            print("❌ Reset cancelled")
    else:
        print("Available commands:")
        print("  python db_config.py --init   Initialize database")
        print("  python db_config.py --check  Check database status")
        print("  python db_config.py --reset  Reset database (DANGEROUS!)")