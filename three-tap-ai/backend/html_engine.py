import os
from bs4 import BeautifulSoup

HTML_PATH = "../data/html"

def load_html_docs():
    docs = []

    for root, dirs, files in os.walk(HTML_PATH):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")
                    text = soup.get_text(separator=" ", strip=True)
                    docs.append(text)

    print("Loaded institute pages:", len(docs))
    return docs
