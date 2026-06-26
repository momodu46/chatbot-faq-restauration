import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.web_scraper import (
    search_menu, search_promotions, format_menu_context,
    format_allergenes, format_produit_detail, format_horaires,
    search_en_ce_moment, get_services, get_info_produit
)
from src.brand_loader import load_brand_data


SAMPLE_DATA = {
    "menus": {
        "burgers": [
            {"nom": "Giant", "prix": 7.50, "description": "Un bon burger", "calories": 650,
             "allergenes": ["gluten", "lactose"], "traces": ["moutarde"], "ingredients": ["pain", "viande", "fromage"]},
            {"nom": "Classiq", "prix": 5.90, "description": "Le classique", "calories": 500},
        ]
    },
    "promotions": [
        {"titre": "Promo Giant", "description": "Giant à 5€"},
        {"titre": "Menu du mois", "description": "Menu à 8€"}
    ],
    "en_ce_moment": [
        {"nom": "Giant Truffe", "prix": 9.90, "description": "Édition limitée"}
    ],
    "horaires": {
        "sur_place": {"lundi": "11h-22h", "mardi": "11h-22h"}
    },
    "services": ["wifi", "parking"]
}


def test_search_menu_match():
    results = search_menu(SAMPLE_DATA, "giant")
    assert len(results) >= 1
    assert results[0]["nom"] == "Giant"


def test_search_menu_no_match():
    results = search_menu(SAMPLE_DATA, "pizza")
    assert len(results) == 0


def test_search_promotions():
    results = search_promotions(SAMPLE_DATA, "promo")
    assert len(results) >= 1
    assert results[0]["titre"] == "Promo Giant"


def test_format_menu_context():
    items = [{"nom": "Giant", "prix": 7.50, "calories": 650, "description": "Bon burger"}]
    text = format_menu_context(SAMPLE_DATA, items)
    assert "Giant" in text
    assert "€" in text
    assert "650" in text


def test_format_allergenes():
    item = {"allergenes": ["gluten"], "traces": ["moutarde"], "calories": 650, "ingredients": ["pain"]}
    text = format_allergenes(item)
    assert "gluten" in text
    assert "moutarde" in text
    assert "650" in text


def test_format_allergenes_empty():
    text = format_allergenes({})
    assert "Aucune information" in text


def test_format_produit_detail():
    item = {"nom": "Giant", "prix": 7.50, "calories": 650, "allergenes": ["gluten"]}
    text = format_produit_detail(item)
    assert "Giant" in text
    assert "€" in text


def test_search_en_ce_moment():
    items = search_en_ce_moment(SAMPLE_DATA)
    assert len(items) == 1
    assert items[0]["nom"] == "Giant Truffe"


def test_get_services():
    services = get_services(SAMPLE_DATA)
    assert "wifi" in services
    assert "parking" in services


def test_get_info_produit():
    item = get_info_produit(SAMPLE_DATA, "Giant")
    assert item is not None
    assert item["nom"] == "Giant"


def test_get_info_produit_not_found():
    item = get_info_produit(SAMPLE_DATA, "Inexistant")
    assert item is None


def test_format_horaires():
    horaires = {"sur_place": {"lundi": "11h-22h", "mardi": "11h-22h"}}
    text = format_horaires(horaires)
    assert "Sur place" in text
    assert "11h-22h" in text


def test_kfc_data_loads():
    data = load_brand_data("kfc")
    assert data["enseigne"] == "KFC"
    assert "menus" in data
    assert "Burgers" in data["menus"]
    assert len(data["menus"]["Burgers"]) >= 5
    assert data["menus"]["Burgers"][0]["nom"] == "Classic Chicken"
    assert "promotions" in data
    assert "horaires" in data
    assert "services" in data


def test_kfc_search_menu():
    data = load_brand_data("kfc")
    results = search_menu(data, "classic")
    assert len(results) >= 1
    assert results[0]["nom"] == "Classic Chicken"


def test_kfc_search_promotions():
    data = load_brand_data("kfc")
    results = search_promotions(data, "bucket")
    assert len(results) >= 1
