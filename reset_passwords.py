import sys
sys.path.insert(0, '/e/Users/User/Downloads/FYP/codingPortion')

from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("MONGODB_CONNECTION_STRING")
db_name = os.getenv("MONGODB_DATABASE_NAME", "orbitlinkfyp")

client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
db = client[db_name]

print("Resetting passwords for test users...")

# Reset bizreg password
hashed = bcrypt.hashpw('bizpass'.encode('utf-8'), bcrypt.gensalt(rounds=12))
result = db.users.update_one(
    {"username": "bizreg"},
    {"$set": {"password": hashed.decode('utf-8'), "status": "active"}}
)
print(f"✓ Reset bizreg password (matched: {result.matched_count}, modified: {result.modified_count})")

# Reset infreg password
hashed = bcrypt.hashpw('infpass'.encode('utf-8'), bcrypt.gensalt(rounds=12))
result = db.users.update_one(
    {"username": "infreg"},
    {"$set": {"password": hashed.decode('utf-8'), "status": "active"}}
)
print(f"✓ Reset infreg password (matched: {result.matched_count}, modified: {result.modified_count})")

# Reset admin password
hashed = bcrypt.hashpw('adminpass'.encode('utf-8'), bcrypt.gensalt(rounds=12))
result = db.users.update_one(
    {"username": "admin"},
    {"$set": {"password": hashed.decode('utf-8'), "status": "active", "role": "admin"}}
)
print(f"✓ Reset admin password (matched: {result.matched_count}, modified: {result.modified_count})")

print("\n=== Updated Login Credentials ===")
print("Admin: admin@example.com / adminpass (or use hardcoded: admin / admin123)")
print("Business: bizreg / bizpass")
print("Influencer: infreg / infpass")
