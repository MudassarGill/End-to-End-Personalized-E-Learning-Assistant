"""
MongoDB Models and CRUD Operations
Database: elearning_db on MongoDB Atlas
Collections: users, pdfs, quizzes, attempts, progress
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("elearning.models")


# ═══════════════════════════════════════════════
#  Database Connection Manager
# ═══════════════════════════════════════════════
class DatabaseManager:
    """Async MongoDB connection manager with connection pooling."""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self):
        """Connect to MongoDB Atlas."""
        mongo_uri = os.getenv(
            "MONGODB_URI",
            "mongodb://localhost:27017",
        )
        db_name = os.getenv("MONGODB_DB", "elearning_db")

        self.client = AsyncIOMotorClient(
            mongo_uri,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=10000,
        )
        self.db = self.client[db_name]

        # Test connection
        await self.client.admin.command("ping")
        logger.info(f"Connected to MongoDB: {db_name}")

        # Create indexes
        await self._create_indexes()

    async def _create_indexes(self):
        """Create database indexes for performance."""
        try:
            await self.db.users.create_index("email", unique=True)
            await self.db.pdfs.create_index("user_id")
            await self.db.quizzes.create_index("user_id")
            await self.db.quizzes.create_index("pdf_id")
            await self.db.attempts.create_index("user_id")
            await self.db.attempts.create_index("quiz_id")
            await self.db.progress.create_index("user_id", unique=True)
            logger.info("Database indexes created.")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")

    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    def get_db(self):
        """Get database instance."""
        return self.db


# Global instance
db_manager = DatabaseManager()


def _serialize(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    # Convert any remaining ObjectId fields
    for key, val in doc.items():
        if isinstance(val, ObjectId):
            doc[key] = str(val)
        elif isinstance(val, datetime):
            doc[key] = val.isoformat()
    return doc


# ═══════════════════════════════════════════════
#  User Model & CRUD
# ═══════════════════════════════════════════════
class UserModel:
    """
    User document structure:
    {
        _id: ObjectId,
        email: str (unique),
        name: str,
        created_at: datetime,
        last_active: datetime,
    }
    """

    collection_name = "users"

    @staticmethod
    def _collection():
        return db_manager.get_db()[UserModel.collection_name]

    @staticmethod
    async def create(email: str, name: str) -> Dict:
        """Create a new user."""
        doc = {
            "email": email,
            "name": name,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
        }
        result = await UserModel._collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        logger.info(f"User created: {email}")
        return _serialize(doc)

    @staticmethod
    async def get_by_id(user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        try:
            doc = await UserModel._collection().find_one(
                {"_id": ObjectId(user_id)}
            )
            return _serialize(doc)
        except Exception:
            return None

    @staticmethod
    async def get_by_email(email: str) -> Optional[Dict]:
        """Get user by email."""
        doc = await UserModel._collection().find_one({"email": email})
        return _serialize(doc)

    @staticmethod
    async def get_or_create(email: str, name: str = "Student") -> Dict:
        """Get existing user or create new one."""
        user = await UserModel.get_by_email(email)
        if user:
            await UserModel.update_last_active(user["id"])
            return user
        return await UserModel.create(email, name)

    @staticmethod
    async def update_last_active(user_id: str) -> bool:
        """Update user's last active timestamp."""
        result = await UserModel._collection().update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_active": datetime.utcnow()}},
        )
        return result.modified_count > 0

    @staticmethod
    async def delete(user_id: str) -> bool:
        """Delete a user."""
        result = await UserModel._collection().delete_one(
            {"_id": ObjectId(user_id)}
        )
        return result.deleted_count > 0

    @staticmethod
    async def list_all(limit: int = 50) -> List[Dict]:
        """List all users."""
        cursor = UserModel._collection().find().sort("created_at", -1).limit(limit)
        return [_serialize(doc) async for doc in cursor]


