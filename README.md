# Assistant Restauration Rapide

Chatbot multi-enseigne pour les fast-foods en France : Quick, Burger King, McDonald's et KFC.

## Fonctionnalites

- Recherche dans une FAQ commune (TF-IDF + embeddings semantiques)
- Recherche dans les menus, promos, horaires, allergenes par enseigne
- Generation de reponse via Mistral AI (ou mode recherche seule sans cle API)
- Detection automatique de l'enseigne posee dans la question

## Structure du projet

```
.
├── app.py                  # Application Streamlit
├── data/
│   ├── faq_dataset.csv     # FAQ commune a toutes les enseignes
│   ├── quick_menu.json     # Menu Quick
│   ├── bk_menu.json        # Menu Burger King
│   ├── mcdo_menu.json      # Menu McDonald's
│   ├── kfc_menu.json       # Menu KFC
│   ├── question_embeddings.npy   # Cache des embeddings
│   └── embeddings_cache.pkl      # Cache supplementaire
├── notebooks/
│   └── exploration_analyse.ipynb # Analyse exploratoire
├── src/
│   ├── embedding_engine.py # Moteur TF-IDF + embeddings semantiques
│   ├── mistral_handler.py  # Interface avec l'API Mistral
│   ├── web_scraper.py      # Scraping + recherche dans les menus
│   └── brand_loader.py     # Detection et chargement des enseignes
├── tests/
│   ├── test_brand_loader.py
│   └── test_web_scraper.py
├── requirements.txt
├── launch.bat
└── .env                    # Cle API Mistral (a creer)
```

## Installation

```bash
# Cloner le depot
git clone <url>
cd assistant-restauration-rapide

# Installer les dependances
pip install -r requirements.txt

# Configurer la cle API Mistral (optionnel, mode degrade sans)
echo "MISTRAL_API_KEY=votre_cle_ici" > .env
```

## Utilisation

```bash
streamlit run app.py
```

Sans cle API Mistral, le chatbot fonctionne en mode "recherche seule"
(reponses depuis la FAQ uniquement).

## Tests

```bash
pytest tests/
```

## Technologies

- Python 3.14
- Streamlit (interface)
- sentence-transformers (embeddings semantiques)
- scikit-learn (TF-IDF, similarite cosinus)
- Mistral AI (generation de reponse)
- BeautifulSoup / requests (scraping)
