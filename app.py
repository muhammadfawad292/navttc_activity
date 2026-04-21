import streamlit as st
from google import genai
from PIL import Image
import fitz  # PyMuPDF
import io
import base64

# ──────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Vision Roast System",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# Custom CSS – dark fire aesthetic
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

/* ── Root palette ── */
:root {
    --fire-red:    #FF3D00;
    --fire-orange: #FF6D00;
    --fire-amber:  #FFB300;
    --bg-deep:     #0A0A0F;
    --bg-card:     #13131A;
    --bg-surface:  #1C1C28;
    --border:      rgba(255,109,0,0.25);
    --text-main:   #F0EDE8;
    --text-muted:  #8A8A9A;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    background-color: var(--bg-deep) !important;
    color: var(--text-main) !important;
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 780px !important; }

/* ── Hero header ── */
.hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    position: relative;
}
.hero-header h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(2.6rem, 8vw, 4.2rem);
    letter-spacing: 0.06em;
    background: linear-gradient(135deg, var(--fire-red), var(--fire-orange), var(--fire-amber));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin: 0;
}
.hero-header p {
    color: var(--text-muted);
    font-size: 0.95rem;
    margin-top: 0.6rem;
    letter-spacing: 0.03em;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    transition: border-color 0.25s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--fire-orange) !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] > div {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}
[data-testid="stRadio"] label {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.55rem 1.2rem;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
}
[data-testid="stRadio"] label:hover {
    border-color: var(--fire-orange);
    color: var(--fire-orange) !important;
}

/* ── Text inputs & textareas ── */
input[type="text"], textarea, .stTextInput input, .stTextArea textarea {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-main) !important;
    font-family: 'Inter', sans-serif !important;
}
input[type="text"]:focus, textarea:focus {
    border-color: var(--fire-orange) !important;
    box-shadow: 0 0 0 3px rgba(255,109,0,0.15) !important;
}

/* ── Primary button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, var(--fire-red), var(--fire-orange)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.25rem !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
    transition: all 0.25s;
    box-shadow: 0 4px 24px rgba(255,61,0,0.35);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(255,109,0,0.5);
}
.stButton > button:active { transform: translateY(0); }

/* ── Result cards ── */
.result-card {
    background: var(--bg-card);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    border: 1px solid var(--border);
}
.result-card-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.35rem;
    letter-spacing: 0.08em;
    margin-bottom: 0.75rem;
}
.roast-title  { color: var(--fire-red); }
.suggest-title{ color: var(--fire-orange); }
.design-title { color: var(--fire-amber); }
.result-card p, .result-card li { font-size: 0.93rem; line-height: 1.7; color: var(--text-main); }
.result-card ul { padding-left: 1.2rem; margin: 0; }

/* ── Divider ── */
.styled-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--fire-orange), transparent);
    margin: 1.8rem 0;
    border: none;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
}

