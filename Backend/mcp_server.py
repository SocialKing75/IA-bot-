import subprocess
from memory import add_message, get_history
from scraper import scrape_wikipedia, scrape_wikivoyage
from indexer import TextIndexer
from text_cleaner import clean_text

OLLAMA_PATH = r"C:\Users\Khadija Darkaoui\AppData\Local\Programs\Ollama\ollama.exe"


def ask_llama(prompt):
    """
    Envoie un prompt au modèle LLaMA via Ollama
    et retourne la réponse brute du modèle.
    """
    process = subprocess.Popen(
        [OLLAMA_PATH, "run", "llama3"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    output, error = process.communicate(prompt)

    if error:
        print("Erreur Ollama :", error)

    return output.strip()


def extract_location(user_message):
    """
    Utilise l'IA pour extraire dynamiquement
    le lieu principal depuis la question utilisateur.
    """
    prompt = f"""
Extrais uniquement le nom du lieu géographique principal
présent dans cette phrase.

Phrase :
"{user_message}"

Réponds uniquement par le nom du lieu, sans phrase.
"""
    return ask_llama(prompt)


def chat_with_llm(user_message):
    """
    Fonction principale :
    - gère la mémoire
    - déclenche le scraping
    - indexe les données
    - sélectionne les infos pertinentes
    - génère la réponse finale
    """

    # -----------------------------
    # Gestion de fin de conversation
    # -----------------------------
    end_keywords = [
        "merci",
        "c'est tout",
        "au revoir",
        "fin de conversation",
        "terminé"
    ]

    if any(word in user_message.lower() for word in end_keywords):
        response = (
            "Merci pour cette conversation 😊\n\n"
            "N'hésitez pas à revenir si vous avez besoin "
            "d'autres conseils de randonnée ou de voyage."
        )
        add_message("user", user_message)
        add_message("assistant", response)
        return response


    # -----------------------------
    # Sauvegarde du message utilisateur
    # -----------------------------
    add_message("user", user_message)


    # -----------------------------
    # Extraction du lieu par IA
    # -----------------------------
    location = extract_location(user_message)

    # Sécurité si l'IA échoue
    if not location or len(location) < 2:
        location = user_message


    # -----------------------------
    # Scraping dynamique
    # -----------------------------
    wiki_text = scrape_wikipedia(location)
    wikivoyage_text = scrape_wikivoyage(location)

    # Nettoyage des textes scrapés
    wiki_text = clean_text(wiki_text)
    wikivoyage_text = clean_text(wikivoyage_text)


    # -----------------------------
    # Indexation avec Scikit-learn
    # -----------------------------
    indexer = TextIndexer()

    documents = [
        wiki_text,
        wikivoyage_text
    ]

    indexer.add_documents(documents)


    # -----------------------------
    # Recherche par similarité cosinus
    # -----------------------------
    relevant_docs = indexer.search(user_message, top_k=2)

    # Contexte final fourni au modèle
    context = "\n\n".join(relevant_docs)


    # -----------------------------
    # Construction du prompt final
    # -----------------------------
    prompt = f"""
Tu es un assistant expert en randonnée et tourisme nature.

Voici des informations issues de sources touristiques fiables :
{context}

Consignes :
- Réponds en français
- Structure toujours ta réponse avec :
  • des titres
  • des listes à puces ou numérotées
  • des retours à la ligne
- Utilise du Markdown
- Sois clair, concis et pratique
- Ne cite jamais tes sources.
- Tu dois répondre UNIQUEMENT à partir des documents fournis.
- Si l'information n'est pas présente dans les documents, dis :
  "Je n’ai pas trouvé d’informations fiables sur ce point."
- N’invente jamais de lieux, durées ou faits.
- Si le sujet n'est pas une randonnée nature (forêt, montagne, sentier),
  explique poliment que ce n'est pas une randonnée.

Question de l'utilisateur :
"{user_message}"

Réponse :
"""


    # -----------------------------
    # Appel au modèle LLaMA
    # -----------------------------
    response = ask_llama(prompt)


    # -----------------------------
    # Sauvegarde de la réponse
    # -----------------------------
    add_message("assistant", response)

    return response













# # OLLAMA_PATH = r"C:\Users\Khadija Darkaoui\AppData\Local\Programs\Ollama\ollama.exe"
# import subprocess
# from memory import add_message, get_history

# OLLAMA_PATH = r"C:\Users\Khadija Darkaoui\AppData\Local\Programs\Ollama\ollama.exe"

# def ask_llama(prompt):
#     process = subprocess.Popen(
#         [OLLAMA_PATH, "run", "llama3"],
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#         encoding="utf-8"
#     )
#     output, error = process.communicate(prompt)

#     if error:
#         print("Ollama error:", error)

#     return output.strip()


# def chat_with_llm(user_message):
#     """
#     Conversation avec mémoire et fin possible, sans répéter le dernier message utilisateur
#     """
#     # Vérifier si l'utilisateur veut terminer
#     end_keywords = ["merci", "c'est tout", "au revoir", "fin de conversation", "terminé"]
#     if any(word.lower() in user_message.lower() for word in end_keywords):
#         response = "Merci pour cette conversation ! Si vous voulez d'autres conseils sur les randonnées, n'hésitez pas à revenir."
#         add_message("user", user_message)
#         add_message("assistant", response)
#         return response

#     # Ajouter le message utilisateur à la mémoire
#     add_message("user", user_message)

#     # Construire l'historique **sans le dernier message utilisateur**
#     history_text = ""
#     history = get_history()
#     if len(history) > 1:
#         for msg in history[:-1]:  # On enlève le dernier message utilisateur
#             role = "Utilisateur" if msg["role"] == "user" else "Assistant"
#             history_text += f"{role} : {msg['content']}\n"

#     # Prompt principal
#     prompt = f"""
# Tu es un assistant expert en randonnée et tourisme nature.

# Voici l'historique de la conversation :
# {history_text}

# Règles :
# - Réponds en français
# - Utilise les randonnées déjà citées si l'utilisateur y fait référence
# - Sois clair, pratique et réaliste
# - Structure toujours ta réponse avec :
#   • des titres courts
#   • des listes à puces ou numérotées
#   • des retours à la ligne
# - Utilise du Markdown (titres, listes, paragraphes)
# - Si une information manque, pose UNE seule question
# - Si l'utilisateur indique qu'il n'a plus de questions, termine la conversation poliment sans relancer.

# Message de l'utilisateur :
# "{user_message}"

# Réponse :
# """

#     response = ask_llama(prompt)

#     # Ajouter réponse du bot à la mémoire
#     add_message("assistant", response)

#     return response













