from flask import Flask, request, jsonify
from scraper import scrape_wikipedia, scrape_wikivoyage
from mcp_server import summarize_hike

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    # Exemple simple : région = Andalousie
    wiki_content = scrape_wikipedia("Andalousie")
    voy_content = scrape_wikivoyage("Andalousie")

    combined = wiki_content + "\n" + voy_content

    response = summarize_hike(combined, user_message)

    return jsonify({"bot": response})

if __name__ == "__main__":
    app.run(debug=True)
