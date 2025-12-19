import mysql.connector

def get_connection():
    # Skip database connection for now
    print("Database connection skipped (MySQL not configured)")
    return None

def init_db():
    """Create database and table if they don't exist"""
    # Skip database initialization for now
    print("Database initialization skipped (MySQL not configured)")
    return

# Initialize database when this module is imported
init_db()