import os
import subprocess
from memory import add_message, get_history
from knowledge import query_items

OLLAMA_CMD = os.environ.get("OLLAMA_CMD", "ollama")

def ask_llama(prompt):
    """Appel à l'outil Ollama CLI si disponible (configurable via la variable d'env OLLAMA_CMD)."""
    try:
        # Utiliser subprocess.run pour envoyer le prompt en stdin
        result = subprocess.run([OLLAMA_CMD, "run", "llama3"], input=prompt, text=True, capture_output=True, check=False)
        if result.stderr:
            print("Ollama stderr:", result.stderr)
        return (result.stdout or "").strip()
    except FileNotFoundError:
        # Ollama non installé ou commande introuvable
        print("Ollama CLI not found. Please install ollama or set OLLAMA_CMD env var.")
        return "Désolé, le modèle n'est pas disponible localement (Ollama)."  
    except Exception as e:
        print("Error calling Ollama:", e)
        return "Désolé, une erreur est survenue lors de l'appel au modèle."  


def chat_with_llm(user_message):
    """
    Conversation avec mémoire et fin possible, sans répéter le dernier message utilisateur
    """
    # Vérifier si l'utilisateur veut terminer
    end_keywords = ["merci", "c'est tout", "au revoir", "fin de conversation", "terminé"]
    if any(word.lower() in user_message.lower() for word in end_keywords):
        response = "Merci pour cette conversation ! Si vous voulez d'autres conseils sur les randonnées, n'hésitez pas à revenir."
        add_message("user", user_message)
        add_message("assistant", response)
        return response

    # Ajouter le message utilisateur à la mémoire
    add_message("user", user_message)

    # Construire l'historique **sans le dernier message utilisateur**
    history_text = ""
    history = get_history()
    if len(history) > 1:
        for msg in history[:-1]:  # On enlève le dernier message utilisateur
            role = "Utilisateur" if msg["role"] == "user" else "Assistant"
            history_text += f"{role} : {msg['content']}\n"

    # Inclure les connaissances pertinentes (Wikipedia / scrapers)
    relevant = query_items(user_message, top_k=5)
    knowledge_text = ""
    if relevant:
        knowledge_text = "Connaissances pertinentes:\n"
        for it, score in relevant:
            snippet = it.content[:800].replace("\n", " ")
            knowledge_text += f"- {it.title or it.url} ({it.source}): {snippet[:400]}...\n"

    # Prompt principal
    prompt = f"""
Tu es un assistant expert en randonnée et tourisme nature.

Voici les connaissances disponibles :
{knowledge_text}

Voici l'historique de la conversation :
{history_text}

Règles :
- Réponds en français
- Utilise les randonnées déjà citées si l'utilisateur y fait référence
- Sois clair, pratique et réaliste
- Structure toujours ta réponse avec :
  • des titres courts
  • des listes à puces ou numérotées
  • des retours à la ligne
- Utilise du Markdown (titres, listes, paragraphes)
- Si une information manque, pose UNE seule question
- Si l'utilisateur indique qu'il n'a plus de questions, termine la conversation poliment sans relancer.

Message de l'utilisateur :
"{user_message}"

Réponse :
"""

    response = ask_llama(prompt)

    # Ajouter réponse du bot à la mémoire
    add_message("assistant", response)

    return response













