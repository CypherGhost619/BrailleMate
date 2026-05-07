from transformers import pipeline

MAX_CHARS = 900

try:
    _summarizer = pipeline(
        task="text2text-generation",
        model="google/flan-t5-base"
    )
except Exception:
    _summarizer = None


def summarize(text):

    if not text:
        return "No text provided."

    text = text[:MAX_CHARS]

    # Fallback if model fails
    if _summarizer is None:
        return text[:300]

    try:
        prompt = f"Summarize this text:\n{text}"

        result = _summarizer(
            prompt,
            max_new_tokens=120,
            do_sample=False
        )

        return result[0]["generated_text"]

    except Exception:
        return text[:300]
