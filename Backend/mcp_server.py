# OLLAMA_PATH = r"C:\Users\Khadija Darkaoui\AppData\Local\Programs\Ollama\ollama.exe"
import subprocess
from memory import add_message, get_history

OLLAMA_PATH = r"C:\Users\Khadija Darkaoui\AppData\Local\Programs\Ollama\ollama.exe"

def ask_llama(prompt):
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
        print("Ollama error:", error)

    return output.strip()


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

    # Prompt principal
    prompt = f"""
Tu es un assistant expert en randonnée et tourisme nature.

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













