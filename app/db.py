import os

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    ingredients JSONB NOT NULL,
    steps JSONB NOT NULL,
    tags JSONB NOT NULL,
    source TEXT,
    raw_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def get_connection() -> psycopg.Connection:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to your environment "
            "(e.g. export DATABASE_URL=postgresql://user:pass@host/dbname)."
        )
    return psycopg.connect(database_url, row_factory=dict_row)


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(SCHEMA)


def insert_recipe(recipe: dict) -> int:
    with get_connection() as conn:
        row = conn.execute(
            """
            INSERT INTO recipes (title, ingredients, steps, tags, source, raw_text)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                recipe["title"],
                Jsonb(recipe.get("ingredients", [])),
                Jsonb(recipe.get("steps", [])),
                Jsonb(recipe.get("tags", [])),
                recipe.get("source"),
                recipe["raw_text"],
            ),
        ).fetchone()
    return row["id"]


def _row_to_dict(row: dict | None) -> dict | None:
    if row is None:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "steps": row["steps"],
        "tags": row["tags"],
        "source": row["source"],
        "created_at": row["created_at"].isoformat(),
    }


def list_recipes() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM recipes ORDER BY id DESC").fetchall()
    return [_row_to_dict(r) for r in rows]


def get_recipe(recipe_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM recipes WHERE id = %s", (recipe_id,)
        ).fetchone()
    return _row_to_dict(row)


def search_recipes(query: str) -> list[dict]:
    tokens = [t.strip() for t in query.split() if t.strip()]
    if not tokens:
        return list_recipes()

    # Every token must appear in the title or somewhere in the ingredients.
    conditions = " AND ".join(
        "(title ILIKE %s OR ingredients::text ILIKE %s)" for _ in tokens
    )
    params = []
    for t in tokens:
        pattern = f"%{t}%"
        params += [pattern, pattern]

    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT * FROM recipes WHERE {conditions} ORDER BY id DESC", params
        ).fetchall()
    return [_row_to_dict(r) for r in rows]
