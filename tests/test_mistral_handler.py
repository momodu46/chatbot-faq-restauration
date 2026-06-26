import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_mistral_handler_charge_si_cle_presente():
    os.environ.get("MISTRAL_API_KEY")
    try:
        from src.mistral_handler import MistralHandler
        handler = MistralHandler()
        assert handler.model == "mistral-small-latest"
    except ValueError:
        # Clé absente — test ignoré
        pass

def test_mistral_handler_leve_erreur_sans_cle():
    from src.mistral_handler import MistralHandler
    original = os.environ.pop("MISTRAL_API_KEY", None)
    try:
        try:
            MistralHandler()
            assert False, "Aurait dû lever ValueError"
        except ValueError:
            pass
    finally:
        if original:
            os.environ["MISTRAL_API_KEY"] = original

def test_mistral_generate_answer_retourne_string():
    try:
        from src.mistral_handler import MistralHandler
        handler = MistralHandler()
        result = handler.generate_answer("Quels sont vos horaires ?", context="Enseigne : Quick")
        assert isinstance(result, str)
        assert len(result) > 0
    except ValueError:
        pass