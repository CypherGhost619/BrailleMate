import streamlit as st
import os
from core.preprocess import clean_text, limit_text
from core.summarizer import summarize
from core.braille import to_braille
from core.tts import text_to_speech
from core.extractor import extract_from_url, extract_from_pdf, extract_from_image
import re
def contains_hindi(text):
    return bool(re.search(r'[\u0900-\u097F]', text))


# ---------------- STATE ----------------
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""

if "do_summarize" not in st.session_state:
    st.session_state.do_summarize = False

# ---------------- HELPERS ----------------
def has_real_text(t):
    return bool(t and t.strip() and len(t.strip()) > 20)

# Safe language detection
try:
    from langdetect import detect
except:
    def detect(text): return "en"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="BrailleMate", page_icon="♿", layout="centered")

# ---------------- UI ----------------
st.markdown("""
<style>
.main { background: linear-gradient(135deg, #0b0f14, #0e1117); color: #fafafa; }
.title { font-size: 42px; font-weight: 700; text-align: center; color: #4CAF50; }
.subtitle { text-align: center; color: #bdbdbd; margin-bottom: 30px; }
.card { background: #121821; box-shadow: 0 8px 25px rgba(0,0,0,0.45); padding:20px; border-radius:12px; }
.section { font-size: 22px; font-weight: 600; color: #58a6ff; margin-bottom: 10px; }
.block-container { padding-top: 3.5rem; }
textarea, button { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>BrailleMate</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI Companion for Accessible Reading</div>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")
max_chars = st.sidebar.slider("Max characters to process", 500, 5000, 3000)

# ---------------- INPUT ----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section'>📥 Input</div>", unsafe_allow_html=True)

mode = st.radio("Choose input type:",
                ["Paste Text", "URL", "PDF Upload", "Image (OCR)"],
                horizontal=True)

if mode == "Paste Text":
    temp_text = st.text_area("Enter text:", height=180, key="paste_input")

    # Ctrl+Enter support
    if st.session_state.get("paste_input") is not None:
        st.session_state.raw_text = temp_text

    if st.button("Summarize", use_container_width=True):
        st.session_state.raw_text = temp_text
        st.session_state.do_summarize = False

elif mode == "URL":
    url = st.text_input("Enter URL")
    if st.button("🌐 Fetch URL", use_container_width=True):
        st.session_state.raw_text = extract_from_url(url)
        st.session_state.do_summarize = False

elif mode == "PDF Upload":
    pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf and st.button("📄 Extract PDF", use_container_width=True):
        st.session_state.raw_text = extract_from_pdf(pdf)
        st.session_state.do_summarize = False

elif mode == "Image (OCR)":
    img = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if img and st.button("🖼 OCR Image", use_container_width=True):
        st.session_state.raw_text = extract_from_image(img)
        st.session_state.do_summarize = False

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- OUTPUT ----------------
if has_real_text(st.session_state.raw_text):

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section'>📤 Output</div>", unsafe_allow_html=True)

    text = st.session_state.raw_text.strip()

    st.write("**Extracted Text (Preview)**")
    st.write(text[:1500])

    if st.button("🚀 Summarize", use_container_width=True):
        st.session_state.do_summarize = True

    if st.session_state.do_summarize:

        cleaned = clean_text(text)
        limited = limit_text(cleaned, max_chars)
        if contains_hindi(text):
            summary = text[:max_chars]
        else:
             try:
                 input_lang = detect(text)
             except:
                input_lang = "en"

# Only use AI summarizer for English
             if input_lang != "en":
                summary = text[:max_chars]
             else:
                summary = summarize(limited)


        st.subheader("Summary")
        st.write(summary)

        braille = to_braille(summary)
        st.subheader("Braille Output")
        st.text_area("", braille, height=150)

        try:
            lang = detect(summary)
        except:
            lang = "en"

        audio = text_to_speech(summary, "summary.mp3", lang)

        if audio and os.path.exists(audio):
            with open(audio, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

        st.download_button(
            "⬇ Download Braille (.txt)",
            braille.encode("utf-8"),
            file_name="braille.txt"
        )

    st.markdown("</div>", unsafe_allow_html=True)
