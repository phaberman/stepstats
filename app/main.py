import os
import shutil
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import duckdb

# --- App setup ---
app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Templates folder
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- DuckDB setup ---
DB_FILE = os.path.join(BASE_DIR, "players.duckdb")
con = duckdb.connect(DB_FILE)

# Create table if not exists
con.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    name TEXT,
    strength TEXT,
    weakness TEXT,
    gout_level TEXT,
    quote TEXT,
    image TEXT
)
""")

UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Home route ---
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Fetch all players from DuckDB
    rows = con.execute("SELECT id, name, image FROM players ORDER BY id").fetchall()
    players = [
        {
            "id": r[0],
            "name": r[1],
            "image": r[2]
        } for r in rows
    ]
    return templates.TemplateResponse("index.html", {"request": request, "players": players})

# --- Player profile ---
@app.get("/players/{player_id}", response_class=HTMLResponse)
async def player_profile(request: Request, player_id: int):
    result = con.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    if not result:
        return HTMLResponse(content="Player not found", status_code=404)

    player = {
        "id": result[0],
        "name": result[1],
        "strength": result[2],
        "weakness": result[3],
        "gout_level": result[4],
        "quote": result[5],
        "image": result[6]
    }
    return templates.TemplateResponse("player_profile.html", {"request": request, "player": player})

# --- Team Management page ---
@app.get("/team-management", response_class=HTMLResponse)
async def team_management(request: Request):
    rows = con.execute("SELECT * FROM players ORDER BY id").fetchall()
    players = [
        {
            "id": r[0],
            "name": r[1],
            "strength": r[2],
            "weakness": r[3],
            "gout_level": r[4],
            "quote": r[5],
            "image": r[6]
        } for r in rows
    ]
    return templates.TemplateResponse("team_management.html", {"request": request, "players": players})

# --- Add player ---
@app.get("/team-management/add", response_class=HTMLResponse)
async def add_player_form(request: Request):
    return templates.TemplateResponse("add_edit_player.html", {"request": request, "action": "Add", "player": None})

@app.post("/team-management/add")
async def add_player(
    name: str = Form(...),
    strength: str = Form(...),
    weakness: str = Form(...),
    gout_level: str = Form(...),
    quote: str = Form(...),
    image: UploadFile = File(...)
):
    # Save uploaded image
    image_filename = f"{name}_{image.filename}"
    image_path = os.path.join(UPLOAD_DIR, image_filename)
    with open(image_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    # Get next ID
    next_id = con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM players").fetchone()[0]

    # Insert into DuckDB
    con.execute("""
        INSERT INTO players (id, name, strength, weakness, gout_level, quote, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (next_id, name, strength, weakness, gout_level, quote, f"uploads/{image_filename}"))

    return RedirectResponse("/team-management", status_code=303)

# --- Edit player ---
@app.get("/team-management/edit/{player_id}", response_class=HTMLResponse)
async def edit_player_form(request: Request, player_id: int):
    row = con.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    if not row:
        return HTMLResponse(content="Player not found", status_code=404)

    player = {
        "id": row[0],
        "name": row[1],
        "strength": row[2],
        "weakness": row[3],
        "gout_level": row[4],
        "quote": row[5],
        "image": row[6]
    }
    return templates.TemplateResponse(
        "add_edit_player.html",
        {"request": request, "action": "Save Changes", "player": player}
    )

@app.post("/team-management/edit/{player_id}")
async def edit_player(
    player_id: int,
    name: str = Form(...),
    strength: str = Form(...),
    weakness: str = Form(...),
    gout_level: str = Form(...),
    quote: str = Form(...),
    image: UploadFile = File(None)
):
    # Fetch current image path from DB
    current_image = con.execute("SELECT image FROM players WHERE id = ?", (player_id,)).fetchone()[0]

    # Only overwrite image if a file was uploaded
    if image and image.filename:
        image_filename = f"{name}_{image.filename}"
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_db_path = f"uploads/{image_filename}"
    else:
        image_db_path = current_image  # Preserve existing image

    con.execute("""
        UPDATE players
        SET name=?, strength=?, weakness=?, gout_level=?, quote=?, image=?
        WHERE id=?
    """, (name, strength, weakness, gout_level, quote, image_db_path, player_id))

    return RedirectResponse("/team-management", status_code=303)

# --- Delete player ---
@app.post("/team-management/delete/{player_id}")
async def delete_player(player_id: int):
    con.execute("DELETE FROM players WHERE id = ?", (player_id,))
    return RedirectResponse("/team-management", status_code=303)
