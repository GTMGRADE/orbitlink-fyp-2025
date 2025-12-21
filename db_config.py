import mysql.connector
import os
from dotenv import load_dotenv

from mysql.connector import Error

load_dotenv()


def get_connection():
    try:

        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")

        print(db_host, db_port, db_name)

        # connection = mysql.connector.connect(
        #     host='localhost',
        #     user='root',  
        #     password='pass', 
        #     database='orbitlink' 
        # )

        connection = mysql.connector.connect(
           host=db_host,
           user=db_user,  
           password=db_password, 
           database=db_name
        )

        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    """Create database and table if they don't exist - SIMPLIFIED"""
    try:

        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")

        
        # connection = mysql.connector.connect(
        #     host='localhost',
        #     user='root',  
        #     password='pass', 
        #     database='orbitlink'  
        # )
        
        connection = mysql.connector.connect(
           host=db_host,
           user=db_user,  
           password=db_password, 
           database=db_name
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
                    status VARCHAR(20) DEFAULT 'active'
                )
            """)
            
            connection.commit()
            print("Database initialized successfully")
            
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

init_db()