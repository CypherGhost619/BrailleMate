import streamlit as st
import os
from core.preprocess import clean_text, limit_text
from core.summarizer import summarize
from core.braille import to_braille
from core.tts import text_to_speech
from core.extractor import extract_from_url, extract_from_pdf, extract_from_image

# GLOBAL SAFE VARIABLES
summary = ""
braille_output = ""

# ---------------- SESSION STATE ----------------
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""

if "do_process" not in st.session_state:
    st.session_state.do_process = False

# ---------------- HELPERS ----------------
def has_real_text(t):
    return bool(t and t.strip() and len(t.strip()) > 20)

# Language detection
try:
    from langdetect import detect
except:
    def detect(text):
        return "en"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="BrailleMate",
    page_icon="♿",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

/* APP BACKGROUND */
.stApp {
    background:
        radial-gradient(circle at top left, rgba(124,58,237,0.08), transparent 35%),
        radial-gradient(circle at bottom right, rgba(0,245,255,0.05), transparent 30%),
        #000000;
    color: white;
}

/* CONTAINER */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* TITLE */
.title {
    font-size: 64px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #8B5CF6, #00F5FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
    text-shadow: 0 0 25px rgba(139,92,246,0.25);
}

/* SUBTITLE */
.subtitle {
    text-align: center;
    font-size: 19px;
    color: #9ca3af;
    margin-bottom: 40px;
}

/* CARDS */
.card {
    background: rgba(8, 8, 12, 0.88);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 28px;
    margin-bottom: 24px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow:
        0 0 25px rgba(124,58,237,0.08),
        0 0 45px rgba(0,245,255,0.04),
        0 10px 40px rgba(0,0,0,0.7);
}

/* SECTION HEADINGS */
.section {
    font-size: 26px;
    font-weight: 800;
    color: #00F5FF;
    margin-bottom: 18px;
    text-shadow: 0 0 10px rgba(0,245,255,0.2);
}

/* FUTURISTIC BUTTONS */
.stButton > button {
    width: 100%;
    height: 62px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.08);
    background: linear-gradient(135deg, rgba(124,58,237,0.95), rgba(6,182,212,0.95));
    color: white;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.4px;
    box-shadow:
        0 0 15px rgba(124,58,237,0.35),
        0 0 30px rgba(6,182,212,0.18);
    transition: all 0.35s ease;
}

.stButton > button:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow:
        0 0 20px rgba(124,58,237,0.5),
        0 0 40px rgba(0,245,255,0.28);
}

/* TEXTAREA */
textarea {
    border-radius: 22px !important;
    background: rgba(5,5,5,0.95) !important;
    color: white !important;
}

/* TABS */
button[data-baseweb="tab"] {
    background: rgba(10,10,10,0.75);
    border-radius: 999px !important;
    color: #d1d5db !important;
    margin-right: 10px;
    border: 1px solid rgba(255,255,255,0.06);
    padding: 12px 24px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #7C3AED, #06B6D4);
    color: white !important;
}

/* AUDIO */
audio {
    width: 100%;
    border-radius: 18px;
    filter: brightness(1.1);
}

/* FOOTER */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='title'>BrailleMate</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Next-Generation AI Accessibility Platform for Digital Inclusion</div>",
    unsafe_allow_html=True
)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Settings")

max_chars = st.sidebar.slider(
    "Max characters to process",
    1000,
    15000,
    10000
)

st.sidebar.markdown("---")
st.sidebar.info("Upload or paste your content and let BrailleMate process it.")

# ---------------- INPUT SECTION ----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section'>Input Source</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Paste Text",
    "🌐 URL",
    "📄 PDF Upload",
    "🖼 Image OCR"
])

# PASTE TEXT
with tab1:
    pasted_text = st.text_area(
        "Enter content:",
        height=250,
        placeholder="Paste your text here..."
    )

    if st.button("Process Text"):
        if pasted_text.strip():
            st.session_state.raw_text = pasted_text
            st.session_state.do_process = True
        else:
            st.warning("Please enter text first.")

