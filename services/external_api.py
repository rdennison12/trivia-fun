import json
from typing import Any

import httpx


async def get_opentdb_config(client: httpx.AsyncClient) -> dict[str, Any] | None:
    """
    Fetch API configuration from Open Trivia Database.

    Returns:
        Dictionary containing API configuration or None if the request fails.
    """
    categories_url = "https://opentdb.com/api_category.php"

    try:
        response = await client.get(categories_url)
        response.raise_for_status()
        categories_data = response.json()

        # Format categories as {id: name} as expected by the template
        categories = {
            str(cat["id"]): cat["name"]
            for cat in categories_data.get("trivia_categories", [])
        }

        # OpenTDB has fixed difficulties and types
        difficulties = ["easy", "medium", "hard"]
        types = ["multiple", "boolean"]
        type_labels = {
            "multiple": "Multiple Choice",
            "boolean": "True / False",
        }

        return {
            "categories": categories,
            "difficulties": difficulties,
            "types": types,
            "type_labels": type_labels,
        }
    except (httpx.HTTPError, json.JSONDecodeError, KeyError) as e:
        print(f"Error occurred while fetching OpenTDB config: {e}")
        return None
