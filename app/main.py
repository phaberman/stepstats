import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- App setup ---
app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- Import db ---
from .db import con, get_next_id

# --- Import routers ---
from .routes import players, stats, team_management, games

app.include_router(players.router)
app.include_router(stats.router)
app.include_router(team_management.router)
app.include_router(games.router)

# --- Home route ---
from fastapi import Request
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Example: fetch players for homepage
    rows = con.execute("SELECT id, name, image FROM players ORDER BY id").fetchall()
    players = [{"id": r[0], "name": r[1], "image": r[2]} for r in rows]
    return templates.TemplateResponse("index.html", {"request": request, "players": players})
