from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from services.external_api import get_opentdb_config


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0),
    ) as client:
        app.state.http = client
        yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Configure this function to use the external_api.py to show options for the user.
# Goals for this iteration
# Add a call to the API to fetch questions and associated answers based on user preferences
# Add the appropriate fields to the home.html template


@app.get("/")
async def home(request: Request):
    config = await get_opentdb_config(request.app.state.http)
    if config is None:
        # Provide fallback configuration if the API call fails
        config = {
            "categories": {},
            "difficulties": ["easy", "medium", "hard"],
            "types": ["multiple", "boolean"],
            "type_labels": {
                "multiple": "Multiple Choice",
                "boolean": "True / False",
            },
        }
    return templates.TemplateResponse(
        request,
        "home.html",
        {"title": "Home", "config": config},
    )


@app.get("/api/config")
async def api_config(request: Request):
    config = await get_opentdb_config(request.app.state.http)
    return config or {}


@app.get("/quiz")
async def quiz(
    request: Request,
    amount: int = 10,
    category: str = "",
    difficulty: str = "",
    type: str = "",
    page: int = 1,
):
    limit = 4
    params = {"amount": amount}
    if category:
        params["category"] = category
    if difficulty:
        params["difficulty"] = difficulty
    if type:
        params["type"] = type

    # For simplicity, we fetch all questions first, then paginate
    # In a real app, you might cache these or use an actual database
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://opentdb.com/api.php", params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        print(f"Error fetching questions: {e}")
        data = {"results": []}

    questions = data.get("results", [])
    if not questions and data.get("response_code") != 0:
        print(f"OpenTDB returned response_code: {data.get('response_code')}")
    total_questions = len(questions)

    # Simple pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_questions = questions[start:end]
    total_pages = (total_questions + limit - 1) // limit

    return templates.TemplateResponse(
        request,
        "quiz.html",
        {
            "title": "Quiz",
            "questions": paginated_questions,
            "page": page,
            "total_pages": total_pages,
            "amount": amount,
            "category": category,
            "difficulty": difficulty,
            "type": type,
        },
    )
