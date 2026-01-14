import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.robotparser
import json
import time
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel, Field

DB_PATH = os.environ.get("KNOWLEDGE_DB", "knowledge.db")

class KnowledgeItem(BaseModel):
    id: Optional[int] = None
    source: str
    title: Optional[str] = None
    url: Optional[str] = None
    content: str
    keywords: List[str] = Field(default_factory=list)


def _get_conn(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: str = DB_PATH):
    conn = _get_conn(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            title TEXT,
            url TEXT,
            content TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def add_item(item: KnowledgeItem, path: str = DB_PATH) -> KnowledgeItem:
    conn = _get_conn(path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO knowledge (source, title, url, content) VALUES (?, ?, ?, ?)",
        (item.source, item.title, item.url, item.content),
    )
    item.id = cur.lastrowid
    # compute and store keywords if present on the model
    if not getattr(item, 'keywords', None):
        item.keywords = extract_keywords(item.title or "" + "\n" + item.content)
    cur.execute(
        "UPDATE knowledge SET keywords = ? WHERE id = ?",
        (",".join(item.keywords), cur.lastrowid),
    )
    conn.commit()
    conn.close()
    return item


def list_items(limit: int = 100, path: str = DB_PATH) -> List[KnowledgeItem]:
    conn = _get_conn(path)
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM knowledge ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    dict_rows = []
    for r in rows:
        d = dict(r)
        kw = d.get("keywords")
        if kw and isinstance(kw, str):
            d["keywords"] = [k for k in kw.split(",") if k]
        else:
            d["keywords"] = []
        dict_rows.append(d)
    items = [KnowledgeItem(**d) for d in dict_rows]
    return items


def _text_score(text: str, query_terms: List[str]) -> int:
    text_lower = text.lower()
    score = 0
    for t in query_terms:
        score += text_lower.count(t)
    return score

# --- Keywords / Indexing helpers ---

# minimal stopword lists (fr + en)
_STOPWORDS = set([
    "et","la","le","les","des","du","de","un","une","pour","avec","sur","dans","par","au","aux","ce","ces","en","à","a","is","the","of","and","in","on","for","with",
])

import re

def extract_keywords(text: str, top_k: int = 10) -> List[str]:
    """Very simple keyword extractor: tokenize, remove stopwords, take most frequent terms (lowercased)."""
    if not text:
        return []
    tokens = re.findall(r"[\wÀ-ÿ']+", text.lower())
    counts = {}
    for t in tokens:
        if len(t) <= 2 or t.isdigit() or t in _STOPWORDS:
            continue
        counts[t] = counts.get(t, 0) + 1
    # sort by frequency and return top_k
    sorted_terms = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [term for term, _ in sorted_terms[:top_k]]


def ensure_keywords_column(path: str = DB_PATH):
    conn = _get_conn(path)
    cur = conn.cursor()
    # check if column exists
    try:
        cur.execute("SELECT keywords FROM knowledge LIMIT 1")
    except sqlite3.OperationalError:
        # need to alter table
        cur.execute("ALTER TABLE knowledge ADD COLUMN keywords TEXT DEFAULT ''")
        conn.commit()
    conn.close()


def query_by_keyword(keyword: str, path: str = DB_PATH, top_k: int = 50) -> List[KnowledgeItem]:
    ensure_keywords_column(path)
    conn = _get_conn(path)
    cur = conn.cursor()
    kw = keyword.lower()
    rows = cur.execute("SELECT * FROM knowledge WHERE lower(keywords) LIKE ? ORDER BY id DESC LIMIT ?", (f"%{kw}%", top_k)).fetchall()
    conn.close()
    dict_rows = []
    for r in rows:
        d = dict(r)
        kw = d.get("keywords")
        if kw and isinstance(kw, str):
            d["keywords"] = [k for k in kw.split(",") if k]
        else:
            d["keywords"] = []
        dict_rows.append(d)
    items = [KnowledgeItem(**d) for d in dict_rows]
    return items


def reindex_all(path: str = DB_PATH) -> int:
    """Recompute keywords for all entries and update the DB. Returns number of updated rows."""
    ensure_keywords_column(path)
    conn = _get_conn(path)
    cur = conn.cursor()
    rows = cur.execute("SELECT id, title, content FROM knowledge").fetchall()
    updated = 0
    for r in rows:
        text = (r["title"] or "") + "\n" + (r["content"] or "")
        kws = extract_keywords(text)
        if kws:
            cur.execute("UPDATE knowledge SET keywords = ? WHERE id = ?", (",".join(kws), r["id"]))
            updated += 1
    conn.commit()
    conn.close()
    return updated


def query_items(query: str, top_k: int = 5, path: str = DB_PATH) -> List[Tuple[KnowledgeItem, int]]:
    """Retourne les meilleurs items par correspondance de mots simples (count-based)."""
    terms = [t.strip().lower() for t in query.split() if t.strip()]
    if not terms:
        return []
    items = list_items(limit=1000, path=path)
    scored = []
    for it in items:
        title = it.title or ""
        content = it.content or ""
        score = _text_score(title, terms) * 3 + _text_score(content, terms)
        if score > 0:
            scored.append((it, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


# --- Ingestion helpers ---

WIKIPEDIA_API_FR = "https://fr.wikipedia.org/api/rest_v1/page/summary/{}"
WIKIPEDIA_API_EN = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"


def fetch_wikipedia(topic: str, lang: str = "fr") -> Optional[KnowledgeItem]:
    """Récupère le résumé d'une page Wikipedia via l'API REST (préférence pour fr)."""
    api = WIKIPEDIA_API_FR if lang == "fr" else WIKIPEDIA_API_EN
    title = topic.replace(" ", "_")
    url = api.format(title)
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        return None
    data = resp.json()
    extract = data.get("extract") or ""
    full_title = data.get("title") or topic
    item = KnowledgeItem(source=f"wikipedia:{lang}", title=full_title, url=data.get("content_urls", {}).get("desktop", {}).get("page"), content=extract)
    return add_item(item)


def _is_allowed_by_robots(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception:
        # En cas d'erreur, être prudent et refuser
        return False


def scrape_site(url: str, selector: Optional[str] = None) -> Optional[KnowledgeItem]:
    """Scrape une page web en respectant robots.txt et extrait le texte principal.
    selector optionnel pour cibler une balise CSS (ex: 'article' ou '#content').
    Le contenu retourné est nettoyé et stocké en tant que KnowledgeItem.
    """
    if not _is_allowed_by_robots(url):
        return None
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "IA-bot/1.0 (+contact)"})
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        if selector:
            elems = soup.select(selector)
        else:
            # Essayer d'extraire les balises d'article sinon tous les <p>
            elems = soup.select("article") or soup.find_all("p")
        text_parts = []
        for e in elems:
            text = e.get_text(separator=" ", strip=True)
            if len(text) > 50:
                text_parts.append(text)
        content = "\n\n".join(text_parts).strip()
        if not content:
            return None
        title = soup.title.string if soup.title else url
        item = KnowledgeItem(source="scrape", title=title, url=url, content=content)
        return add_item(item)
    except Exception as e:
        print("Scrape error:", e)
        return None


def build_from_wikipedia(topics: List[str], lang: str = "fr") -> List[KnowledgeItem]:
    items = []
    for t in topics:
        it = fetch_wikipedia(t, lang=lang)
        if it:
            items.append(it)
    return items


# --- Models for external sources ---

class WeatherInfo(BaseModel):
    lat: float
    lon: float
    weather: str
    temp_c: float
    feels_like_c: float
    humidity: int
    wind_speed: float
    raw: Dict = Field(default_factory=dict)

class IGNInfo(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    coordinates: Optional[Tuple[float, float]] = None
    raw: Dict = Field(default_factory=dict)

class StravaSegment(BaseModel):
    id: int
    name: Optional[str] = None
    climbing_category: Optional[str] = None
    elevation_gain: Optional[float] = None
    distance_m: Optional[float] = None
    raw: Dict = Field(default_factory=dict)


# --- OpenWeatherMap ingestion ---

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY")

def fetch_openweather_by_coords(lat: float, lon: float) -> Optional[KnowledgeItem]:
    if not OPENWEATHER_KEY:
        print("OPENWEATHER_API_KEY not set; skipping OpenWeatherMap ingestion.")
        return None
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY, "units": "metric", "lang": "fr"}
    try:
        time.sleep(1)  # rate-limit
        r = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        if r.status_code != 200:
            print("OpenWeatherMap error:", r.status_code, r.text[:200])
            return None
        data = r.json()
        wi = WeatherInfo(
            lat=data.get("coord", {}).get("lat", lat),
            lon=data.get("coord", {}).get("lon", lon),
            weather=data.get("weather", [{}])[0].get("description", ""),
            temp_c=data.get("main", {}).get("temp"),
            feels_like_c=data.get("main", {}).get("feels_like"),
            humidity=data.get("main", {}).get("humidity"),
            wind_speed=data.get("wind", {}).get("speed"),
            raw=data,
        )
        content = json.dumps(wi.dict(), ensure_ascii=False)
        item = KnowledgeItem(source="openweathermap", title=f"Météo {lat},{lon}", url=None, content=content)
        return add_item(item)
    except Exception as e:
        print("OpenWeather error:", e)
        return None


# --- IGN ingestion (scrape or API wrapper) ---

IGN_API_KEY = os.environ.get("IGN_API_KEY")

def fetch_ign_by_url(url: str, selector: Optional[str] = None) -> Optional[KnowledgeItem]:
    """Scrape an IGN page or use IGN API if configured."""
    # If an IGN API key and a known API endpoint were preferred, implement here.
    # For now, fall back to scraping with the same robots checks.
    if not _is_allowed_by_robots(url):
        print("Robots.txt blocks IGN URL:", url)
        return None
    it = scrape_site(url, selector=selector)
    if it:
        it.source = "ign"
        return it
    return None


# --- Strava ingestion helpers ---

STRAVA_BASE = "https://www.strava.com/api/v3"
STRAVA_TOKEN = os.environ.get("STRAVA_TOKEN")

def fetch_strava_segment(segment_id: int, token: Optional[str] = None) -> Optional[KnowledgeItem]:
    token = token or STRAVA_TOKEN
    if not token:
        print("STRAVA_TOKEN not set; skipping Strava ingestion.")
        return None
    url = f"{STRAVA_BASE}/segments/{segment_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        time.sleep(1)
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print("Strava error:", r.status_code, r.text[:200])
            return None
        data = r.json()
        seg = StravaSegment(
            id=data.get("id"),
            name=data.get("name"),
            climbing_category=data.get("climb_category"),
            elevation_gain=data.get("elevation_high") - data.get("elevation_low") if data.get("elevation_high") and data.get("elevation_low") else data.get("total_elevation_gain"),
            distance_m=data.get("distance"),
            raw=data,
        )
        content = json.dumps(seg.dict(), ensure_ascii=False)
        item = KnowledgeItem(source="strava", title=seg.name or f"Strava segment {segment_id}", url=url, content=content)
        return add_item(item)
    except Exception as e:
        print("Strava fetch error:", e)
        return None


# --- High level ingestion --- 

def ingest_area(
    area_name: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    wikipedia_topics: Optional[List[str]] = None,
    ign_urls: Optional[List[str]] = None,
    strava_segment_ids: Optional[List[int]] = None,
) -> List[KnowledgeItem]:
    """Ingeste différentes sources pour une zone donnée et stocke-les en base."""
    added = []
    # Wikipedia
    if wikipedia_topics:
        added.extend(build_from_wikipedia(wikipedia_topics))
    # OpenWeather by coords
    if lat is not None and lon is not None:
        ow = fetch_openweather_by_coords(lat, lon)
        if ow:
            added.append(ow)
    # IGN URLs
    if ign_urls:
        for u in ign_urls:
            it = fetch_ign_by_url(u)
            if it:
                added.append(it)
    # Strava segments
    if strava_segment_ids:
        for sid in strava_segment_ids:
            it = fetch_strava_segment(sid)
            if it:
                added.append(it)
    return added


# Initialize DB on import if missing
init_db()
# Ensure keywords column exists for older DBs
ensure_keywords_column()
