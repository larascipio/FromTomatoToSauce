"""Copy recipes from the old SQLite file into the Postgres database in DATABASE_URL.

Usage:
    uv run python -m scripts.migrate_sqlite_to_postgres [path/to/recipes.db]
"""

import json
import sqlite3
import sys

from psycopg.types.json import Jsonb

from app import db


def main() -> None:
    sqlite_path = sys.argv[1] if len(sys.argv) > 1 else "recipes.db"
    src = sqlite3.connect(sqlite_path)
    src.row_factory = sqlite3.Row
    rows = src.execute("SELECT * FROM recipes ORDER BY id").fetchall()

    db.init_db()
    with db.get_connection() as conn:
        for row in rows:
            conn.execute(
                """
                INSERT INTO recipes
                    (title, ingredients, steps, tags, source, raw_text, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s::timestamp AT TIME ZONE 'UTC')
                """,
                (
                    row["title"],
                    Jsonb(json.loads(row["ingredients"])),
                    Jsonb(json.loads(row["steps"])),
                    Jsonb(json.loads(row["tags"])),
                    row["source"],
                    row["raw_text"],
                    row["created_at"],
                ),
            )

    print(f"Copied {len(rows)} recipe(s) from {sqlite_path} to Postgres.")


if __name__ == "__main__":
    main()
