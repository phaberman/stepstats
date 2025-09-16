import os
import duckdb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "stepstats.duckdb")

# Connect to DuckDB
con = duckdb.connect(DB_FILE)

# --- Create tables ---

# Teams table
con.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name TEXT,
    logo TEXT
)
""")

# Insert initial teams if table is empty
existing_teams = con.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
if existing_teams == 0:
    con.execute("""
    INSERT INTO teams (id, name, logo) VALUES
    (1, 'Stepdads', 'stepdads.png'),
    (2, 'Blackouts', 'blackouts.png'),
    (3, 'Dragons', 'dragons.png'),
    (4, 'SOBs', 'sobs.png'),
    (5, 'Thundersharkz', 'thundersharkz.png'),
    (6, 'Huge Wave', 'hugewave.png')
    """)

# Players table
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

# Games table
con.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    date DATE,
    home_team_id INTEGER,
    away_team_id INTEGER
)
""")

# Game results table
con.execute("""
CREATE TABLE IF NOT EXISTS game_results (
    id INTEGER PRIMARY KEY,
    away_team_id INTEGER,
    home_team_id INTEGER,
    away_team_runs INTEGER,
    home_team_runs INTEGER
)
""")

# Player stats table
con.execute("""
CREATE TABLE IF NOT EXISTS player_stats (
    id INTEGER PRIMARY KEY,
    player_id INTEGER,
    game_id INTEGER,
    singles INTEGER,
    doubles INTEGER,
    triples INTEGER,
    home_runs INTEGER,
    walks INTEGER,
    runs INTEGER,
    rbis INTEGER
)
""")

# --- Helper function ---
def get_next_id(table_name: str) -> int:
    """Return the next ID for a table."""
    return con.execute(f"SELECT COALESCE(MAX(id),0)+1 FROM {table_name}").fetchone()[0]
