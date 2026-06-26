import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

BRAND_CONFIG = {
    "quick": {
        "file": "quick_menu.json",
        "display_name": "Quick",
        "emoji": "🍔",
        "detect_keywords": ["quick", "qarrément", "qrousty", "giant", "classiq", "remarquable", "suprême", "suprême"],
        "site": "https://www.quick.fr",
    },
    "bk": {
        "file": "bk_menu.json",
        "display_name": "Burger King",
        "emoji": "👑",
        "detect_keywords": ["burger king", "bk", "whopper", "big king", "steakhouse", "king", "nuggets", "veggie whopper", "long chicken"],
        "site": "https://www.burgerking.fr",
    },
    "mcdo": {
        "file": "mcdo_menu.json",
        "display_name": "McDonald's",
        "emoji": "🍟",
        "detect_keywords": ["mcdo", "mcdonald", "big mac", "royal cheese", "mcchicken", "mccrispy", "filet o fish", "filet-o-fish", "happy meal", "mcnuggets", "mcfirst", "mcsmart", "big arch", "cbo", "big tasty", "mcmuffin"],
        "site": "https://www.mcdonalds.fr",
    },
    "kfc": {
        "file": "kfc_menu.json",
        "display_name": "KFC",
        "emoji": "🍗",
        "detect_keywords": ["kfc", "kentucky", "fried chicken", "poulet frit", "bucket", "popcorn chicken", "chicken strips", "tower burger", "classic chicken", "spicy chicken"],
        "site": "https://www.kfc.fr",
    },
}

BRAND_KEYWORDS = {}
for key, config in BRAND_CONFIG.items():
    for kw in config["detect_keywords"]:
        BRAND_KEYWORDS[kw] = key

def detect_brand(question: str, default: str = "quick") -> str:
    question_lower = question.lower().strip()
    best_brand = default
    best_pos = len(question_lower)
    for keyword, brand in BRAND_KEYWORDS.items():
        pos = question_lower.find(keyword)
        if pos != -1 and pos < best_pos:
            best_pos = pos
            best_brand = brand
    return best_brand

def load_brand_data(brand_key: str) -> dict:
    config = BRAND_CONFIG.get(brand_key)
    if not config:
        brand_key = "quick"
        config = BRAND_CONFIG["quick"]
    path = os.path.join(DATA_DIR, config["file"])
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_brand_info(brand_key: str) -> dict:
    return BRAND_CONFIG.get(brand_key, BRAND_CONFIG["quick"])

def get_all_brands() -> list[str]:
    return list(BRAND_CONFIG.keys())
