from fastapi import FastAPI
from pathlib import Path
import sqlite3

APP_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = APP_ROOT / "db" / "risk.db"

app = FastAPI(title="GMP Packaging Risk Analytics API", version="0.1.0")

def ensure_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Minimal tables to prove pipeline works; we'll expand later
    cur.execute("""
    CREATE TABLE IF NOT EXISTS machines (
        machine_id TEXT PRIMARY KEY,
        site_id TEXT NOT NULL,
        is_legacy INTEGER NOT NULL,
        vendor TEXT,
        model TEXT,
        timezone TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        ts_utc TEXT NOT NULL,
        site_id TEXT NOT NULL,
        machine_id TEXT NOT NULL,
        tag TEXT NOT NULL,
        value REAL NOT NULL
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry(ts_utc)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_machine ON telemetry(machine_id)")
    con.commit()
    con.close()

@app.on_event("startup")
def startup():
    ensure_db()

@app.get("/health")
def health():
    return {"status": "ok", "db_path": str(DB_PATH)}

@app.get("/db/info")
def db_info():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    con.close()
    return {"tables": tables}
