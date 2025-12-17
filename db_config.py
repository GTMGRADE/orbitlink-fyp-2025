import mysql.connector

def get_connection():
    # First, connect to MySQL and create the database/table
    init_db()
    
    # Then return connection to the database
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pass",
        database="orbitlink_db"
    )

def init_db():
    """Create database and table if they don't exist"""
    try:
        # Connect to MySQL without database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pass"
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS orbitlink_db")
        
        # Switch to database
        cursor.execute("USE orbitlink_db")
        
        # Create users table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role ENUM('influencer', 'business') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active'
        )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and table initialized successfully!")
        
    except mysql.connector.Error as err:
        print(f"Database initialization error: {err}")

# Initialize database when this module is imported
init_db()