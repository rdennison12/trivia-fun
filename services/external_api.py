import json
from typing import Any

import httpx


async def get_opentdb_config() -> dict[str, Any] | None:
    """
    Fetch API configuration from Open Trivia Database.

    Returns:
        Dictionary containing API configuration or None if the request fails.

    """
    url = "https://opentdb.com/api_config.php"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
