#!/usr/bin/env python3
"""Script d'initialisation de la base de connaissances (KB).
Usage:
  python scripts/seed_kb.py --config config.json
  - ou -
  python scripts/seed_kb.py --topics "Parc national des Écrins" --ign "https://www.ign.fr/" --lat 44.95 --lon 6.3

Le script utilise les variables d'environnement suivantes si nécessaire:
 - OPENWEATHER_API_KEY
 - STRAVA_TOKEN

"""
import argparse
import json
import os
import sys
# allow importing backend modules when run from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Backend")))
from knowledge import ingest_area, list_items


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", help="fichier json décrivant l'aire à ingérer")
    p.add_argument("--topics", help="topics wikipedia, séparés par ;")
    p.add_argument("--ign", help="URLs IGN séparées par ;")
    p.add_argument("--lat", type=float)
    p.add_argument("--lon", type=float)
    p.add_argument("--strava", help="IDs Strava séparés par ;")
    p.add_argument("--reindex", action='store_true', help="Reindex existing KB keywords and exit")
    args = p.parse_args()

    # handle reindex flag early
    if args.reindex:
        from knowledge import reindex_all
        n = reindex_all()
        print(f"Reindexed {n} items")
        return

    cfg = {}
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        if args.topics:
            cfg["wikipedia_topics"] = [t.strip() for t in args.topics.split(";") if t.strip()]
        if args.ign:
            cfg["ign_urls"] = [u.strip() for u in args.ign.split(";") if u.strip()]
        if args.lat is not None and args.lon is not None:
            cfg["lat"] = args.lat
            cfg["lon"] = args.lon
        if args.strava:
            cfg["strava_segment_ids"] = [int(s.strip()) for s in args.strava.split(";") if s.strip()]

    if not cfg:
        print("Aucune configuration fournie. Voir --help")
        return

    print("Starting ingest with config:", json.dumps(cfg, ensure_ascii=False))
    added = ingest_area(
        area_name=cfg.get("area_name"),
        lat=cfg.get("lat"),
        lon=cfg.get("lon"),
        wikipedia_topics=cfg.get("wikipedia_topics"),
        ign_urls=cfg.get("ign_urls"),
        strava_segment_ids=cfg.get("strava_segment_ids"),
    )
    print(f"Added {len(added)} items")
    # print a sample of KB
    for it in list_items(limit=20):
        print(f"- {it.id}: {it.source} - {it.title}")


if __name__ == "__main__":
    main()
