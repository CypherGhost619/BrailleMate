import re

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()

def limit_text(text, max_chars=3000):
    return text[:max_chars]
