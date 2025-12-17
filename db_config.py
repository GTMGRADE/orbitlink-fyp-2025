import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pass",
        database="orbitlink_db"
    )

# Create database if it doesn't exist
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="pass"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS orbitlink_db")
    conn.close()
except mysql.connector.Error as err:
    print(f"Error creating database: {err}")