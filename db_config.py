
import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  
            password='pass', 
            database='orbitlink' 
        )
        if connection.is_connected():
            print("Database connection successful get_connection()")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Create database and table if they don't exist"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  
            password='pass'  , 
            database='orbitlink'  
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            cursor.execute("CREATE DATABASE IF NOT EXISTS orbitlink")
            cursor.execute("USE orbitlink")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('influencer', 'business', 'admin') NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'active',
                    INDEX idx_email (email),
                    INDEX idx_username (username)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    session_token VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_token (session_token)
                )
            """)
            
            cursor.execute("SELECT id FROM users WHERE email = 'admin@example.com'")
            if not cursor.fetchone():
                # Using bcrypt hash for admin password
                admin_password = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'  # 'adminpass' hashed
                cursor.execute("""
                    INSERT INTO users (email, username, password, role) 
                    VALUES (%s, %s, %s, %s)
                """, ('admin@example.com', 'admin', admin_password, 'admin'))
            
            connection.commit()
            print("Database initialized successfully")
            
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

init_db()