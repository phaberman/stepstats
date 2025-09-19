import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from ..db import con
from fastapi.templating import Jinja2Templates

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/view-players", response_class=HTMLResponse)
async def view_players(request: Request):
    rows = con.execute("SELECT * FROM players ORDER BY name").fetchall()
    players = [
        {"id": r[0], "name": r[1], "strength": r[2], "weakness": r[3],
         "gout_level": r[4], "quote": r[5], "image": r[6]}
        for r in rows
    ]
    return templates.TemplateResponse("view_players.html", {"request": request, "players": players})
