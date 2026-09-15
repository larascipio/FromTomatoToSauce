from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import db, parser

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="FromTomatoToSauce")

db.init_db()


class SaveRequest(BaseModel):
    text: str
    source: str | None = None


class ParsedRecipe(BaseModel):
    title: str
    ingredients: list[str]
    steps: list[str]
    tags: list[str]


class RecipeOut(ParsedRecipe):
    id: int
    source: str | None = None
    created_at: str


@app.post("/recipes")
def save_recipe(req: SaveRequest) -> dict:
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Recipe text is empty.")

    parsed = parser.parse_recipe(req.text)
    recipe_id = db.insert_recipe(
        {
            **parsed,
            "source": req.source,
            "raw_text": req.text.strip(),
        }
    )
    saved = db.get_recipe(recipe_id)
    return {"message": "Recipe saved", "recipe": saved}


@app.get("/recipes")
def list_recipes() -> list[dict]:
    return db.list_recipes()


@app.get("/recipes/search")
def search_recipes(q: str = "") -> list[dict]:
    return db.search_recipes(q)


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int) -> dict:
    recipe = db.get_recipe(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")