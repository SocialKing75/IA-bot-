import os
import sqlite3
import requests
from pydantic import BaseModel
from typing import Optional

DB_PATH = os.environ.get("KNOWLEDGE_DB", "knowledge.db")

class StravaConfig(BaseModel):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


def _get_conn(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_strava_table(path: str = DB_PATH):
    conn = _get_conn(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS strava_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            client_id TEXT,
            client_secret TEXT,
            access_token TEXT,
            refresh_token TEXT
        )
        """
    )
    # Ensure single row exists
    cur.execute("INSERT OR IGNORE INTO strava_config (id) VALUES (1)")
    conn.commit()
    conn.close()


def set_config(cfg: StravaConfig, path: str = DB_PATH):
    conn = _get_conn(path)
    cur = conn.cursor()
    cur.execute(
        "UPDATE strava_config SET client_id = ?, client_secret = ?, access_token = ?, refresh_token = ? WHERE id = 1",
        (cfg.client_id, cfg.client_secret, cfg.access_token, cfg.refresh_token),
    )
    conn.commit()
    conn.close()


def get_config(path: str = DB_PATH) -> StravaConfig:
    conn = _get_conn(path)
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM strava_config WHERE id = 1").fetchone()
    conn.close()
    if not row:
        return StravaConfig()
    return StravaConfig(client_id=row["client_id"], client_secret=row["client_secret"], access_token=row["access_token"], refresh_token=row["refresh_token"])


# Minimal function to query segment info
BASE_URL = "https://www.strava.com/api/v3"


def get_segment(segment_id: int) -> Optional[dict]:
    cfg = get_config()
    if not cfg.access_token:
        raise RuntimeError("Strava access token not configured")
    headers = {"Authorization": f"Bearer {cfg.access_token}"}
    resp = requests.get(f"{BASE_URL}/segments/{segment_id}", headers=headers, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Strava API error: {resp.status_code} {resp.text}")
    return resp.json()


# Initialize table on import
init_strava_table()
