# FromTomatoToSauce

Your personal online cookbook. Paste a recipe from Instagram (or anywhere),
and the app extracts the title, ingredients, steps, and tags automatically,
then saves it for browsing and ingredient-based search.

## How it works

- **FastAPI** serves a simple web UI and REST API
- **SQLite** stores the recipes (`recipes.db`)
- **Mistral LLM** turns free-form pasted text into structured recipe data

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv sync                             # creates .venv and installs dependencies
export MISTRAL_API_KEY="your-key"   # from console.mistral.ai
```

## Run

```sh
uv run uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 in your browser, paste a recipe, and search by ingredients.

## API

| Method | Path                | Description                    |
|--------|---------------------|--------------------------------|
| POST   | `/recipes`          | Save a recipe (`text`, optional `source`) |
| GET    | `/recipes`          | List all recipes               |
| GET    | `/recipes/search?q=`| Search by ingredients/title   |
| GET    | `/recipes/{id}`     | Fetch one recipe               |

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