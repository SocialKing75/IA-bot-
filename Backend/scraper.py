import requests
from bs4 import BeautifulSoup
from text_cleaner import clean_text

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_wikipedia(page_title):
    url = f"https://fr.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    paragraphs = soup.select("p")
    raw_text = " ".join(p.text for p in paragraphs[:6])

    return clean_text(raw_text)

def scrape_wikivoyage(page_title):
    url = f"https://fr.wikivoyage.org/wiki/{page_title.replace(' ', '_')}"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    content = soup.select("div.mw-parser-output p")
    text = "\n".join(p.text for p in content[:6])

    return clean_text(text)







# import requests
# from bs4 import BeautifulSoup

# HEADERS = {
#     "User-Agent": "Mozilla/5.0"
# }

# def scrape_wikipedia(page_title):
#     url = f"https://fr.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
#     r = requests.get(url, headers=HEADERS)
#     soup = BeautifulSoup(r.text, "html.parser")

#     paragraphs = soup.select("p")
#     text = "\n".join(p.text for p in paragraphs[:5])

#     return text


# def scrape_wikivoyage(page_title):
#     url = f"https://fr.wikivoyage.org/wiki/{page_title.replace(' ', '_')}"
#     r = requests.get(url, headers=HEADERS)
#     soup = BeautifulSoup(r.text, "html.parser")

#     content = soup.select("div.mw-parser-output p")
#     text = "\n".join(p.text for p in content[:6])

#     return text
