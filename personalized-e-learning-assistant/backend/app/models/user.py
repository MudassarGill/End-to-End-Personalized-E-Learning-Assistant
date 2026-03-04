# MongoDB user models
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QuizAttempt(BaseModel):
    quiz_id: str
    score: int
    total: int
    attempted_at: datetime = Field(default_factory=datetime.utcnow)


class UserProgress(BaseModel):
    topic: str
    summaries_viewed: int = 0
    quizzes_taken: int = 0
    average_score: float = 0.0


class User(BaseModel):
    username: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    progress: List[UserProgress] = []
    quiz_attempts: List[QuizAttempt] = []
    uploaded_files: List[str] = []
