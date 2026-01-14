# IA-bot

## Mise en place de la base de connaissances (KB) 🔧

Le projet fournit des helpers pour ingérer des sources (Wikipedia, pages IGN, OpenWeatherMap, Strava) et stocker des KnowledgeItems dans une base SQLite (`knowledge.db` par défaut).

1. Créez un environnement virtuel et installez les dépendances :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Définissez vos clés d'API dans un `.env` (ou exportez en variables d'environnement) :
- `OPENWEATHER_API_KEY` pour OpenWeatherMap
- `STRAVA_TOKEN` pour Strava
- `IGN_API_KEY` si vous disposez d'une clé IGN

Un fichier exemple `.env.example` est fourni.

3. Démarrer le backend :

```bash
source .venv/bin/activate
python Backend/app.py
```

4. Pour ingérer des données, utilisez l'API `POST /ingest` ou le script de seed :

```bash
# Exemple minimal
curl -X POST -H "Content-Type: application/json" -d '{"wikipedia_topics":["Parc national des Écrins"], "lat":44.95, "lon":6.3, "ign_urls":["https://www.ign.fr/"] }' http://127.0.0.1:5000/ingest

# Ou via le script
python scripts/seed_kb.py --topics "Parc national des Écrins" --ign "https://www.ign.fr/" --lat 44.95 --lon 6.3
```

5. Interroger la KB :

- `GET /knowledge/list?limit=50` — liste des entrées (renvoie aussi `keywords`)
- `GET /knowledge/query?q=mot1+mot2` — recherche par mots clefs simples
- `GET /knowledge/by_keyword?k=mot` — recherche par mot-clé indexé
- `POST /knowledge/reindex` — force la réindexation des mots-clés pour toutes les entrées


---
-