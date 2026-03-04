# Extract keywords from text
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract top keywords from text using TF-IDF."""
    vectorizer = TfidfVectorizer(
        max_features=top_n,
        stop_words="english",
        ngram_range=(1, 2),
    )

    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()

    # Sort by TF-IDF score
    scores = tfidf_matrix.toarray()[0]
    keyword_scores = list(zip(feature_names, scores))
    keyword_scores.sort(key=lambda x: x[1], reverse=True)

    return [kw for kw, score in keyword_scores[:top_n]]
