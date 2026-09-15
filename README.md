# FromTomatoToSauce

Your personal online cookbook. Paste a recipe from Instagram (or anywhere),
and the app extracts the title, ingredients, steps, and tags automatically,
then saves it for browsing and ingredient-based search.

## How it works

- **FastAPI** serves a simple web UI and REST API
- **SQLite** stores the recipes (`recipes.db`)
- **Mistral LLM** turns free-form pasted text into structured recipe data

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export MISTRAL_API_KEY="your-key"   # from console.mistral.ai
```

## Run

```sh
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 in your browser, paste a recipe, and search by ingredients.

## API

| Method | Path                | Description                    |
|--------|---------------------|--------------------------------|
| POST   | `/recipes`          | Save a recipe (`text`, optional `source`) |
| GET    | `/recipes`          | List all recipes               |
| GET    | `/recipes/search?q=`| Search by ingredients/title   |
| GET    | `/recipes/{id}`     | Fetch one recipe               |