from flask import Flask, request, jsonify
from mcp_server import chat_with_llm
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    response = chat_with_llm(user_message)

    # Ne renvoyer que la réponse du bot
    return jsonify({"bot": response})

if __name__ == "__main__":
    app.run(debug=True)













