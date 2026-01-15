import re

def clean_text(text):
    text = re.sub(r"\[\d+\]", "", text)      # Supprimer références [1]
    text = re.sub(r"\s+", " ", text)         # Espaces multiples
    text = text.replace("\n", " ").strip()
    return text