/* ── Spinner override ── */
.stSpinner > div { border-top-color: var(--fire-orange) !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Gemini setup (Streamlit Secrets)
# ──────────────────────────────────────────────
def configure_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception:
        st.error(
            "⚠️ **Gemini API key not found.** "
            "Add `GEMINI_API_KEY` to your Streamlit Secrets "
            "(*Settings → Secrets* in Streamlit Community Cloud)."
        )
        return False


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def pdf_to_image(pdf_bytes: bytes) -> Image.Image:
    """Render first page of a PDF as a PIL Image."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    mat = fitz.Matrix(2.0, 2.0)          # 2× zoom for clarity
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    return Image.open(io.BytesIO(img_bytes))


def image_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def build_prompt(design_type: str, brand_name: str, industry: str, extra_context: str) -> str:
    context_block = ""
    if brand_name:
        context_block += f"\n- Brand / Company Name: {brand_name}"
    if industry:
        context_block += f"\n- Industry / Niche: {industry}"
    if extra_context:
        context_block += f"\n- Additional context: {extra_context}"

    return f"""You are a brutally honest yet brilliant design critic with 20 years of experience.

The user has uploaded a **{design_type}** design for your review.{context_block}

Your task has TWO parts:

---

### PART 1 — 🔥 THE ROAST (keep it fun, sharp, witty, 3-5 sentences)
Roast this {design_type} like a comedian. Point out obvious flaws, questionable choices, or dated aesthetics — all in good fun. Be clever, not cruel. Use specific design observations.

---

### PART 2 — 🎯 PROFESSIONAL FEEDBACK

#### Suggestions (bullet list, 4-6 points):
Provide actionable, specific improvement suggestions covering typography, layout, color usage, visual hierarchy, spacing, and brand alignment.

#### Design Improvements (bullet list, 3-5 points):
Recommend concrete design upgrades: fonts to consider, color palette improvements, modern techniques, or compositional fixes.

---

Format your response EXACTLY like this (use these exact section headers):

🔥 ROAST:
<roast text here>

🎯 SUGGESTIONS:
• <suggestion 1>
• <suggestion 2>
...

🎨 DESIGN IMPROVEMENTS:
• <improvement 1>
• <improvement 2>
...
"""


def parse_response(text: str) -> dict:
    """Split raw Gemini text into roast / suggestions / improvements."""
    sections = {"roast": "", "suggestions": "", "improvements": ""}

    roast_start     = text.find("🔥 ROAST:")
    suggest_start   = text.find("🎯 SUGGESTIONS:")
    design_start    = text.find("🎨 DESIGN IMPROVEMENTS:")

    if roast_start != -1:
        end = suggest_start if suggest_start != -1 else len(text)
        sections["roast"] = text[roast_start + len("🔥 ROAST:"):end].strip()

    if suggest_start != -1:
        end = design_start if design_start != -1 else len(text)
        sections["suggestions"] = text[suggest_start + len("🎯 SUGGESTIONS:"):end].strip()

    if design_start != -1:
        sections["improvements"] = text[design_start + len("🎨 DESIGN IMPROVEMENTS:"):].strip()

    # Fallback: show full text in roast field
    if not any(sections.values()):
        sections["roast"] = text

    return sections


def call_gemini(image: Image.Image, prompt: str) -> str:
    # ── MODEL PLACEHOLDER ──────────────────────────
    # Change model name here when Gemini 2.5 Flash
    # becomes available on your API tier, e.g.:
    #   model_name = "gemini-2.5-flash"
    MODEL_NAME = "gemini-2.5-flash"   # ← swap model here
    # ───────────────────────────────────────────────

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content([prompt, image])
    return response.text


# ──────────────────────────────────────────────
# UI
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <h1>🔥 AI Vision Roast System</h1>
  <p>Upload your logo or banner — we'll roast it, then actually help you fix it.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

# ── File upload ──
st.markdown('<div class="section-label">Upload Design</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="",
    type=["png", "jpg", "jpeg", "webp", "pdf"],
    help="Supported formats: PNG, JPG, JPEG, WEBP, PDF",
    label_visibility="collapsed",
)

# ── Design type ──
st.markdown('<div class="section-label" style="margin-top:1.2rem;">Design Type</div>', unsafe_allow_html=True)
design_type = st.radio(
    label="",
    options=["Logo", "Banner"],
    horizontal=True,
    label_visibility="collapsed",
)

# ── Optional context ──
st.markdown('<div class="section-label" style="margin-top:1.2rem;">Optional Context <span style="font-weight:300;font-size:0.65rem;">(helps get better feedback)</span></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    brand_name = st.text_input("Brand / Company Name", placeholder="e.g. Nova Coffee Co.", label_visibility="visible")
with col2:
    industry = st.text_input("Industry / Niche", placeholder="e.g. Tech Startup, Bakery", label_visibility="visible")

extra_context = st.text_area(
    "Additional Notes",
    placeholder="Target audience, brand values, anything the AI should know...",
    height=90,
    label_visibility="visible",
)

st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)

# ── Analyze button ──
analyze_clicked = st.button("🔥 Analyze Design", use_container_width=True)

# ──────────────────────────────────────────────
# Analysis logic
# ──────────────────────────────────────────────
if analyze_clicked:
    if not uploaded_file:
        st.warning("⚠️ Please upload an image or PDF first.")
    elif not configure_gemini():
        pass  # error already shown
    else:
        # Load image
        with st.spinner("Processing your design..."):
            try:
                file_bytes = uploaded_file.read()
                if uploaded_file.type == "application/pdf":
                    image = pdf_to_image(file_bytes)
                else:
                    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            except Exception as e:
                st.error(f"❌ Failed to load file: {e}")
                st.stop()

        # Preview
        st.markdown('<div class="section-label">Your Design</div>', unsafe_allow_html=True)
        preview_col, _ = st.columns([1, 1])
        with preview_col:
            st.image(image, use_container_width=True)

        st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🔍 Analysis Result</div>', unsafe_allow_html=True)

        # Call Gemini
        with st.spinner("Roasting your design... 🔥"):
            try:
                prompt  = build_prompt(design_type, brand_name, industry, extra_context)
                raw     = call_gemini(image, prompt)
                parsed  = parse_response(raw)
            except Exception as e:
                st.error(f"❌ Gemini API error: {e}")
                st.stop()

        # ── Roast card ──
        if parsed["roast"]:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title roast-title">🔥 Roast Feedback</div>
                <p>{parsed["roast"]}</p>
            </div>
            """, unsafe_allow_html=True)

        # ── Suggestions card ──
        if parsed["suggestions"]:
            lines = [l.strip() for l in parsed["suggestions"].splitlines() if l.strip()]
            items = "".join(f"<li>{l.lstrip('•·-- ').strip()}</li>" for l in lines)
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title suggest-title">🎯 Suggestions</div>
                <ul>{items}</ul>
            </div>
            """, unsafe_allow_html=True)

        # ── Design improvements card ──
        if parsed["improvements"]:
            lines = [l.strip() for l in parsed["improvements"].splitlines() if l.strip()]
            items = "".join(f"<li>{l.lstrip('•·-- ').strip()}</li>" for l in lines)
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-title design-title">🎨 Design Improvements</div>
                <ul>{items}</ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="styled-divider">', unsafe_allow_html=True)
        st.success("✅ Analysis complete! Use the feedback above to level up your design.")
        
