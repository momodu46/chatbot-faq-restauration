# Handover — Assistant Restauration Rapide

## Contexte

Chatbot multi-enseigne streamlit pour fast-foods en France : Quick, Burger King, McDonald's, KFC.
Recherche FAQ (TF-IDF + embeddings semantiques) + generation Mistral AI + donnees menus JSON.

## Structure

```
app.py               # Application Streamlit (214 lignes)
src/
  brand_loader.py    # Detection enseigne + chargement menus JSON
  embedding_engine.py# TF-IDF + embeddings (sentence-transformers)
  mistral_handler.py # Appel API Mistral (streaming)
  web_scraper.py     # Recherche menus/promos/horaires/services
data/
  faq_dataset.csv    # 49 questions FAQ, 10 categories
  quick_menu.json    # 124 items, 6 promos
  bk_menu.json       # 123 items, 6 promos
  mcdo_menu.json     # 151 items, 7 promos
  kfc_menu.json      # 71 items, 6 promos
tests/               # 24 tests unitaires (tout passe)
notebooks/           # 1 notebook d'analyse exploratoire
.env                # MISTRAL_API_KEY (clé valide)
```

## Ce qui a ete corrige (session actuelle)

1. **Double dossier `data/data/`** → fichiers deplaces dans `data/`, chemins corriges
2. **Parsing CSV fragile** → normalisation CSV guillemets + `pd.read_csv()`
3. **SYSTEM_PROMPT** → mis a jour avec les 4 enseignes
4. **`st.session_state.brand` conflict** → widget radio ne bloque plus l'auto-detection
5. **API Mistral 401** → nouvelle cle, plus fallback try/except vers FAQ
6. **Notebook & README** → crees
7. **Caches** → `__pycache__/` et logs supprimes

## Etat actuel

- **24/24 tests OK**
- **API Mistral OK** (cle valide, testee)
- **Fallback FAQ OK** (si API indisponible)
- **4 enseignes OK** (selection radio + auto-detection)

## Points restants

1. **Portabilite** : Si la cle expire, fallback FAQ deja fonctionnel
2. **Normalisation `_normalize()`** : `q->c` puis `qu->cu` est incoherent dans web_scraper.py
3. **Tests embedding_engine / mistral_handler** : pas de tests unitaires
4. **Versions requirements.txt** : pinner les versions pour eviter les regressions
5. **FAQ par enseigne** : pour l'instant FAQ commune (reponses generiques)

## Pour lancer

```bash
cd "Projet tuteuré"
pip install -r requirements.txt
streamlit run app.py
# ou double-clic sur launch.bat
```

La cle API est dans `.env` — si elle expire, le mode FAQ prend le relais automatiquement.
