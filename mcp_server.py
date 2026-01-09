# OLLAMA_PATH = r"C:\Users\Khadija Darkaoui\AppData\Local\Programs\Ollama\ollama.exe"


import subprocess
import json

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

    output, _ = process.communicate(prompt)
    return output


def summarize_hike(content, user_request):
    prompt = f"""
Tu es un guide de randonnée professionnel.

Voici des informations extraites d'articles :
{content}

Question utilisateur :
"{user_request}"

Réponds de façon claire et structurée.
Inclure :
- itinéraires possibles
- durée estimée
- niveau de difficulté
- conseils pratiques
"""

    return ask_llama(prompt)



