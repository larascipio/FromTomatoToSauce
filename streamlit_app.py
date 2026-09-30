import hmac
import os

import streamlit as st

from app import db, parser

st.set_page_config(page_title="FromTomatoToSauce", page_icon="🍅")

SETTINGS = ("MISTRAL_API_KEY", "MISTRAL_MODEL", "DATABASE_URL", "APP_PASSWORD")


def load_settings() -> None:
    """Copy settings from Streamlit secrets into the environment, where parser/db read them.

    On Streamlit Community Cloud they come from the app's Secrets; locally they can
    come from .streamlit/secrets.toml or from exported environment variables.
    """
    try:
        secrets = {key: st.secrets[key] for key in SETTINGS if key in st.secrets}
    except FileNotFoundError:
        secrets = {}
    for key, value in secrets.items():
        os.environ.setdefault(key, str(value))


@st.cache_resource
def init_database() -> None:
    db.init_db()


def show_recipe(recipe: dict) -> None:
    with st.expander(recipe["title"]):
        if recipe["tags"]:
            st.caption(" · ".join(recipe["tags"]))
        st.markdown("**Ingredients**")
        for item in recipe["ingredients"]:
            st.markdown(f"- {item}")
        st.markdown("**Steps**")
        for number, step in enumerate(recipe["steps"], start=1):
            st.markdown(f"{number}. {step}")
        if recipe["source"]:
            st.caption(f"Source: {recipe['source']}")


def browse_page() -> None:
    query = st.text_input("Search by ingredient or title", placeholder="e.g. tomato garlic")
    recipes = db.search_recipes(query)
    if not recipes:
        st.info("No recipes found." if query.strip() else "No recipes yet.")
    for recipe in recipes:
        show_recipe(recipe)


def is_unlocked() -> bool:
    if st.session_state.get("unlocked"):
        return True

    expected = os.environ.get("APP_PASSWORD")
    if not expected:
        st.error("Adding recipes is disabled: APP_PASSWORD is not configured.")
        return False

    password = st.text_input("Password", type="password")
    if password:
        if hmac.compare_digest(password.encode(), expected.encode()):
            st.session_state.unlocked = True
            st.rerun()
        st.error("Wrong password.")
    return False


def add_page() -> None:
    if not is_unlocked():
        return

    # Step 1: paste free-form text and let the LLM structure it.
    with st.form("parse"):
        text = st.text_area("Paste a recipe", height=250)
        source = st.text_input("Source (optional)", placeholder="e.g. Instagram link")
        if st.form_submit_button("Parse recipe"):
            if not text.strip():
                st.warning("Paste a recipe first.")
            else:
                with st.spinner("Reading your recipe..."):
                    try:
                        st.session_state.draft = {
                            **parser.parse_recipe(text),
                            "source": source.strip() or None,
                            "raw_text": text.strip(),
                        }
                    except Exception as e:
                        st.error(f"Could not parse the recipe: {e}")

    draft = st.session_state.get("draft")
    if not draft:
        return

    # Step 2: review and correct the result before saving.
    st.subheader("Check the result")
    with st.form("review"):
        title = st.text_input("Title", value=draft["title"])
        ingredients = st.text_area(
            "Ingredients (one per line)", value="\n".join(draft["ingredients"]), height=200
        )
        steps = st.text_area("Steps (one per line)", value="\n".join(draft["steps"]), height=250)
        tags = st.text_input("Tags (comma separated)", value=", ".join(draft["tags"]))
        save, discard = st.columns(2)
        if save.form_submit_button("Save recipe", type="primary"):
            db.insert_recipe(
                {
                    **draft,
                    "title": title.strip() or "Untitled recipe",
                    "ingredients": _lines(ingredients),
                    "steps": _lines(steps),
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                }
            )
            del st.session_state.draft
            st.session_state.saved_title = title.strip()
            st.rerun()
        if discard.form_submit_button("Discard"):
            del st.session_state.draft
            st.rerun()


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


load_settings()
init_database()

st.title("🍅 FromTomatoToSauce")

if "saved_title" in st.session_state:
    st.success(f"Saved “{st.session_state.pop('saved_title')}”.")

browse_tab, add_tab = st.tabs(["Recipes", "Add recipe"])
with browse_tab:
    browse_page()
with add_tab:
    add_page()
