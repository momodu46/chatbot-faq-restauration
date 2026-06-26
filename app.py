import streamlit as st
from src.embedding_engine import EmbeddingEngine
from src.mistral_handler import MistralHandler
from src.web_scraper import (
    search_promotions, search_menu, format_menu_context,
    format_allergenes, search_en_ce_moment, get_horaires,
    get_services, get_info_produit, format_horaires,
    format_produit_detail
)
from src.brand_loader import detect_brand, load_brand_data, get_brand_info, get_all_brands
import json
import os

PROMO_KEYWORDS = ["promo", "offre", "nouveaute", "nouveau", "actuel", "actuellement", "bon plan", "reduction", "rabais", "solde"]
ALLERGEN_KEYWORDS = ["allergene", "allergene", "gluten", "lactose", "intolerant", "intolerant", "composition"]
CALORIE_KEYWORDS = ["calorie", "kcal", "nutrition", "nutritif", "gras", "proteine", "proteine"]
HORAIRE_KEYWORDS = ["horaire", "ouvert", "ferme", "ferme", "quand", "drive", "sur place"]
EN_MOMENT_KEYWORDS = ["en ce moment", "nouveaute", "nouveau", "ephemere", "ephemere", "actu", "actuellement", "du moment"]
INGREDIENT_KEYWORDS = ["ingredient", "ingredient", "dedans", "compose", "compose", "c'est quoi", "y a quoi"]
SERVICE_KEYWORDS = ["service", "wifi", "parking", "terrasse", "jeu", "handicap", "pmr", "application"]

st.set_page_config(page_title="Assistant Restaurant", page_icon="🍔")

