import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- App setup ---
app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- Import routes ---
from app.routes import players, team_management, stats  # games.py can be added later

app.include_router(players.router)
app.include_router(team_management.router)
app.include_router(stats.router)
