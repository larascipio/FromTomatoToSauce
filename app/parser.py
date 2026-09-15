import json
import os

from mistralai.client import Mistral

PROMPT = """You are a recipe parser. Extract structured data from the recipe text below.

Return ONLY valid JSON with EXACTLY this shape:
{{
  "title": "string",
  "ingredients": ["string", ...],
  "steps": ["string", ...],
  "tags": ["string", ...]
}}

Rules:
- title: the recipe name. If none found, use "Untitled recipe".
- ingredients: each ingredient on its own item, keeping amounts as written (e.g. "2 cups flour").
- steps: each instruction step on its own item, in order.
- tags: 2-5 short tags covering cuisine, meal type (breakfast/lunch/dinner/dessert) and notable flags (vegetarian, vegan, gluten-free, spicy, quick, etc).
- If a field is not present in the text, return an empty array. Never invent ingredients or steps.

Recipe text:
---
{text}
---
"""

RECIPE_MODEL = os.environ.get("MISTRAL_MODEL", "ministral-8b-latest")


def parse_recipe(text: str) -> dict:
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError(
            "MISTRAL_API_KEY is not set. Add it to your environment (e.g. export MISTRAL_API_KEY=...)."
        )

    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model=RECIPE_MODEL,
        messages=[{"role": "user", "content": PROMPT.format(text=text.strip())}],
response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Could not parse LLM output as JSON: {e}") from e

    return {
        "title": str(data.get("title") or "Untitled recipe").strip(),
        "ingredients": _as_list(data.get("ingredients")),
        "steps": _as_list(data.get("steps")),
        "tags": _as_list(data.get("tags")),
    }


def _as_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]