# FromTomatoToSauce

Your personal online cookbook. Paste a recipe from Instagram (or anywhere),
and the app extracts the title, ingredients, steps, and tags automatically,
then saves it for browsing and ingredient-based search.

## How it works

- **Streamlit** serves the web UI (`streamlit_app.py`)
- **PostgreSQL** stores the recipes (e.g. a free database on [Neon](https://neon.tech))
- **Mistral LLM** turns free-form pasted text into structured recipe data

Anyone with the link can browse and search recipes. Adding a recipe requires
the password in `APP_PASSWORD`; the parsed result is shown for review before saving.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv sync   # creates .venv and installs dependencies
```

Create `.streamlit/secrets.toml` (it is git-ignored, never commit it):

```toml
MISTRAL_API_KEY = "your-key"            # from console.mistral.ai
DATABASE_URL = "postgresql://..."       # connection string of your Postgres database
APP_PASSWORD = "choose-a-password"      # needed to add recipes
```

Exported environment variables with the same names work too.

To copy recipes from an old SQLite `recipes.db` into Postgres (run once):

```sh
uv run python -m scripts.migrate_sqlite_to_postgres recipes.db
```

## Run

```sh
uv run streamlit run streamlit_app.py
```

Open http://localhost:8501 in your browser.

## Deploy

On [Streamlit Community Cloud](https://share.streamlit.io), create an app from
this GitHub repo with `streamlit_app.py` as the main file, and paste the
contents of your `secrets.toml` into the app's **Secrets** setting.

## TO DO 
- design front-end
- design the back-end a bit more clearly
- figure out how to host it for free and connect it to a database that can be accessed on prem
- figure out if I can use an open source and free llm besides mistral
- figure out how the pydantic models should look like
- write a good prompt
- move to using langchain if necessary
- move to making the application agentic (for the sake of learning, but not sure if it is necessary)
- add features:
    - searching
    - editing a recipe from the front-end
    - ...