import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Templates folder
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Example player data
players = {
    1: {
        "name": "Sojo",
        "image": "sojo.jpg",
        "quote": "Can I get the 6 kuai chicken tenders?",
        "strength": "Bananas",
        "weakness": "Hamstrings"
    },
    2: {
        "name": "Phil",
        "image": "phil.jpg",
        "quote": "Nah, I'm going straight home after the games.",
        "strength": "Not being afraid of Bryce's throws from shortstop",
        "weakness": "effort"
    },
    3: {
        "name": "Al",
        "image": "al.jpg",
        "quote": "I have a reputation to protect!",
        "strength": "Won't shut up",
        "weakness": "Big and Gay"
    }
}

@app.get("/players/{player_id}", response_class=HTMLResponse)
async def player_profile(request: Request, player_id: int):
    player = players.get(player_id)
    if not player:
        return HTMLResponse(content="Player not found", status_code=404)
    return templates.TemplateResponse("player_profile.html", {"request": request, "player": player})
