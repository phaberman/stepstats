import os, shutil
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from app.db import con, get_next_id

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Team Management page ---
@router.get("/team-management", response_class=HTMLResponse)
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
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))
    return templates.TemplateResponse("team_management.html", {"request": request, "players": players})

# --- Add Player ---
@router.get("/team-management/add", response_class=HTMLResponse)
async def add_player_form(request: Request):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))
    return templates.TemplateResponse("add_edit_player.html", {"request": request, "action": "Add", "player": None})

@router.post("/team-management/add")
async def add_player(
    name: str = Form(...),
    strength: str = Form(...),
    weakness: str = Form(...),
    gout_level: str = Form(...),
    quote: str = Form(...),
    image: UploadFile = File(...)
):
    image_filename = f"{name}_{image.filename}"
    image_path = os.path.join(UPLOAD_DIR, image_filename)
    with open(image_path, "wb") as f:
        shutil.copyfileobj(image.file, f)
    next_id = get_next_id("players")
    con.execute("""
        INSERT INTO players (id, name, strength, weakness, gout_level, quote, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (next_id, name, strength, weakness, gout_level, quote, f"uploads/{image_filename}"))
    return RedirectResponse("/team-management", status_code=303)

# --- Edit Player ---
@router.get("/team-management/edit/{player_id}", response_class=HTMLResponse)
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
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))
    return templates.TemplateResponse("add_edit_player.html", {"request": request, "action": "Save Changes", "player": player})

@router.post("/team-management/edit/{player_id}")
async def edit_player(
    player_id: int,
    name: str = Form(...),
    strength: str = Form(...),
    weakness: str = Form(...),
    gout_level: str = Form(...),
    quote: str = Form(...),
    image: UploadFile = File(None)
):
    current_image = con.execute("SELECT image FROM players WHERE id = ?", (player_id,)).fetchone()[0]
    if image and image.filename:
        image_filename = f"{name}_{image.filename}"
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_db_path = f"uploads/{image_filename}"
    else:
        image_db_path = current_image
    con.execute("""
        UPDATE players
        SET name=?, strength=?, weakness=?, gout_level=?, quote=?, image=?
        WHERE id=?
    """, (name, strength, weakness, gout_level, quote, image_db_path, player_id))
    return RedirectResponse("/team-management", status_code=303)

# --- Delete Player ---
@router.post("/team-management/delete/{player_id}")
async def delete_player(player_id: int):
    con.execute("DELETE FROM players WHERE id = ?", (player_id,))
    return RedirectResponse("/team-management", status_code=303)
