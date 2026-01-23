from db_config import get_connection
import bcrypt

def create_users():
    """Create initial test users"""
    connection = get_connection()
    if not connection:
        print("Failed to connect to database")
        return
    
    cursor = connection.cursor()
    
    users = [
        {
            'email': 'admin@example.com',
            'username': 'admin',
            'password': 'adminpass',
            'role': 'admin'
        },
        {
            'email': 'bizreg@example.com',
            'username': 'bizreg',
            'password': 'bizpass',
            'role': 'business'
        },
        {
            'email': 'infreg@example.com',
            'username': 'infreg',
            'password': 'infpass',
            'role': 'influencer'
        },
        {
            'email': 'john@example.com',
            'username': 'john',
            'password': 'johnpass',
            'role': 'business'
        }
    ]
    
    for user in users:
        try:
            # Hash the password
            hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (email, username, password, role, status)
                VALUES (%s, %s, %s, %s, 'active')
            """, (user['email'], user['username'], hashed_password, user['role']))
            
            print(f"✓ Created {user['role']} user: {user['username']} ({user['email']})")
            
        except Exception as e:
            if "Duplicate entry" in str(e):
                print(f"⚠ User {user['username']} already exists, skipping...")
            else:
                print(f"✗ Error creating user {user['username']}: {e}")
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("\n=== User Credentials ===")
    print("Admin: admin@example.com / adminpass")
    print("Business: bizreg / bizpass")
    print("Influencer: infreg / infpass")
    print("Password Reset Test: john@example.com / johnpass")

if __name__ == "__main__":
    create_users()