# ═══════════════════════════════════════════════
#  PDF Model & CRUD
# ═══════════════════════════════════════════════
class PDFModel:
    """
    PDF document structure:
    {
        _id: ObjectId,
        user_id: str,
        filename: str,
        original_filename: str,
        s3_url: str (optional),
        upload_date: datetime,
        pages: int,
        size_bytes: int,
        text_content: str,
        summary: str,
        keywords: list,
    }
    """

    collection_name = "pdfs"

    @staticmethod
    def _collection():
        return db_manager.get_db()[PDFModel.collection_name]

    @staticmethod
    async def create(
        user_id: str,
        filename: str,
        original_filename: str,
        pages: int = 0,
        size_bytes: int = 0,
        text_content: str = "",
        summary: str = "",
        keywords: List[str] = None,
        s3_url: str = "",
    ) -> Dict:
        """Save a processed PDF record."""
        doc = {
            "user_id": user_id,
            "filename": filename,
            "original_filename": original_filename,
            "s3_url": s3_url,
            "upload_date": datetime.utcnow(),
            "pages": pages,
            "size_bytes": size_bytes,
            "text_content": text_content[:50000],  # Limit stored text
            "summary": summary,
            "keywords": keywords or [],
        }
        result = await PDFModel._collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        logger.info(f"PDF saved: {original_filename}")
        return _serialize(doc)

    @staticmethod
    async def get_by_id(pdf_id: str) -> Optional[Dict]:
        """Get PDF by ID."""
        try:
            doc = await PDFModel._collection().find_one(
                {"_id": ObjectId(pdf_id)}
            )
            return _serialize(doc)
        except Exception:
            return None

    @staticmethod
    async def get_by_user(user_id: str, limit: int = 20, skip: int = 0) -> List[Dict]:
        """Get all PDFs for a user with pagination."""
        cursor = (
            PDFModel._collection()
            .find({"user_id": user_id})
            .sort("upload_date", -1)
            .skip(skip)
            .limit(limit)
        )
        return [_serialize(doc) async for doc in cursor]

    @staticmethod
    async def delete(pdf_id: str) -> bool:
        """Delete a PDF record."""
        result = await PDFModel._collection().delete_one(
            {"_id": ObjectId(pdf_id)}
        )
        return result.deleted_count > 0

    @staticmethod
    async def count_by_user(user_id: str) -> int:
        """Count PDFs by user."""
        return await PDFModel._collection().count_documents({"user_id": user_id})


# ═══════════════════════════════════════════════
#  Quiz Model & CRUD
# ═══════════════════════════════════════════════
class QuizModel:
    """
    Quiz document structure:
    {
        _id: ObjectId,
        user_id: str,
        pdf_id: str,
        title: str,
        questions: [
            {
                id: int,
                type: 'mcq' | 'true_false',
                question: str,
                options: list,
                correct_answer: int,
                explanation: str,
            }
        ],
        total_questions: int,
        difficulty: str,
        created_at: datetime,
        attempts_count: int,
    }
    """

    collection_name = "quizzes"

    @staticmethod
    def _collection():
        return db_manager.get_db()[QuizModel.collection_name]

    @staticmethod
    async def create(
        user_id: str,
        pdf_id: str,
        title: str,
        questions: List[Dict],
        difficulty: str = "medium",
    ) -> Dict:
        """Create a new quiz."""
        doc = {
            "user_id": user_id,
            "pdf_id": pdf_id,
            "title": title,
            "questions": questions,
            "total_questions": len(questions),
            "difficulty": difficulty,
            "created_at": datetime.utcnow(),
            "attempts_count": 0,
        }
        result = await QuizModel._collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        logger.info(f"Quiz created: {title} ({len(questions)} questions)")
        return _serialize(doc)

    @staticmethod
    async def get_by_id(quiz_id: str) -> Optional[Dict]:
        """Get quiz by ID."""
        try:
            doc = await QuizModel._collection().find_one(
                {"_id": ObjectId(quiz_id)}
            )
            return _serialize(doc)
        except Exception:
            return None

    @staticmethod
    async def get_by_user(
        user_id: str, limit: int = 20, skip: int = 0
    ) -> List[Dict]:
        """Get all quizzes for a user with pagination."""
        cursor = (
            QuizModel._collection()
            .find({"user_id": user_id})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        return [_serialize(doc) async for doc in cursor]

    @staticmethod
    async def increment_attempts(quiz_id: str):
        """Increment attempts counter."""
        await QuizModel._collection().update_one(
            {"_id": ObjectId(quiz_id)},
            {"$inc": {"attempts_count": 1}},
        )

    @staticmethod
    async def delete(quiz_id: str) -> bool:
        """Delete a quiz."""
        result = await QuizModel._collection().delete_one(
            {"_id": ObjectId(quiz_id)}
        )
        return result.deleted_count > 0

    @staticmethod
    async def count_by_user(user_id: str) -> int:
        """Count quizzes by user."""
        return await QuizModel._collection().count_documents({"user_id": user_id})


# ═══════════════════════════════════════════════
#  Attempt Model & CRUD
# ═══════════════════════════════════════════════
class AttemptModel:
    """
    Attempt document structure:
    {
        _id: ObjectId,
        user_id: str,
        quiz_id: str,
        answers: {question_id: selected_option},
        score: float (0-100),
        correct_count: int,
        total_questions: int,
        time_taken_seconds: int,
        date: datetime,
    }
    """

    collection_name = "attempts"

    @staticmethod
    def _collection():
        return db_manager.get_db()[AttemptModel.collection_name]

    @staticmethod
    async def create(
        user_id: str,
        quiz_id: str,
        answers: Dict[str, Any],
        score: float,
        correct_count: int,
        total_questions: int,
        time_taken_seconds: int = 0,
    ) -> Dict:
        """Save a quiz attempt."""
        doc = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "answers": answers,
            "score": round(score, 2),
            "correct_count": correct_count,
            "total_questions": total_questions,
            "time_taken_seconds": time_taken_seconds,
            "date": datetime.utcnow(),
        }
        result = await AttemptModel._collection().insert_one(doc)
        doc["_id"] = result.inserted_id

        # Increment quiz attempts
        await QuizModel.increment_attempts(quiz_id)

        logger.info(f"Attempt saved: quiz={quiz_id}, score={score}%")
        return _serialize(doc)

    @staticmethod
    async def get_by_user(user_id: str, limit: int = 50) -> List[Dict]:
        """Get all attempts for a user."""
        cursor = (
            AttemptModel._collection()
            .find({"user_id": user_id})
            .sort("date", -1)
            .limit(limit)
        )
        return [_serialize(doc) async for doc in cursor]

    @staticmethod
    async def get_by_quiz(quiz_id: str) -> List[Dict]:
        """Get all attempts for a quiz."""
        cursor = (
            AttemptModel._collection()
            .find({"quiz_id": quiz_id})
            .sort("date", -1)
        )
        return [_serialize(doc) async for doc in cursor]

    @staticmethod
    async def get_average_score(user_id: str) -> float:
        """Calculate user's average score across all attempts."""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}},
        ]
        result = await AttemptModel._collection().aggregate(pipeline).to_list(1)
        if result:
            return round(result[0]["avg_score"], 2)
        return 0.0


