import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# --- App setup ---

app = FastAPI()

# Security
load_dotenv()  # loads .env file
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")  # fallback
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "fallback-secret")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

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
    rows = con.execute("SELECT id, name, image FROM players ORDER BY name").fetchall()
    players = [{"id": r[0], "name": r[1], "image": r[2]} for r in rows]
    return templates.TemplateResponse("index.html", {"request": request, "players": players})

# --- Team Management login ---
from fastapi import Form
from fastapi.responses import RedirectResponse

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["is_admin"] = True
        return RedirectResponse("/team-management", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid password"})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
