"""Persistent local SQLite history."""
import json, sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "crowdripple.sqlite3"
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db=sqlite3.connect(DB_PATH); db.row_factory=sqlite3.Row
    db.execute("CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, inputs TEXT NOT NULL, state TEXT NOT NULL, prediction TEXT, recommendation TEXT)")
    db.commit(); return db
def save_run(inputs,state,prediction=None,recommendation=None):
    with connect() as db:
        cur=db.execute("INSERT INTO runs(inputs,state,prediction,recommendation) VALUES(?,?,?,?)",(json.dumps(inputs),json.dumps(state),json.dumps(prediction),json.dumps(recommendation)))
        return cur.lastrowid
def recent_runs(limit=20):
    with connect() as db: return [dict(r) for r in db.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?",(limit,)).fetchall()]
