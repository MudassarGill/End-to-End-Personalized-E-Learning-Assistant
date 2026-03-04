"""
Keyword Extraction Service
Uses TF-IDF with scikit-learn, supports English + Urdu.
Falls back to frequency-based extraction if sklearn unavailable.
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger("elearning.keywords")

# Urdu stop words
URDU_STOPS = {
    "کا", "کی", "کے", "ہے", "ہیں", "میں", "سے", "کو", "نے", "پر",
    "اور", "یہ", "وہ", "جو", "کہ", "تھا", "تھی", "تھے", "ہو", "ہوا",
    "اس", "ان", "جب", "تو", "بھی", "لیے", "ساتھ", "کر", "ہی", "تک",
    "یا", "مگر", "لیکن", "اگر", "کیا", "جیسے", "بعد", "پہلے",
    "بہت", "کچھ", "ایک", "دو", "اپنے", "اپنی", "اپنا",
    "ہوتا", "ہوتی", "والا", "والی", "والے", "رہا", "رہی",
    "گا", "گی", "گے", "ہوں", "تم", "آپ", "ہم",
}

ENGLISH_STOPS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "under", "again",
    "then", "once", "here", "there", "when", "where", "why", "how",
    "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "and", "but", "or", "if", "while", "it",
    "this", "that", "these", "those", "i", "me", "my", "we", "our",
    "you", "your", "he", "him", "his", "she", "her", "they", "them",
    "their", "its", "about", "also", "which", "many", "much", "just",
    "like", "over", "what", "use", "used", "using",
}


class KeywordExtractor:
    """
    Extract keywords using TF-IDF or frequency analysis.
    Supports English and Urdu.

    Usage:
        kw = KeywordExtractor()
        result = kw.extract_keywords("Some educational text...", top_n=10)
        print(result['keywords'])
    """

    def __init__(self):
        self._tfidf = None
        logger.info("KeywordExtractor initialized.")

    def extract_keywords(self, text: str, top_n: int = 10) -> Dict:
        """
        Extract keywords from text.

        Returns:
            {
                'keywords': ['word1', 'word2', ...],
                'scored_keywords': [('word1', 0.95), ...],
                'method': 'tfidf' | 'frequency',
                'language': 'en' | 'ur',
            }
        """
        lang = self._detect_language(text)

        if lang == "ur":
            scored = self._extract_urdu(text, top_n)
        else:
            scored = self._extract_tfidf(text, top_n)
            if not scored:
                scored = self._extract_frequency(text, top_n, lang)

        method = "tfidf" if lang == "en" else "frequency"

        return {
            "keywords": [kw for kw, _ in scored],
            "scored_keywords": scored,
            "method": method,
            "language": lang,
        }

    def _extract_tfidf(self, text: str, top_n: int) -> List[Tuple[str, float]]:
        """TF-IDF based extraction using sklearn."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            vectorizer = TfidfVectorizer(
                max_features=top_n * 3,
                stop_words="english",
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95,
            )
            matrix = vectorizer.fit_transform([text])
            features = vectorizer.get_feature_names_out()
            scores = matrix.toarray()[0]

            results = sorted(
                zip(features, scores),
                key=lambda x: x[1],
                reverse=True,
            )
            return [(kw, round(float(s), 4)) for kw, s in results[:top_n]]

        except Exception as e:
            logger.warning(f"TF-IDF failed: {e}")
            return []

    def _extract_urdu(self, text: str, top_n: int) -> List[Tuple[str, float]]:
        """Frequency-based extraction for Urdu text."""
        words = re.findall(r'[\u0600-\u06FF]+', text)
        filtered = [w for w in words if w not in URDU_STOPS and len(w) > 2]

        freq = {}
        for w in filtered:
            freq[w] = freq.get(w, 0) + 1

        max_freq = max(freq.values()) if freq else 1
        scored = [
            (w, round(c / max_freq, 4))
            for w, c in sorted(freq.items(), key=lambda x: x[1], reverse=True)
        ]
        return scored[:top_n]

    def _extract_frequency(
        self, text: str, top_n: int, lang: str = "en"
    ) -> List[Tuple[str, float]]:
        """Simple frequency-based fallback."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        stops = ENGLISH_STOPS if lang == "en" else URDU_STOPS
        filtered = [w for w in words if w not in stops]

        freq = {}
        for w in filtered:
            freq[w] = freq.get(w, 0) + 1

        max_freq = max(freq.values()) if freq else 1
        scored = [
            (w, round(c / max_freq, 4))
            for w, c in sorted(freq.items(), key=lambda x: x[1], reverse=True)
        ]
        return scored[:top_n]

    def _detect_language(self, text: str) -> str:
        urdu = len(re.findall(r'[\u0600-\u06FF]', text))
        alpha = sum(1 for c in text if c.isalpha())
        if alpha > 0 and urdu / alpha > 0.3:
            return "ur"
        return "en"