def get_brand_data(brand_key):
    return load_brand_data(brand_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "brand" not in st.session_state:
    st.session_state.brand = "quick"

@st.cache_resource
def get_engine():
    with st.spinner("Chargement du moteur de recherche..."):
        return EmbeddingEngine()

engine = get_engine()

try:
    mistral = MistralHandler()
    has_mistral = True
except ValueError:
    mistral = None
    has_mistral = False

with st.sidebar:
    st.header("Enseigne")
    brand_key = st.radio(
        "Enseigne",
        options=["quick", "bk", "mcdo", "kfc"],
        format_func=lambda x: {"quick": "🍔 Quick", "bk": "👑 BK", "mcdo": "🍟 McDo", "kfc": "🍗 KFC"}[x],
        index=["quick", "bk", "mcdo", "kfc"].index(st.session_state.brand),
        label_visibility="collapsed"
    )
    st.session_state.brand = brand_key

    data = get_brand_data(st.session_state.brand)
    brand_info = get_brand_info(st.session_state.brand)
    brand_name = brand_info["display_name"]
    brand_emoji = brand_info["emoji"]

    st.header("Liens utiles")
    pdf_a = data.get("pdf_allergenes")
    if pdf_a:
        st.markdown(f"[📋 Tableau des allergènes (PDF)]({pdf_a})")
    pdf_n = data.get("pdf_nutrition")
    if pdf_n:
        st.markdown(f"[📊 Déclaration nutritionnelle (PDF)]({pdf_n})")
    st.markdown(f"[🌐 Site {brand_name}]({data.get('site', brand_info['site'])})")

    en_moment = search_en_ce_moment(data)
    if en_moment:
        st.header("En ce moment")
        for item in en_moment:
            st.markdown(f"**{item['nom']}** — {item['prix']}€")
            if item.get('description'):
                st.caption(item['description'])

    services = get_services(data)
    if services:
        st.header("Services")
        for s in services:
            st.markdown(f"✓ {s}")

    horaires = get_horaires(data)
    if horaires:
        with st.expander("Horaires types"):
            st.markdown(format_horaires(horaires))

st.title(f"{brand_emoji} Assistant {brand_name}")
st.caption("Menu, prix, allergènes, calories, horaires, promos...")

if not has_mistral:
    st.warning("⚠️ MISTRAL_API_KEY non définie — mode recherche seule (sans génération IA)")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = None
        faq_source = None
        answer_rendered = False

        detected_brand = detect_brand(prompt)
        if detected_brand != st.session_state.brand:
            st.session_state.brand = detected_brand
            data = get_brand_data(detected_brand)
            brand_info = get_brand_info(detected_brand)
            brand_name = brand_info["display_name"]
            brand_emoji = brand_info["emoji"]

        prompt_lower = prompt.lower()
        is_allergen = any(kw in prompt_lower for kw in ALLERGEN_KEYWORDS)
        is_calorie = any(kw in prompt_lower for kw in CALORIE_KEYWORDS)
        is_horaire = any(kw in prompt_lower for kw in HORAIRE_KEYWORDS)
        is_en_moment = any(kw in prompt_lower for kw in EN_MOMENT_KEYWORDS)
        is_service = any(kw in prompt_lower for kw in SERVICE_KEYWORDS)
        is_promo = any(kw in prompt_lower for kw in PROMO_KEYWORDS)
        is_ingredient = any(kw in prompt_lower for kw in INGREDIENT_KEYWORDS)

        if not has_mistral:
            if is_horaire:
                horaires = get_horaires(data)
                answer = f"**Horaires types {brand_name} :**\n\n{format_horaires(horaires)}"
            elif is_en_moment:
                items = search_en_ce_moment(data)
                if items:
                    text = "\n".join([f"• **{i['nom']}** — {i['prix']}€" + (f" : {i['description']}" if i.get('description') else "") for i in items])
                    answer = f"**En ce moment chez {brand_name} :**\n\n{text}"
            elif is_service:
                services = get_services(data)
                answer = "**Services disponibles :**\n" + "\n".join([f"• {s}" for s in services])
            elif is_allergen or is_calorie:
                menu_items = search_menu(data, prompt)
                if menu_items:
                    lines = []
                    for item in menu_items:
                        lines.append(format_produit_detail(item))
                        lines.append("")
                    answer = "\n".join(lines) if lines else None
            elif is_ingredient:
                menu_items = search_menu(data, prompt)
                if menu_items:
                    lines = []
                    for item in menu_items:
                        if item.get("ingredients"):
                            lines.append(f"**{item['nom']}** : {', '.join(item['ingredients'])}")
                        else:
                            lines.append(f"**{item['nom']}** : pas d'information détaillée disponible")
                    answer = "\n\n".join(lines) if lines else None

        if not answer:
            with st.spinner("Recherche..."):
                result = engine.find_best_answer(prompt, method="tfidf")

            if result and not has_mistral:
                faq_q, faq_a, score = result
                faq_source = (faq_q, faq_a, score)
                answer = faq_a

            if has_mistral:
                with st.spinner("Réflexion..."):
                    try:
                        menu_items = search_menu(data, prompt)
                        menu_text = format_menu_context(data, menu_items) if menu_items else ""
                        promos = search_promotions(data, prompt)
                        promos_text = "\n".join([f"• {p['titre']} : {p['description']}" for p in promos]) if promos else ""
                        faq_text = f"FAQ - {result[0]} : {result[1]}" if result and result[2] >= 0.3 else ""

                        if is_allergen or is_calorie or is_ingredient:
                            extra_lines = []
                            for item in menu_items:
                                info = format_allergenes(item)
                                if info:
                                    extra_lines.append(f"{item['nom']} : {info}")
                            if extra_lines:
                                menu_text += "\n\n" + "\n".join(extra_lines)

                        en_moment = search_en_ce_moment(data)
                        en_moment_text = "\n".join([f"• {i['nom']} ({i['prix']}€)" for i in en_moment]) if en_moment else ""
                        horaires_text = format_horaires(get_horaires(data))

                        context_parts = [p for p in [
                            f"Enseigne : {brand_name}",
                            faq_text, promos_text, menu_text,
                            f"En ce moment :\n{en_moment_text}" if en_moment_text else "",
                            f"Horaires :\n{horaires_text}" if is_horaire else ""
                        ] if p]
                        context = "\n\n".join(context_parts) if context_parts else ""
                        answer = st.write_stream(mistral.generate_answer_stream(prompt, context))
                        answer_rendered = True
                    except Exception as e:
                        print(f"ERREUR MISTRAL : {e}")
                        has_mistral = False
                        st.warning("⚠️ API Mistral indisponible — bascule en mode FAQ")
                        if result:
                            faq_q, faq_a, score = result
                            faq_source = (faq_q, faq_a, score)
                            answer = faq_a

        if answer:
            if not answer_rendered:
                st.markdown(answer)
            if faq_source:
                with st.expander("Voir la source"):
                    st.markdown(f"**Question :** {faq_source[0]}\n\n**Réponse :** {faq_source[1]}\n\n**Score :** {faq_source[2]:.2f}")

    st.session_state.messages.append({"role": "assistant", "content": answer or "Désolé, je n'ai pas trouvé de réponse."})
