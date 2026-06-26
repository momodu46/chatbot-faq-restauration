import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.brand_loader import detect_brand, get_brand_info, get_all_brands


def test_detect_brand_quick():
    assert detect_brand("quick menu") == "quick"
    assert detect_brand("qrousty") == "quick"
    assert detect_brand("giant") == "quick"


def test_detect_brand_bk():
    assert detect_brand("burger king") == "bk"
    assert detect_brand("whopper") == "bk"
    assert detect_brand("big king") == "bk"


def test_detect_brand_mcdo():
    assert detect_brand("mcdo") == "mcdo"
    assert detect_brand("mcdonald") == "mcdo"
    assert detect_brand("big mac") == "mcdo"


def test_detect_brand_default():
    assert detect_brand("menu du jour") == "quick"


def test_detect_brand_priorite():
    assert detect_brand("quick burger king") == "quick"


def test_get_brand_info():
    info = get_brand_info("quick")
    assert info["display_name"] == "Quick"
    assert info["emoji"] == "🍔"

    info = get_brand_info("bk")
    assert info["display_name"] == "Burger King"

    info = get_brand_info("mcdo")
    assert info["display_name"] == "McDonald's"


def test_get_brand_info_invalid():
    info = get_brand_info("unknown")
    assert info["display_name"] == "Quick"


def test_detect_brand_kfc():
    assert detect_brand("kfc") == "kfc"
    assert detect_brand("kentucky") == "kfc"
    assert detect_brand("bucket") == "kfc"
    assert detect_brand("poulet frit") == "kfc"


def test_get_all_brands():
    brands = get_all_brands()
    assert "quick" in brands
    assert "bk" in brands
    assert "mcdo" in brands
    assert "kfc" in brands
