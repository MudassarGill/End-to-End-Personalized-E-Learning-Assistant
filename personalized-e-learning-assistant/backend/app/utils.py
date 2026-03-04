# Utility functions
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "elearning_db")


async def get_database():
    """Get MongoDB database connection."""
    client = AsyncIOMotorClient(MONGO_URL)
    return client[DATABASE_NAME]


def truncate_text(text: str, max_length: int = 5000) -> str:
    """Truncate text to a maximum length."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
