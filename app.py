from flask import Flask, request, jsonify
from mcp_server import chat_with_llm

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    response = chat_with_llm(user_message)

    # Ne renvoyer que la réponse du bot
    return jsonify({"bot": response})

if __name__ == "__main__":
    app.run(debug=True)














# from flask import Flask, request, jsonify
# from mcp_server import chat_with_llm

# app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return jsonify({
#         "message": "API Chatbot Randonnée active. Utilise POST /chat"
#     })


# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.get_json()

#     if not data or "message" not in data:
#         return jsonify({"error": "Champ 'message' manquant"}), 400

#     user_message = data["message"]
#     response = chat_with_llm(user_message)

#     return jsonify({
#         "user": user_message,
#         "bot": response
#     })


# if __name__ == "__main__":
#     app.run(
#         host="127.0.0.1",
#         port=5000,
#         debug=True
#     )






# from flask import Flask, request, jsonify
# from scraper import scrape_wikipedia, scrape_wikivoyage
# from mcp_server import summarize_hike, chat_with_llm

# app = Flask(__name__)

# @app.route("/chat", methods=["POST"])
# def chat():
#     user_message = request.json["message"]

#     # Exemple simple : région = Andalousie
#     wiki_content = scrape_wikipedia("Andalousie")
#     voy_content = scrape_wikivoyage("Andalousie")
    
#     combined = wiki_content + "\n" + voy_content

#     response = summarize_hike(combined, user_message)

#     return jsonify({"bot": response})

# if __name__ == "__main__":
#     app.run(debug=True)
