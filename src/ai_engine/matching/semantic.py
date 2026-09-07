from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 1), min_df=1)

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        if not text_a or not text_b or not text_a.strip() or not text_b.strip():
            return 0.0

        try:
            tfidf_matrix = self.vectorizer.fit_transform([text_a, text_b])
            score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(round(max(0.0, min(1.0, score)), 4))
        except Exception:
            return 0.0
