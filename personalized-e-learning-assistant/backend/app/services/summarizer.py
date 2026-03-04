"""
Summarizer Service - Generates summaries from extracted text.
Uses BART for English, extractive approach for Urdu/other languages.
Falls back to mock/extractive if ML models not available.
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("elearning.summarizer")


class Summarizer:
    """
    Text summarizer with ML model support and fallback.

    Usage:
        s = Summarizer()
        result = s.summarize("Long text here...")
        print(result['summary'])
    """

    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        self._pipeline = None
        self._model_loaded = False
        logger.info(f"Summarizer initialized (model: {model_name})")

    def _load_model(self):
        """Lazy-load the summarization model."""
        if self._model_loaded:
            return
        try:
            from transformers import pipeline
            self._pipeline = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
            )
            self._model_loaded = True
            logger.info("BART model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load ML model: {e}. Using extractive fallback.")
            self._pipeline = None
            self._model_loaded = True

    def summarize(
        self,
        text: str,
        max_length: int = 200,
        min_length: int = 50,
    ) -> Dict:
        """
        Generate summary from text.

        Returns:
            {
                'summary': str,
                'method': 'bart' | 'extractive',
                'original_length': int,
                'summary_length': int,
                'compression_ratio': float,
            }
        """
        if not text or len(text.strip()) < 30:
            return {
                "summary": text.strip(),
                "method": "passthrough",
                "original_length": len(text),
                "summary_length": len(text),
                "compression_ratio": 1.0,
            }

        lang = self._detect_language(text)

        # Try ML model for English
        if lang == "en":
            self._load_model()
            if self._pipeline:
                try:
                    summary = self._abstractive_summary(text, max_length, min_length)
                    return self._build_result(text, summary, "bart")
                except Exception as e:
                    logger.warning(f"BART failed: {e}. Using extractive.")

        # Extractive fallback (works for all languages)
        summary = self._extractive_summary(text, num_sentences=5)
        return self._build_result(text, summary, "extractive")

    def summarize_with_chunks(
        self, text: str, chunk_size: int = 1000
    ) -> Dict:
        """Summarize long text by chunking it first."""
        if len(text) <= chunk_size:
            return self.summarize(text)

        chunks = self._split_chunks(text, chunk_size)
        summaries = []
        for chunk in chunks[:5]:  # Max 5 chunks
            result = self.summarize(chunk, max_length=100, min_length=30)
            summaries.append(result["summary"])

        combined = " ".join(summaries)
        return self._build_result(text, combined, "chunked_extractive")

    # ── Private Methods ──

    def _abstractive_summary(self, text: str, max_length: int, min_length: int) -> str:
        """Use BART model for abstractive summarization."""
        # BART max input ~1024 tokens
        if len(text) > 1024:
            text = text[:1024]

        result = self._pipeline(
            text,
            max_length=max_length,
            min_length=min(min_length, len(text.split()) // 2),
            do_sample=False,
        )
        return result[0]["summary_text"]

    def _extractive_summary(self, text: str, num_sentences: int = 5) -> str:
        """Score sentences by word frequency and position, return top ones."""
        sentences = self._split_sentences(text)
        if len(sentences) <= num_sentences:
            return text.strip()

        # Build word frequencies
        words = text.lower().split()
        freq = {}
        for w in words:
            w = re.sub(r'[^\w]', '', w)
            if len(w) > 2:
                freq[w] = freq.get(w, 0) + 1

        scored = []
        for i, sent in enumerate(sentences):
            score = sum(freq.get(re.sub(r'[^\w]', '', w.lower()), 0)
                        for w in sent.split())
            # Position bonus
            if i < 3:
                score *= 1.5
            # Length bonus for medium sentences
            wc = len(sent.split())
            if 8 <= wc <= 30:
                score *= 1.3
            elif wc < 5:
                score *= 0.5
            scored.append((i, sent, score))

        scored.sort(key=lambda x: x[2], reverse=True)
        top = sorted(scored[:num_sentences], key=lambda x: x[0])
        return " ".join(s[1].strip() for s in top)

    def _detect_language(self, text: str) -> str:
        urdu_pattern = re.compile(r'[\u0600-\u06FF]')
        urdu_count = len(urdu_pattern.findall(text))
        alpha_count = sum(1 for c in text if c.isalpha())
        if alpha_count > 0 and urdu_count / alpha_count > 0.3:
            return "ur"
        return "en"

    def _split_sentences(self, text: str) -> List[str]:
        parts = re.split(r'(?<=[.!?\n])\s+', text)
        return [s.strip() for s in parts if len(s.strip()) > 10]

    def _split_chunks(self, text: str, size: int) -> List[str]:
        sentences = self._split_sentences(text)
        chunks, current = [], ""
        for s in sentences:
            if len(current) + len(s) > size and current:
                chunks.append(current.strip())
                current = s
            else:
                current += " " + s
        if current.strip():
            chunks.append(current.strip())
        return chunks

    def _build_result(self, original: str, summary: str, method: str) -> Dict:
        orig_len = len(original)
        summ_len = len(summary)
        return {
            "summary": summary,
            "method": method,
            "original_length": orig_len,
            "summary_length": summ_len,
            "compression_ratio": round(summ_len / orig_len, 2) if orig_len > 0 else 0,
        }
