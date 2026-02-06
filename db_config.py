# db_config.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv
import sys

load_dotenv()

# Global MongoDB client and database
_mongo_client = None
_mongo_db = None

def get_connection():
    """Get MongoDB database connection (Firestore compatibility mode)"""
    global _mongo_client, _mongo_db
    
    try:
        if _mongo_client is None:
            connection_string = os.getenv("MONGODB_CONNECTION_STRING")
            db_name = os.getenv("MONGODB_DATABASE_NAME", "orbitlinkfyp")
            
            if not connection_string:
                print("Error: MONGODB_CONNECTION_STRING not found in environment")
                return None
            
            # Create MongoDB client
            _mongo_client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            
            # Test connection
            _mongo_client.admin.command('ping')
            _mongo_db = _mongo_client[db_name]
            print(f"✓ Connected to MongoDB/Firestore: {db_name}")
        
        return _mongo_db
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"Error connecting to MongoDB/Firestore: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def init_db():
    """Create collections and indexes if they don't exist"""
    try:
        db = get_connection()
        if db is None:
            print("❌ Failed to connect to database")
            sys.exit(1)
        
        # Create collections (MongoDB equivalent of tables)
        collections = ['users', 'projects', 'youtube_analysis', 'website_content']
        
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"✓ Created collection: {collection_name}")
            else:
                print(f"✓ Collection exists: {collection_name}")
        
        # Create indexes for users collection
        db.users.create_index("email", unique=True, name="idx_users_email")
        db.users.create_index("username", unique=True, name="idx_users_username")
        print("✓ Indexes created for users collection")
        
        # Create indexes for projects collection
        db.projects.create_index("user_id", name="idx_projects_user_id")
        db.projects.create_index([("user_id", 1), ("created_at", -1)], name="idx_projects_user_created")
        print("✓ Indexes created for projects collection")
        
        # Create indexes for youtube_analysis collection
        db.youtube_analysis.create_index([("user_id", 1), ("project_id", 1)], name="idx_youtube_user_project")
        db.youtube_analysis.create_index([("created_at", -1)], name="idx_youtube_created_at")
        print("✓ Indexes created for youtube_analysis collection")
        
        # Create indexes for website_content collection
        db.website_content.create_index("page_id", unique=True, name="idx_website_content_page_id")
        print("✓ Indexes created for website_content collection")
        
        print("\n✅ Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False



def check_database_status():
    """Check database connection and collection status"""
    db = get_connection()
    if db is None:
        print("❌ Database connection failed")
        return False
    
    try:
        # Check all required collections exist
        collections = ['users', 'projects', 'youtube_analysis', 'website_content']
        existing_collections = db.list_collection_names()
        
        for collection in collections:
            if collection in existing_collections:
                count = db[collection].count_documents({})
                print(f"✓ {collection} collection exists ({count} documents)")
            else:
                print(f"❌ {collection} collection missing")
                return False
        
        # Check indexes
        print("\n📊 youtube_analysis indexes:")
        indexes = db.youtube_analysis.list_indexes()
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

# Initialize database on import (safer approach)
# Comment this out if you want manual control
# init_db()

if __name__ == "__main__":
    # Command line interface for database management
    import argparse
    
    parser = argparse.ArgumentParser(description='Database management utilities')
    parser.add_argument('--init', action='store_true', help='Initialize database and collections')
    parser.add_argument('--check', action='store_true', help='Check database status')
    
    args = parser.parse_args()
    
    if args.init:
        print("🚀 Initializing database...")
        init_db()
    elif args.check:
        print("🔍 Checking database status...")
        check_database_status()
    else:
        print("Available commands:")
        print("  python db_config.py --init   Initialize database")
        print("  python db_config.py --check  Check database status")
