from db_config import get_connection
import mysql.connector

def create_users_table():
    """Create users table for storing registration data"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
        print("Table 'users' created successfully.")
    except mysql.connector.Error as err:
        print(f"Error creating users table: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_users_table()