from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.db import con, get_next_id

router = APIRouter()

from fastapi.templating import Jinja2Templates
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

# View Stats table
@router.get("/stats", response_class=HTMLResponse)
async def view_stats(request: Request):
    rows = con.execute("""
        SELECT ps.id, p.name, ps.singles, ps.doubles, ps.triples, ps.home_runs,
               ps.walks, ps.runs, ps.rbis
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.id
        ORDER BY p.name
    """).fetchall()

    stats = []
    for r in rows:
        H = r[2]+r[3]+r[4]+r[5]  # hits
        AB = max(H + r[6],1)      # approximate at-bats = H + walks (simplified)
        Avg = round(H/AB,3) if AB>0 else 0
        SLG = round((r[2]+2*r[3]+3*r[4]+4*r[5])/AB,3) if AB>0 else 0
        OPS = round(Avg + SLG,3)
        stats.append({
            "id": r[0], "name": r[1], "singles": r[2], "doubles": r[3],
            "triples": r[4], "home_runs": r[5], "walks": r[6],
            "runs": r[7], "rbis": r[8], "H": H, "Avg": Avg, "SLG": SLG, "OPS": OPS
        })
    return templates.TemplateResponse("stats.html", {"request": request, "stats": stats})

# Add stats for a player
@router.get("/stats/add", response_class=HTMLResponse)
async def add_stats_form(request: Request):
    players = con.execute("SELECT id, name FROM players ORDER BY name").fetchall()
    return templates.TemplateResponse("add_edit_stats.html", {"request": request, "players": players, "action": "Add"})

@router.post("/stats/add")
async def add_stats(
    player_id: int = Form(...),
    singles: int = Form(...),
    doubles: int = Form(...),
    triples: int = Form(...),
    home_runs: int = Form(...),
    walks: int = Form(...),
    runs: int = Form(...),
    rbis: int = Form(...)
):
    next_id = get_next_id("player_stats")
    con.execute("""
        INSERT INTO player_stats
        (id, player_id, game_id, singles, doubles, triples, home_runs, walks, runs, rbis)
        VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?)
    """, (next_id, player_id, singles, doubles, triples, home_runs, walks, runs, rbis))
    return RedirectResponse("/stats", status_code=303)
