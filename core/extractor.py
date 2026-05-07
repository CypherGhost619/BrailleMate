import requests
from bs4 import BeautifulSoup
import pdfplumber
from PIL import Image
import pytesseract

def extract_from_url(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return " ".join(p.get_text() for p in soup.find_all("p"))

def extract_from_pdf(file):
    text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text.append(page.extract_text())
    return "\n".join(text)

def extract_from_image(file):
    img = Image.open(file)
    return pytesseract.image_to_string(img)
