"""
AWS S3 Upload Service
Uploads files to S3 bucket for persistent storage.
Gracefully degrades if AWS credentials are not configured.
"""

import os
import logging
from typing import Dict, Optional

logger = logging.getLogger("elearning.s3")


class S3Uploader:
    """
    Upload files to AWS S3.

    Usage:
        uploader = S3Uploader()
        result = uploader.upload(file_bytes, "doc.pdf", "uploads/")
        print(result['url'])
    """

    def __init__(self):
        self._client = None
        self._available = False
        self.bucket = os.getenv("AWS_S3_BUCKET", "elearning-uploads")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self._init_client()

    def _init_client(self):
        """Initialize S3 client if credentials are available."""
        try:
            import boto3

            access_key = os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

            if not access_key or not secret_key:
                logger.info("AWS credentials not configured. S3 uploads disabled.")
                return

            self._client = boto3.client(
                "s3",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=self.region,
            )
            self._available = True
            logger.info(f"S3 client ready (bucket: {self.bucket}, region: {self.region})")

        except ImportError:
            logger.warning("boto3 not installed. S3 uploads disabled.")
        except Exception as e:
            logger.warning(f"S3 init failed: {e}. Uploads disabled.")

    @property
    def is_available(self) -> bool:
        return self._available

    def upload(
        self,
        file_bytes: bytes,
        filename: str,
        prefix: str = "uploads/",
        content_type: str = "application/octet-stream",
    ) -> Dict:
        """
        Upload file bytes to S3.

        Returns:
            {
                'success': bool,
                'url': str (S3 public URL or ''),
                'key': str (S3 object key or ''),
                'error': str or None,
            }
        """
        if not self._available:
            return {
                "success": False,
                "url": "",
                "key": "",
                "error": "S3 not configured",
            }

        s3_key = f"{prefix}{filename}"

        try:
            self._client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=file_bytes,
                ContentType=content_type,
            )

            url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"
            logger.info(f"Uploaded to S3: {s3_key}")

            return {
                "success": True,
                "url": url,
                "key": s3_key,
                "error": None,
            }

        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return {
                "success": False,
                "url": "",
                "key": s3_key,
                "error": str(e),
            }

    def delete(self, s3_key: str) -> bool:
        """Delete an object from S3."""
        if not self._available:
            return False
        try:
            self._client.delete_object(Bucket=self.bucket, Key=s3_key)
            logger.info(f"Deleted from S3: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"S3 delete failed: {e}")
            return False

    def generate_presigned_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a presigned URL for temporary access."""
        if not self._available:
            return None
        try:
            url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=expires_in,
            )
            return url
        except Exception as e:
            logger.error(f"Presigned URL failed: {e}")
            return None


# Global instance
s3_uploader = S3Uploader()
