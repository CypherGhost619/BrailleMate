from transformers import pipeline

MAX_CHARS = 12000

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

    if _summarizer is None:
        return text[:1200]

    try:
        prompt = f"Generate a detailed summary of this text:\n{text}"

        result = _summarizer(
            prompt,
            max_new_tokens=1500,
            do_sample=False
        )

        return result[0]["generated_text"]

    except Exception:
        return text[:1200]
