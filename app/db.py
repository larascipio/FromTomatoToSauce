import json
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("RECIPE_DB", "recipes.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    steps TEXT NOT NULL,
    tags TEXT NOT NULL,
    source TEXT,
    raw_text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def insert_recipe(recipe: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO recipes (title, ingredients, steps, tags, source, raw_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                recipe["title"],
                json.dumps(recipe.get("ingredients", [])),
                json.dumps(recipe.get("steps", [])),
                json.dumps(recipe.get("tags", [])),
                recipe.get("source"),
                recipe["raw_text"],
            ),
        )
        return cur.lastrowid


def _row_to_dict(row: sqlite3.Row) -> dict:
    if row is None:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": json.loads(row["ingredients"]),
        "steps": json.loads(row["steps"]),
        "tags": json.loads(row["tags"]),
        "source": row["source"],
        "created_at": row["created_at"],
    }


def list_recipes() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM recipes ORDER BY id DESC").fetchall()
    return [_row_to_dict(r) for r in rows]


def get_recipe(recipe_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
    return _row_to_dict(row)


def search_recipes(query: str) -> list[dict]:
    tokens = [t.strip().lower() for t in query.split() if t.strip()]
    if not tokens:
        return list_recipes()

    results = []
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM recipes ORDER BY id DESC").fetchall()

    for row in rows:
        ingredients = " ".join(json.loads(row["ingredients"])).lower()
        title = row["title"].lower()
        if all(t in ingredients or t in title for t in tokens):
            results.append(_row_to_dict(row))
    return results
