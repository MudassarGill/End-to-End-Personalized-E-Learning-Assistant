"""
MongoDB Atlas Connection Test
Tests connectivity, CRUD operations, and collection listing.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get MongoDB URI
mongo_uri = os.getenv('MONGODB_URI')
db_name = os.getenv('MONGODB_DB', 'elearning_db')

print("=" * 50)
print("  MongoDB Atlas Connection Test")
print("=" * 50)

if not mongo_uri:
    print("❌ MONGODB_URI not found in .env file!")
    print("   Make sure your .env has: MONGODB_URI=mongodb+srv://...")
    exit(1)

print(f"\n🔌 Connecting to MongoDB Atlas...")
print(f"   Database: {db_name}")

try:
    # Connect to MongoDB
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)

    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB Connected Successfully!")

    # Get database
    db = client[db_name]

    # Create a test collection
    test_collection = db['connection_test']

    # Insert test document
    result = test_collection.insert_one({
        "status": "connected",
        "timestamp": "test",
        "project": "Personalized E-Learning Assistant"
    })
    print(f"✅ Test document inserted with ID: {result.inserted_id}")

    # Clean up
    test_collection.delete_one({"_id": result.inserted_id})
    print("✅ Test document cleaned up")

    # List all collections
    collections = db.list_collection_names()
    print(f"\n📚 Available collections: {collections}")

    client.close()
    print("\n🎉 MongoDB Atlas setup complete and verified!")

except Exception as e:
    print(f"\n❌ Connection Failed: {e}")
    print("\n   Possible fixes:")
    print("   1. Check your MONGODB_URI in .env file")
    print("   2. Whitelist your IP in MongoDB Atlas Network Access")
    print("   3. Check username/password are correct")
    print("   4. Run: pip install pymongo[srv] python-dotenv")
