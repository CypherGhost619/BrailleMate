from transformers import pipeline

_summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

MAX_CHARS = 900

def summarize(text):
    if not text or len(text.strip()) < 50:
        return text

    chunks = [text[i:i+MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]
    summaries = []

    for chunk in chunks[:5]:   # limit to avoid heavy load
        try:
            result = _summarizer(chunk, max_length=120, min_length=40, do_sample=False)
            summaries.append(result[0]["summary_text"])
        except Exception:
            continue

    return " ".join(summaries)
