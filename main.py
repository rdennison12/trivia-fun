import json
import random
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0),
    ) as client:
        app.state.http = client
        yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def shuffle_filter(answers):
    shuffled = list(answers)
    random.shuffle(shuffled)
    return shuffled


templates.env.filters["shuffle"] = shuffle_filter


@app.get("/")
def home(request: Request):
    with open("questions.json", "r", encoding="utf-8") as f:
        questions_data = json.load(f)
    return templates.TemplateResponse(
        request,
        "home.html",
        {"title": "Home", "questions": questions_data["results"]},
    )
