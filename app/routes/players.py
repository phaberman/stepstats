# app/routes/players.py
import os
import shutil
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from ..db import con, get_next_id
from fastapi.templating import Jinja2Templates

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Player profile ---
@router.get("/players/{player_id}", response_class=HTMLResponse)
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
