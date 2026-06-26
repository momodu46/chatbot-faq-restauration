import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'faq_dataset.csv')
CACHE_DIR = os.path.join(os.path.dirname(DATA_PATH))


def _load_faq(path):
    return pd.read_csv(path, encoding='utf-8')


FRENCH_STOPS = ['le', 'la', 'les', 'du', 'des', 'un', 'une', 'de', 'ce', 'cet', 'cette',
                'ces', 'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
                'nos', 'vos', 'leurs', 'je', 'tu', 'il', 'elle', 'on', 'nous', 'vous',
                'ils', 'elles', 'et', 'ou', 'où', 'qui', 'que', 'quoi', 'dont', 'au',
                'aux', 'est', 'sont', 'avez', 'ont', 'fait', 'peut', 'dans', 'sur',
                'avec', 'pour', 'par', 'pas', 'plus', 'très', 'bien', 'si', 'non', 'oui']


def _save_embeddings(embeddings):
    path = os.path.join(CACHE_DIR, 'question_embeddings.npy')
    np.save(path, embeddings)


def _load_embeddings():
    path = os.path.join(CACHE_DIR, 'question_embeddings.npy')
    try:
        return np.load(path)
    except FileNotFoundError:
        return None


class EmbeddingEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model_name = model_name
        self._embedder = None

        self.df = _load_faq(DATA_PATH)
        self.questions = self.df['question'].tolist()
        self.reponses = self.df['reponse'].tolist()
        self.categories = self.df['categorie'].tolist()

        self.tfidf_vectorizer = TfidfVectorizer(stop_words=FRENCH_STOPS)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.questions)

        self.question_embeddings = _load_embeddings()
        if self.question_embeddings is not None and len(self.question_embeddings) == len(self.questions):
            self._embeddings_loaded = True
        else:
            self._embeddings_loaded = False

    @property
    def embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(self.model_name)
            if not self._embeddings_loaded:
                self.question_embeddings = self._embedder.encode(self.questions, show_progress_bar=False)
                _save_embeddings(self.question_embeddings)
                self._embeddings_loaded = True
        return self._embedder

    def find_by_tfidf(self, query, top_k=3):
        query_vec = self.tfidf_vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = scores.argsort()[-top_k:][::-1]
        return [(self.questions[i], self.reponses[i], scores[i]) for i in top_indices if scores[i] > 0]

    def find_by_semantic(self, query, top_k=3):
        query_emb = self.embedder.encode([query], show_progress_bar=False)
        scores = cosine_similarity(query_emb, self.question_embeddings).flatten()
        top_indices = scores.argsort()[-top_k:][::-1]
        return [(self.questions[i], self.reponses[i], scores[i]) for i in top_indices if scores[i] > 0.3]

    def find_best_answer(self, query, method='semantic'):
        if method == 'tfidf':
            results = self.find_by_tfidf(query, top_k=1)
            return results[0] if results else None
        results = self.find_by_semantic(query, top_k=1)
        return results[0] if results else None

    def get_all_questions(self):
        return self.df[['id', 'categorie', 'question', 'reponse']].to_dict(orient='records')
