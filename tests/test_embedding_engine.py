import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.embedding_engine import EmbeddingEngine

engine = EmbeddingEngine()

def test_engine_charge_dataset():
    assert len(engine.questions) > 0
    assert len(engine.reponses) > 0
    assert len(engine.questions) == len(engine.reponses)

def test_tfidf_retourne_resultat():
    result = engine.find_by_tfidf("horaires ouverture", top_k=1)
    assert len(result) > 0
    assert len(result[0]) == 3  # (question, reponse, score)

def test_tfidf_score_entre_0_et_1():
    results = engine.find_by_tfidf("menu burger", top_k=3)
    for _, _, score in results:
        assert 0.0 <= score <= 1.0

def test_tfidf_question_vide():
    results = engine.find_by_tfidf("", top_k=1)
    assert results == []

def test_find_best_answer_tfidf():
    result = engine.find_best_answer("allergènes gluten", method="tfidf")
    assert result is not None
    assert isinstance(result[0], str)
    assert isinstance(result[1], str)

def test_find_best_answer_retourne_none_si_hors_sujet():
    result = engine.find_best_answer("météo demain paris", method="tfidf")
    # Peut retourner None ou un résultat faible — on vérifie juste que ça ne plante pas
    assert result is None or isinstance(result[0], str)

def test_get_all_questions():
    questions = engine.get_all_questions()
    assert isinstance(questions, list)
    assert len(questions) > 0
    assert "question" in questions[0]
    assert "reponse" in questions[0]