# ═══════════════════════════════════════════════
#  Progress Model & CRUD
# ═══════════════════════════════════════════════
class ProgressModel:
    """
    Progress document structure:
    {
        _id: ObjectId,
        user_id: str (unique),
        quizzes_taken: int,
        total_attempts: int,
        avg_score: float,
        best_score: float,
        strengths: [str],
        weaknesses: [str],
        recent_scores: [float] (last 10),
        updated_at: datetime,
    }
    """

    collection_name = "progress"

    @staticmethod
    def _collection():
        return db_manager.get_db()[ProgressModel.collection_name]

    @staticmethod
    async def get_or_create(user_id: str) -> Dict:
        """Get progress or create default."""
        doc = await ProgressModel._collection().find_one({"user_id": user_id})
        if doc:
            return _serialize(doc)
        return await ProgressModel._create_default(user_id)

    @staticmethod
    async def _create_default(user_id: str) -> Dict:
        """Create default progress record."""
        doc = {
            "user_id": user_id,
            "quizzes_taken": 0,
            "total_attempts": 0,
            "avg_score": 0.0,
            "best_score": 0.0,
            "strengths": [],
            "weaknesses": [],
            "recent_scores": [],
            "updated_at": datetime.utcnow(),
        }
        result = await ProgressModel._collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize(doc)

    @staticmethod
    async def update_after_attempt(
        user_id: str,
        score: float,
        keywords_correct: List[str] = None,
        keywords_wrong: List[str] = None,
    ) -> Dict:
        """Update progress after a quiz attempt."""
        progress = await ProgressModel.get_or_create(user_id)

        recent_scores = progress.get("recent_scores", [])
        recent_scores.append(score)
        recent_scores = recent_scores[-10:]  # Keep last 10

        # Update strengths/weaknesses
        strengths = list(set(progress.get("strengths", []) + (keywords_correct or [])))
        weaknesses = list(set(progress.get("weaknesses", []) + (keywords_wrong or [])))
        # Remove from weaknesses if now in strengths
        weaknesses = [w for w in weaknesses if w not in strengths]

        avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        best = max(recent_scores) if recent_scores else 0

        update_doc = {
            "$set": {
                "avg_score": round(avg, 2),
                "best_score": round(best, 2),
                "strengths": strengths[-20:],      # Keep top 20
                "weaknesses": weaknesses[-20:],
                "recent_scores": recent_scores,
                "updated_at": datetime.utcnow(),
            },
            "$inc": {
                "total_attempts": 1,
            },
        }

        await ProgressModel._collection().update_one(
            {"user_id": user_id},
            update_doc,
        )

        return await ProgressModel.get_or_create(user_id)


# ─── Ensure __init__.py exists for models package ───
_init_path = os.path.join(os.path.dirname(__file__), "__init__.py")
if not os.path.exists(_init_path):
    with open(_init_path, "w") as f:
        f.write("# Models package\n")
