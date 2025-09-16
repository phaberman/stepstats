import os, shutil
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from app.db import con, get_next_id

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Player profile page
@router.get("/players/{player_id}", response_class=HTMLResponse)
async def player_profile(request: Request, player_id: int):
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
    return HTMLResponse(
        content=router.templates.TemplateResponse("player_profile.html", {"request": request, "player": player})
    )
