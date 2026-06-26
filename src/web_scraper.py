import requests
from bs4 import BeautifulSoup
import json
import os
import logging

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

FALLBACK_SOURCES = {
    "quick": {
        "menu": "https://fastfoodsmenu.com/prix-menu-quick-france/",
        "allergenes": "https://assets.quick.fr/Tableau_des_Allergenes_Quick_TF_7_and_TF_7_bis_SANS_REPERE_e653b93798.pdf",
        "nutrition": "https://assets.quick.fr/OK_Declaration_nutritionnelle_QUICK_3_067a228ebb.pdf",
        "calories": "https://www.fatsecret.fr/calories-nutrition/quick",
        "composition": "https://fr.openfoodfacts.org/marque/quick",
    },
    "bk": {
        "menu": "https://fastfoodsmenu.com/prix-menu-burger-king-france/",
        "allergenes": "https://ecoceabkstorageprdnorth.blob.core.windows.net/custom-pages/2026/03/crousty/Tableau_allergenes_clients_BK_CROUSTY_10_03_2026.pdf",
        "nutrition": "https://www.burgerking.fr/page/liste-allergenes",
        "calories": "https://corps-sain.fr/blog/calories-burger-king-tableau-complet-menus",
    },
    "mcdo": {
        "menu": "https://www.fou-food.fr/prix-menu-mcdo/",
        "allergenes": "https://www.mcdonalds.fr/mcdonalds-en-france/big-questions-pro/allergenes",
        "nutrition": "https://www.mcdonalds.fr/nos-produits/tableau-nutritionnel",
        "calories": "https://corps-sain.fr/blog/calories-mcdo-tableau-complet-menus",
        "composition": "https://www.mcdonalds.fr/aide-en-ligne/nos_produits/produits_mcdonald_s/valeurs_nutritionnelles",
    },
    "kfc": {
        "menu": "https://www.kfc.fr/menu",
        "allergenes": "https://www.kfc.fr/nutrition/allergenes",
        "nutrition": "https://www.kfc.fr/nutrition",
        "calories": "https://www.kfc.fr/nutrition",
        "composition": "https://www.kfc.fr/nutrition",
    }
}

QUICK_URLS = [
    "https://www.quick.fr/produits/burgers",
    "https://www.quick.fr/produits/menu",
]

BK_URLS = [
    "https://www.burgerking.fr/carte",
]

MCDO_URLS = [
    "https://www.mcdonalds.fr/nos-produits",
]

KFC_URLS = [
    "https://www.kfc.fr/menu",
    "https://www.kfc.fr/promotions",
]


def _scrape_url(url: str) -> str | None:
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup.find_all(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l for l in text.split("\n") if len(l) > 20]
        return "\n".join(lines[:50]) if lines else None
    except Exception as e:
        logging.error("Erreur scraping %s : %s", url, e)
        return None

def _normalize(text: str) -> str:
    return (text.lower()
            .replace("qu", "k")
            .replace("q", "k")
            .replace("é", "e")
            .replace("è", "e")
            .replace("ê", "e")
            .replace("à", "a")
            .replace("â", "a")
            .replace("ô", "o")
            .replace("î", "i")
            .replace("ù", "u")
            .replace("ç", "c")
            .replace("Ã©", "e")
            .replace("Ã¨", "e")
    )


ARTICLES = ["le", "la", "les", "du", "des", "un", "une", "de", "l", "d", "au", "aux"]


def search_promotions(data: dict, keyword: str = "") -> list[dict]:
    results = []
    keyword_lower = keyword.lower()
    for promo in data.get("promotions", []):
        if not keyword_lower or keyword_lower in promo["titre"].lower() or keyword_lower in promo["description"].lower():
            results.append(promo)
    return results


def get_all_promotions(data: dict) -> list[dict]:
    return data.get("promotions", []), None


def search_menu(data: dict, query: str = "", max_results: int = 5) -> list[dict]:
    results = []
    query_norm = _normalize(query)
    query_words = [w for w in query_norm.split() if len(w) > 2 and w not in ARTICLES]
    if not query_words:
        return results
    for category, items in data["menus"].items():
        for item in items:
            name_norm = _normalize(item["nom"])
            desc_norm = _normalize(item.get("description", ""))
            score = sum(1 for w in query_words if w in name_norm or w in desc_norm)
            if score > 0:
                results.append({**item, "categorie": category, "_score": score})
    results.sort(key=lambda x: x["_score"], reverse=True)
    for r in results:
        del r["_score"]
    return results[:max_results]


def format_menu_context(data: dict, results: list[dict]) -> str:
    if not results:
        return ""
    lines = []
    for r in results:
        desc = f" - {r['description']}" if r.get('description') else ""
        prix = f" : {r['prix']}€" if r.get('prix') else ""
        cal = f" ({r['calories']} kcal)" if r.get('calories') else ""
        lines.append(f"• {r['nom']}{prix}{cal}{desc}")
    return "\n".join(lines)


def search_en_ce_moment(data: dict) -> list[dict]:
    return data.get("en_ce_moment", [])


def get_horaires(data: dict) -> dict:
    return data.get("horaires", {})


def get_services(data: dict) -> list[str]:
    return data.get("services", [])


def get_info_produit(data: dict, nom: str) -> dict | None:
    nom_norm = _normalize(nom)
    for category, items in data["menus"].items():
        for item in items:
            if _normalize(item["nom"]) == nom_norm:
                return item
    return None


def format_allergenes(item: dict) -> str:
    parts = []
    if item.get("allergenes"):
        parts.append("Présence : " + ", ".join(item["allergenes"]))
    if item.get("traces"):
        parts.append("Traces possibles : " + ", ".join(item["traces"]))
    if item.get("calories"):
        parts.append(f"Calories : {item['calories']} kcal")
    if item.get("ingredients"):
        parts.append("Ingrédients : " + ", ".join(item["ingredients"]))
    return " | ".join(parts) if parts else "Aucune information allergène disponible"


def format_produit_detail(item: dict) -> str:
    lines = [f"**{item['nom']}** -- {item.get('prix', '?')}€"]
    if item.get("description"):
        lines.append(f"  {item['description']}")
    if item.get("calories"):
        lines.append(f"  Calories : {item['calories']} kcal")
    if item.get("allergenes"):
        lines.append(f"  Allergenes : {', '.join(item['allergenes'])}")
    if item.get("traces"):
        lines.append(f"  Traces : {', '.join(item['traces'])}")
    if item.get("ingredients"):
        lines.append(f"  Ingrédients : {', '.join(item['ingredients'])}")
    return "\n".join(lines)


def format_horaires(horaires: dict) -> str:
    lines = []

    if horaires.get("sur_place"):
        lines.append("**Sur place :**")
        for day, hours in horaires["sur_place"].items():
            lines.append(f"  {day.capitalize()} : {hours}")

    if horaires.get("drive"):
        lines.append("**Drive :**")
        for day, hours in horaires["drive"].items():
            lines.append(f"  {day.capitalize()} : {hours}")

    if horaires.get("click_and_collect"):
        lines.append("**Click & Collect :**")
        for day, hours in horaires["click_and_collect"].items():
            lines.append(f"  {day.capitalize()} : {hours}")

    if horaires.get("delivery"):
        lines.append("**Livraison :**")
        for day, hours in horaires["delivery"].items():
            lines.append(f"  {day.capitalize()} : {hours}")

    if horaires.get("petit_dejeuner"):
        lines.append("**Petit-déjeuner :**")
        for day, hours in horaires["petit_dejeuner"].items():
            lines.append(f"  {day.capitalize()} : {hours}")

    return "\n".join(lines)
