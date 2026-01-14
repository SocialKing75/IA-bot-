from flask import Flask, request, jsonify
from mcp_server import chat_with_llm
from knowledge import build_from_wikipedia, scrape_site, query_items, list_items, ingest_area
from strava import set_config as set_strava_config, get_config as get_strava_config, StravaConfig
import strava
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    response = chat_with_llm(user_message)

    # Ne renvoyer que la réponse du bot
    return jsonify({"bot": response})


@app.route("/ingest_wikipedia", methods=["POST"])
def ingest_wikipedia():
    data = request.json or {}
    topics = data.get("topics", [])
    lang = data.get("lang", "fr")
    if not topics:
        return jsonify({"error": "topics is required"}), 400
    items = build_from_wikipedia(topics, lang=lang)
    return jsonify({"added": len(items)})


@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.json or {}
    url = data.get("url")
    selector = data.get("selector")
    if not url:
        return jsonify({"error": "url is required"}), 400
    item = scrape_site(url, selector=selector)
    if not item:
        return jsonify({"error": "failed or disallowed by robots"}), 400
    return jsonify({"id": item.id, "title": item.title})


@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.json or {}
    area_name = data.get("area_name")
    lat = data.get("lat")
    lon = data.get("lon")
    wikipedia_topics = data.get("wikipedia_topics")
    ign_urls = data.get("ign_urls")
    strava_segment_ids = data.get("strava_segment_ids")

    items = ingest_area(
        area_name=area_name,
        lat=lat,
        lon=lon,
        wikipedia_topics=wikipedia_topics,
        ign_urls=ign_urls,
        strava_segment_ids=strava_segment_ids,
    )
    return jsonify({"added": len(items), "items": [{"id": it.id, "source": it.source, "title": it.title} for it in items]})


@app.route("/knowledge/query", methods=["GET"])
def knowledge_query():
    q = request.args.get("q", "")
    if not q:
        return jsonify({"error": "q param required"}), 400
    results = query_items(q, top_k=10)
    return jsonify([{"id": it.id, "title": it.title, "source": it.source, "snippet": it.content[:400]} for it, _ in results])


@app.route("/knowledge/list", methods=["GET"])
def knowledge_list():
    limit = int(request.args.get("limit", 100))
    items = list_items(limit=limit)
    return jsonify([{"id": it.id, "title": it.title, "source": it.source, "url": it.url, "keywords": it.keywords} for it in items])


@app.route("/knowledge/by_keyword", methods=["GET"])
def knowledge_by_keyword():
    k = request.args.get("k", "")
    if not k:
        return jsonify({"error": "k param required"}), 400
    items = query_by_keyword(k, top_k=int(request.args.get("limit", 100)))
    return jsonify([{"id": it.id, "title": it.title, "source": it.source, "url": it.url, "keywords": it.keywords} for it in items])


@app.route("/knowledge/reindex", methods=["POST"])
def knowledge_reindex():
    count = reindex_all()
    return jsonify({"reindexed": count})


@app.route("/strava/config", methods=["POST"])
def strava_config():
    data = request.json or {}
    cfg = strava.StravaConfig(**data)
    set_strava_config(cfg)
    return jsonify({"status": "saved"})


@app.route("/strava/config", methods=["GET"])
def strava_get_config():
    cfg = get_strava_config()
    return jsonify(cfg.dict())


@app.route("/strava/segment/<int:segment_id>", methods=["GET"])
def strava_get_segment(segment_id: int):
    try:
        seg = strava.get_segment(segment_id)
        return jsonify(seg)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)













