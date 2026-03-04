"""
MLflow Experiment Tracking Service
Logs NLP processing metrics for model versioning and experiments.
Auto-disabled if MLflow server is unavailable.
"""

import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("elearning.mlflow")


class MLflowTracker:
    """
    Track NLP pipeline metrics with MLflow.

    Usage:
        tracker = MLflowTracker()
        tracker.log_processing_run(
            filename="notes.pdf",
            text_length=5000,
            summary_length=500,
            summary_method="bart",
            keyword_count=10,
            keyword_method="tfidf",
            quiz_question_count=5,
        )
    """

    def __init__(self):
        self._available = False
        self._mlflow = None
        self.experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "elearning-nlp")
        self._init_mlflow()

    def _init_mlflow(self):
        """Initialize MLflow if available."""
        try:
            import mlflow

            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "")
            if not tracking_uri:
                logger.info("MLFLOW_TRACKING_URI not set. MLflow tracking disabled.")
                return

            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment(self.experiment_name)
            self._mlflow = mlflow
            self._available = True
            logger.info(f"MLflow ready (uri: {tracking_uri}, experiment: {self.experiment_name})")

        except ImportError:
            logger.info("mlflow not installed. Tracking disabled.")
        except Exception as e:
            logger.warning(f"MLflow init failed: {e}. Tracking disabled.")

    @property
    def is_available(self) -> bool:
        return self._available

    def log_processing_run(
        self,
        filename: str,
        text_length: int,
        summary_length: int,
        summary_method: str,
        compression_ratio: float = 0.0,
        keyword_count: int = 0,
        keyword_method: str = "unknown",
        quiz_question_count: int = 0,
        language: str = "en",
    ) -> Optional[str]:
        """
        Log a document processing run to MLflow.

        Returns:
            run_id (str) if successful, None otherwise.
        """
        if not self._available:
            return None

        try:
            with self._mlflow.start_run():
                # Log parameters
                self._mlflow.log_params({
                    "filename": filename[:100],
                    "summary_method": summary_method,
                    "keyword_method": keyword_method,
                    "language": language,
                })

                # Log metrics
                self._mlflow.log_metrics({
                    "text_length": text_length,
                    "summary_length": summary_length,
                    "compression_ratio": compression_ratio,
                    "keyword_count": keyword_count,
                    "quiz_question_count": quiz_question_count,
                })

                run_id = self._mlflow.active_run().info.run_id
                logger.info(f"MLflow run logged: {run_id}")
                return run_id

        except Exception as e:
            logger.warning(f"MLflow logging failed: {e}")
            return None

    def log_quiz_attempt(
        self,
        user_id: str,
        quiz_id: str,
        score: float,
        correct_count: int,
        total_questions: int,
        time_taken_seconds: int = 0,
    ) -> Optional[str]:
        """Log a quiz attempt to MLflow for learning analytics."""
        if not self._available:
            return None

        try:
            with self._mlflow.start_run():
                self._mlflow.log_params({
                    "user_id": user_id[:50],
                    "quiz_id": quiz_id[:50],
                    "run_type": "quiz_attempt",
                })

                self._mlflow.log_metrics({
                    "score": score,
                    "correct_count": correct_count,
                    "total_questions": total_questions,
                    "time_taken_seconds": time_taken_seconds,
                    "accuracy": correct_count / total_questions if total_questions > 0 else 0,
                })

                run_id = self._mlflow.active_run().info.run_id
                return run_id

        except Exception as e:
            logger.warning(f"MLflow quiz logging failed: {e}")
            return None


# Global instance
mlflow_tracker = MLflowTracker()