# URL
with tab2:
    url = st.text_input(
        "Enter URL:",
        placeholder="https://example.com"
    )

    if st.button("Fetch & Process URL"):
        if url.strip():
            with st.spinner("🌐 Fetching digital content..."):
                try:
                    extracted = extract_from_url(url)
                    st.session_state.raw_text = extracted
                    st.session_state.do_process = True
                    st.success("Website content fetched successfully.")
                except Exception as e:
                    st.error(f"URL extraction failed: {e}")
        else:
            st.warning("Please enter a valid URL.")

# PDF
with tab3:
    pdf_file = st.file_uploader(
        "Upload PDF:",
        type=["pdf"]
    )

    if st.button("Extract & Process PDF"):
        if pdf_file:
            with st.spinner("📄 Reading PDF..."):
                try:
                    extracted = extract_from_pdf(pdf_file)
                    st.session_state.raw_text = extracted
                    st.session_state.do_process = True
                    st.success("PDF extracted successfully.")
                except Exception as e:
                    st.error(f"PDF extraction failed: {e}")
        else:
            st.warning("Please upload a PDF.")

# IMAGE OCR
with tab4:
    image_file = st.file_uploader(
        "Upload image:",
        type=["png", "jpg", "jpeg"]
    )

    if st.button("Extract & Process Image"):
        if image_file:
            with st.spinner("🖼 Running OCR engine..."):
                try:
                    extracted = extract_from_image(image_file)
                    st.session_state.raw_text = extracted
                    st.session_state.do_process = True
                    st.success("OCR extraction completed.")
                except Exception as e:
                    st.error(f"OCR failed: {e}")
        else:
            st.warning("Please upload an image.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- OUTPUT SECTION ----------------
if st.session_state.do_process and has_real_text(st.session_state.raw_text):

    summary = ""
    braille_output = ""

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section'>Output</div>", unsafe_allow_html=True)

    raw_text = st.session_state.raw_text.strip()

    st.write("### Extracted Text Preview")
    st.write(raw_text[:1500])

    # Stats
    c1, c2 = st.columns(2)
    c1.metric("Words", len(raw_text.split()))
    c2.metric("Characters", len(raw_text))

    # Preprocess
    cleaned = clean_text(raw_text)
    limited = limit_text(cleaned, max_chars)

    # Detect language
    try:
        detected_lang = detect(limited)
    except:
        detected_lang = "en"

    # SUMMARY
    with st.spinner("🧠 AI is analyzing your content..."):
        if detected_lang == "en":
            try:
                summary = summarize(limited)
                if not summary or len(summary.strip()) < 100:
                    summary = limited[:5000]
            except: 
                summary = limited[:5000]
        else:
            # Hindi/non-English fallback
            summary = limited[:1200]

    st.success("Processing completed successfully.")

    # Show summary
    st.subheader("Summary")
    st.write(summary)

    # BRAILLE (SUMMARY ONLY)
    with st.spinner("Converting summary to Braille..."):
        try:
            braille_output = to_braille(summary)
        except:
            braille_output = "Braille conversion failed."

    st.subheader("Braille Summary Output")
    st.text_area(
        "Braille Text",
        braille_output,
        height=260
    )

    # AUDIO
    st.subheader("Audio Summary")

    try:
        audio_lang = detect(summary)
    except:
        audio_lang = "en"

    with st.spinner("🔊 Synthesizing speech..."):
        try:
            audio_file = text_to_speech(summary, "summary.mp3", audio_lang)
        except:
            audio_file = None

    if audio_file and os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
    else:
        st.warning("Audio generation unavailable.")

    # DOWNLOADS
    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            "⬇ Download Braille (.txt)",
            braille_output.encode("utf-8"),
            file_name="braille_summary.txt",
            mime="text/plain"
        )

    with d2:
        if summary:
            st.download_button(
                "⬇ Download Summary (.txt)",
                summary.encode("utf-8"),
                file_name="summary.txt",
                mime="text/plain"
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- RESET ----------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button("♻ Reset Session"):
    st.session_state.raw_text = ""
    st.session_state.do_process = False
    st.rerun()

# ---------------- FOOTER ----------------
st.markdown("---")

st.markdown("""
<div style='text-align:center; padding:20px; color:#6b7280; font-size:14px;'>

BrailleMate | Powered by AI • NLP • OCR • Braille Conversion • Text-to-Speech

</div>
""", unsafe_allow_html=True)
