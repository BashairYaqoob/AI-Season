"""
Streamlit frontend for the Multimodal RAG system built on
"Attention Is All You Need".

IMPORTANT: This file only adds a UI layer on top of the existing
backend (multimodal_rag.py). It imports the backend's functions
directly and never redefines the extraction / embedding / retrieval
logic — the backend is untouched.

Theme: "Bright AI Research Observatory" — Apple / Notion / Arc / Linear /
Stripe crossed with a NASA research observatory. Light, airy, glassy,
no dark mode, no chatbot look.

Run with:
    streamlit run app.py

Requirements (in addition to your existing backend deps):
    pip install streamlit

Make sure, in the same folder:
    - multimodal_rag.py            (your backend, unchanged)
    - AttentionIsAllYouNeed.pdf    (the source PDF)
    - .env with GEMINI_API_KEY=... (loaded by the backend via dotenv)
"""

import time

import streamlit as st
import chromadb

import multimodal_rag as rag  # your existing backend, untouched

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Research Observatory · Attention Is All You Need",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Design tokens
# ------------------------------------------------------------------
PRIMARY = "#4F8EF7"
ACCENT = "#6C63FF"
SECONDARY = "#8BD3FF"
BG = "#F8FBFF"
CARD = "#FFFFFF"
BORDER = "#E7ECF5"
SUCCESS = "#4CAF82"
WARNING = "#E8A93B"
ERROR = "#E5675F"
TEXT_DARK = "#1B2430"
TEXT_MUTED = "#6B7A90"

TYPE_ICON = {
    "text": "📄",
    "heading": "🏷️",
    "table": "📊",
    "figure": "🖼️",
}

TYPE_COLOR = {
    "text": PRIMARY,
    "heading": ACCENT,
    "table": WARNING,
    "figure": SECONDARY,
}

# Chip label -> full query text sent to the backend
SAMPLE_CHIPS = {
    "Explain Transformer Architecture": "Explain the Transformer architecture.",
    "What is Multi-Head Attention?": "What is Multi-Head Attention?",
    "BLEU Scores": "What BLEU score did the Transformer achieve?",
    "Encoder Decoder": "Describe the encoder-decoder architecture shown in the figure.",
}

PIPELINE_STAGES = [
    ("Query", "🔎"),
    ("Embedding", "🧬"),
    ("Vector Search", "🗂️"),
    ("Retrieved Context", "📚"),
    ("Gemini", "✨"),
    ("Grounded Answer", "🎯"),
]

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "attention_paper"


# ==================================================================
# CSS
# ==================================================================
def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background: radial-gradient(circle at 15% 0%, #EEF5FF 0%, {BG} 45%, {BG} 100%);
        }}

        h1, h2, h3, .observatory-title {{
            font-family: 'Space Grotesk', sans-serif;
        }}

        #MainMenu, header, footer {{visibility: hidden;}}

        /* ---------- Hero ---------- */
        .hero-wrap {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 2.5rem;
            padding: 2.5rem 0 1.5rem 0;
            flex-wrap: wrap;
        }}
        .hero-eyebrow {{
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {ACCENT};
            background: rgba(108, 99, 255, 0.08);
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
            margin-bottom: 0.9rem;
        }}
        .observatory-title {{
            font-size: 3.1rem;
            font-weight: 700;
            line-height: 1.05;
            color: {TEXT_DARK};
            margin: 0;
            background: linear-gradient(100deg, {TEXT_DARK} 40%, {ACCENT} 100%);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero-sub {{
            font-size: 1.08rem;
            color: {TEXT_MUTED};
            max-width: 34rem;
            margin-top: 0.9rem;
            line-height: 1.55;
        }}
        .badge-row {{
            display: flex;
            gap: 0.6rem;
            margin-top: 1.6rem;
            flex-wrap: wrap;
        }}
        .badge {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 999px;
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            font-weight: 500;
            color: {TEXT_DARK};
            box-shadow: 0 6px 18px rgba(79, 142, 247, 0.08);
            animation: floatY 5s ease-in-out infinite;
        }}
        .badge:nth-child(2) {{ animation-delay: 0.6s; }}
        .badge:nth-child(3) {{ animation-delay: 1.2s; }}
        .badge:nth-child(4) {{ animation-delay: 1.8s; }}

        @keyframes floatY {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-6px); }}
        }}

        .hero-illustration {{ flex-shrink: 0; }}

        @keyframes spinSlow {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        @keyframes pulseSoft {{
            0%, 100% {{ opacity: 0.55; }}
            50% {{ opacity: 1; }}
        }}
        .orbit-group {{ animation: spinSlow 34s linear infinite; transform-origin: 160px 140px; }}
        .particle {{ animation: pulseSoft 3.5s ease-in-out infinite; }}

        /* ---------- Glass card ---------- */
        .glass-card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(79, 142, 247, 0.07);
            padding: 1.6rem 1.8rem;
        }}

        /* ---------- Pipeline ---------- */
        .pipeline-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.3rem;
            margin: 1.4rem 0 0.4rem 0;
            flex-wrap: nowrap;
            overflow-x: auto;
        }}
        .pipe-stage {{
            flex: 1;
            min-width: 118px;
            text-align: center;
            border-radius: 16px;
            padding: 0.85rem 0.4rem;
            border: 1px solid {BORDER};
            background: #FBFDFF;
            color: {TEXT_MUTED};
            font-size: 0.8rem;
            font-weight: 600;
            transition: all 0.4s ease;
        }}
        .pipe-stage .pipe-icon {{ font-size: 1.15rem; display: block; margin-bottom: 0.25rem; }}
        .pipe-stage.done {{
            background: rgba(76, 175, 130, 0.09);
            border-color: rgba(76, 175, 130, 0.35);
            color: {SUCCESS};
        }}
        .pipe-stage.active {{
            background: linear-gradient(135deg, {PRIMARY}, {ACCENT});
            border-color: transparent;
            color: white;
            box-shadow: 0 8px 20px rgba(108, 99, 255, 0.35);
            animation: pulseSoft 1.6s ease-in-out infinite;
        }}
        .pipe-arrow {{ color: {BORDER}; font-size: 1.1rem; padding: 0 0.15rem; }}

        /* ---------- Search card ---------- */
        .search-card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 24px;
            padding: 2rem 2.2rem 1.4rem 2.2rem;
            box-shadow: 0 16px 40px rgba(79, 142, 247, 0.1);
            text-align: center;
        }}
        div[data-testid="stTextInput"] input {{
            border-radius: 999px !important;
            border: 1px solid {BORDER} !important;
            padding: 0.85rem 1.3rem !important;
            font-size: 1rem !important;
            background: #FBFDFF !important;
            color: {TEXT_DARK} !important;
        }}
        div[data-testid="stTextInput"] input::placeholder {{
            color: {TEXT_MUTED} !important;
            opacity: 1;
        }}
        div[data-testid="stTextInput"] input:focus {{
            border-color: {ACCENT} !important;
            box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.15) !important;
        }}

        /* Buttons -> gradient pill look (chips, search, sources, etc.) */
        .stButton > button {{
            border-radius: 999px;
            border: 1px solid {BORDER};
            background: #FBFDFF;
            color: {TEXT_DARK};
            font-weight: 500;
            padding: 0.45rem 1.1rem;
            transition: all 0.25s ease;
        }}
        .stButton > button:hover {{
            border-color: {ACCENT};
            color: {ACCENT};
            transform: translateY(-1px);
        }}
        .stButton > button[kind="primary"] {{
            background: linear-gradient(120deg, {PRIMARY}, {ACCENT});
            border: none;
            color: white;
            font-weight: 600;
            box-shadow: 0 10px 24px rgba(108, 99, 255, 0.3);
        }}
        .stButton > button[kind="primary"]:hover {{
            filter: brightness(1.06);
            transform: translateY(-1px);
            color: white;
        }}

        /* ---------- Context cards ---------- */
        .context-card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 6px 16px rgba(20, 30, 60, 0.05);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
            animation: slideUp 0.5s ease both;
        }}
        .context-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 14px 28px rgba(20, 30, 60, 0.1);
        }}
        @keyframes slideUp {{
            from {{ opacity: 0; transform: translateY(14px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .tag {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            color: white;
            margin-bottom: 0.5rem;
        }}
        .context-preview {{
            font-size: 0.9rem;
            color: {TEXT_MUTED};
            line-height: 1.5;
        }}
        .context-page {{
            font-size: 0.78rem;
            color: {TEXT_MUTED};
            float: right;
        }}

        /* ---------- Answer card ---------- */
        .answer-card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 22px;
            box-shadow: 0 20px 45px rgba(79, 142, 247, 0.12);
            overflow: hidden;
            animation: slideUp 0.6s ease both;
        }}
        .answer-header {{
            background: linear-gradient(120deg, {PRIMARY}, {ACCENT});
            color: white;
            padding: 1.1rem 1.6rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.15rem;
        }}
        .answer-body {{
            padding: 1.6rem 1.9rem;
            font-size: 1.02rem;
            line-height: 1.7;
            color: {TEXT_DARK};
            max-width: 46rem;
        }}

        /* ---------- Stat cards ---------- */
        .stat-card {{
            border-radius: 16px;
            padding: 0.9rem 1rem;
            text-align: center;
            color: white;
            font-family: 'Space Grotesk', sans-serif;
        }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; }}
        .stat-label {{ font-size: 0.75rem; opacity: 0.9; }}

        /* ---------- Timeline ---------- */
        .timeline-item {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.5rem 0;
            font-size: 0.9rem;
            color: {TEXT_MUTED};
        }}
        .timeline-item.done {{ color: {TEXT_DARK}; font-weight: 500; }}
        .timeline-check {{
            width: 22px; height: 22px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.75rem;
            border: 1px solid {BORDER};
            background: #FBFDFF;
            color: {TEXT_MUTED};
        }}
        .timeline-item.done .timeline-check {{
            background: {SUCCESS};
            border-color: {SUCCESS};
            color: white;
        }}

        /* ---------- Pills (recent searches) ---------- */
        .pill-label {{
            font-size: 0.78rem;
            color: {TEXT_MUTED};
            margin-bottom: 0.4rem;
        }}

        /* Section headers */
        .section-eyebrow {{
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {ACCENT};
            margin-bottom: 0.3rem;
        }}
        .section-title {{
            font-size: 1.4rem;
            font-weight: 700;
            color: {TEXT_DARK};
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 0.8rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero_illustration_svg():
    return f"""
    <div class="hero-illustration">
    <svg width="320" height="280" viewBox="0 0 320 280" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="paperGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{SECONDARY}"/>
          <stop offset="100%" stop-color="{PRIMARY}"/>
        </linearGradient>
        <linearGradient id="nodeGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{ACCENT}"/>
          <stop offset="100%" stop-color="{PRIMARY}"/>
        </linearGradient>
      </defs>

      <!-- floating paper -->
      <rect x="118" y="90" width="90" height="112" rx="10" fill="white" stroke="url(#paperGrad)" stroke-width="2.5"/>
      <line x1="132" y1="112" x2="194" y2="112" stroke="{BORDER}" stroke-width="3"/>
      <line x1="132" y1="128" x2="194" y2="128" stroke="{BORDER}" stroke-width="3"/>
      <line x1="132" y1="144" x2="176" y2="144" stroke="{BORDER}" stroke-width="3"/>
      <line x1="132" y1="166" x2="194" y2="166" stroke="{BORDER}" stroke-width="3"/>
      <line x1="132" y1="182" x2="170" y2="182" stroke="{BORDER}" stroke-width="3"/>

      <!-- connection lines -->
      <g stroke="{SECONDARY}" stroke-width="1.4" stroke-dasharray="3 4" opacity="0.75">
        <line x1="163" y1="146" x2="60" y2="70"/>
        <line x1="163" y1="146" x2="270" y2="60"/>
        <line x1="163" y1="146" x2="50" y2="210"/>
        <line x1="163" y1="146" x2="265" y2="220"/>
      </g>

      <!-- orbiting data nodes -->
      <g class="orbit-group">
        <circle class="particle" cx="60" cy="70" r="9" fill="url(#nodeGrad)"/>
        <circle class="particle" cx="270" cy="60" r="7" fill="{SECONDARY}"/>
        <circle class="particle" cx="50" cy="210" r="6" fill="{ACCENT}"/>
        <circle class="particle" cx="265" cy="220" r="8" fill="{PRIMARY}"/>
      </g>

      <!-- small ambient particles -->
      <circle class="particle" cx="20" cy="140" r="3" fill="{SECONDARY}"/>
      <circle class="particle" cx="300" cy="140" r="3" fill="{ACCENT}"/>
      <circle class="particle" cx="160" cy="20" r="3" fill="{PRIMARY}"/>
    </svg>
    </div>
    """


def render_pipeline(active_stage: int):
    """active_stage: 0 = idle, 1..len(stages) = which stage is currently active
    (all stages before it are marked done)."""
    parts = ['<div class="pipeline-row">']
    for i, (label, icon) in enumerate(PIPELINE_STAGES, start=1):
        cls = "pipe-stage"
        if active_stage and i < active_stage:
            cls += " done"
        elif active_stage and i == active_stage:
            cls += " active"
        parts.append(
            f'<div class="{cls}"><span class="pipe-icon">{icon}</span>{label}</div>'
        )
        if i != len(PIPELINE_STAGES):
            parts.append('<span class="pipe-arrow">→</span>')
    parts.append("</div>")
    return "".join(parts)


def stat_card(value, label, color):
    return f"""
    <div class="stat-card" style="background: linear-gradient(135deg, {color}, {color}CC);">
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """


# ==================================================================
# Knowledge base helpers
# ==================================================================
@st.cache_resource(show_spinner=False)
def get_existing_collection():
    """Return the chroma collection if one already exists & is populated."""
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        collection = chroma.get_collection(COLLECTION_NAME)
        if collection.count() > 0:
            return collection
    except Exception:
        pass
    return None


TIMELINE_STEPS = [
    "Images extracted",
    "Gemini Vision completed",
    "Text extracted",
    "Tables extracted",
    "Embeddings generated",
    "ChromaDB ready",
]


def render_timeline(done_count: int):
    parts = ['<div class="glass-card">']
    for i, step in enumerate(TIMELINE_STEPS, start=1):
        cls = "timeline-item done" if i <= done_count else "timeline-item"
        check = "✓" if i <= done_count else "•"
        parts.append(
            f'<div class="{cls}"><span class="timeline-check">{check}</span>{step}</div>'
        )
    parts.append("</div>")
    return "".join(parts)


def build_knowledge_base(timeline_placeholder):
    timeline_placeholder.markdown(render_timeline(0), unsafe_allow_html=True)

    image_info = rag.extract_images()
    timeline_placeholder.markdown(render_timeline(1), unsafe_allow_html=True)

    figure_docs = rag.describe_images(image_info)
    timeline_placeholder.markdown(render_timeline(2), unsafe_allow_html=True)

    text_docs = rag.extract_text()
    timeline_placeholder.markdown(render_timeline(3), unsafe_allow_html=True)

    table_docs = rag.extract_tables()
    timeline_placeholder.markdown(render_timeline(4), unsafe_allow_html=True)

    documents = []
    documents.extend(text_docs)
    documents.extend(table_docs)
    documents.extend(figure_docs)

    collection = rag.build_vector_store(documents)
    timeline_placeholder.markdown(render_timeline(5), unsafe_allow_html=True)
    timeline_placeholder.markdown(render_timeline(6), unsafe_allow_html=True)

    return collection, documents


def get_stats(documents=None, collection=None):
    """Simple per-type counts for the knowledge base dashboard."""
    counts = {"text": 0, "heading": 0, "table": 0, "figure": 0}
    if documents is not None:
        for d in documents:
            counts[d["type"]] = counts.get(d["type"], 0) + 1
        return counts
    if collection is not None:
        for m in collection.get()["metadatas"]:
            counts[m["type"]] = counts.get(m["type"], 0) + 1
        return counts
    return counts


# ------------------------------------------------------------------
# Query + grounded answer
# (mirrors rag.answer_question, but returns data instead of printing
# it, and updates the pipeline visualization as it goes — no backend
# logic is duplicated/changed, this just calls the same
# retrieve_documents() + the same Gemini call)
# ------------------------------------------------------------------
def run_query(question, collection, pipeline_placeholder, k=5):
    start = time.time()

    pipeline_placeholder.markdown(render_pipeline(1), unsafe_allow_html=True)
    time.sleep(0.25)

    pipeline_placeholder.markdown(render_pipeline(2), unsafe_allow_html=True)
    results = rag.retrieve_documents(question, collection, k=k)

    pipeline_placeholder.markdown(render_pipeline(3), unsafe_allow_html=True)
    docs = results["documents"][0]
    metadata = results["metadatas"][0]

    pipeline_placeholder.markdown(render_pipeline(4), unsafe_allow_html=True)
    context = ""
    retrieved = []
    for doc, meta in zip(docs, metadata):
        retrieved.append({
            "type": meta["type"],
            "page": meta["page"],
            "content": doc,
            "path": meta.get("path", ""),
        })
        context += doc + "\n\n"
    time.sleep(0.2)

    pipeline_placeholder.markdown(render_pipeline(5), unsafe_allow_html=True)
    response = rag.client.models.generate_content(
        model=rag.MODEL,
        contents=f"""
Context:
{context}
Question:
{question}

Instructions:
- Answer ONLY using the retrieved context.
- Do not use outside knowledge.
- If the answer cannot be found in the context, reply:
  "The retrieved context does not contain enough information."
- Mention the relevant page numbers if possible.
"""
    )

    pipeline_placeholder.markdown(render_pipeline(6), unsafe_allow_html=True)
    elapsed = time.time() - start
    return retrieved, response.text, elapsed


# ==================================================================
# Session state
# ==================================================================
if "collection" not in st.session_state:
    st.session_state.collection = None
if "documents" not in st.session_state:
    st.session_state.documents = None
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None  # (question, retrieved, answer, elapsed)

if st.session_state.collection is None:
    existing = get_existing_collection()
    if existing is not None:
        st.session_state.collection = existing

inject_css()

# ==================================================================
# Sidebar — Knowledge base dashboard
# ==================================================================
with st.sidebar:
    st.markdown(
        f"""<div style="font-family:'Space Grotesk',sans-serif;font-size:1.3rem;
        font-weight:700;color:{TEXT_MUTED};">🧠 Research Observatory</div>
        <div style="color:{TEXT_MUTED};font-size:0.85rem;margin-bottom:1rem;">
        Attention Is All You Need --> knowledge base</div>""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown('<div class="section-eyebrow">Knowledge base</div>', unsafe_allow_html=True)

    if st.session_state.collection is not None:
        stats = get_stats(documents=st.session_state.documents, collection=st.session_state.collection)
        total = sum(stats.values())

        st.markdown(
            f"""<div style="background:rgba(76,175,130,0.1);border:1px solid rgba(76,175,130,0.35);
            border-radius:12px;padding:0.6rem 0.9rem;margin-bottom:0.9rem;color:{SUCCESS};
            font-weight:600;font-size:0.85rem;">● Live Vector Store · Ready</div>""",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(stat_card(total, "Total Documents", PRIMARY), unsafe_allow_html=True)
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
            st.markdown(stat_card(stats.get("table", 0), "Tables", WARNING), unsafe_allow_html=True)
        with c2:
            st.markdown(stat_card(stats.get("text", 0) + stats.get("heading", 0), "Text Chunks", ACCENT), unsafe_allow_html=True)
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
            st.markdown(stat_card(stats.get("figure", 0), "Figures", SECONDARY), unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        if st.button("🔁 Rebuild knowledge base", use_container_width=True):
            st.session_state.collection = None
            st.session_state.documents = None
            get_existing_collection.clear()
            st.rerun()
    else:
        st.warning("No vector store found yet.")
        if st.button("🚀 Build knowledge base", type="primary", use_container_width=True):
            timeline_placeholder = st.empty()
            with st.spinner("Running full pipeline (this can take a few minutes)..."):
                collection, documents = build_knowledge_base(timeline_placeholder)
            st.session_state.collection = collection
            st.session_state.documents = documents
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-eyebrow">Recent searches</div>', unsafe_allow_html=True)
    if st.session_state.history:
        for q in reversed(st.session_state.history[-6:]):
            if st.button(f"↺ {q[:40]}{'...' if len(q) > 40 else ''}", key=f"pill_{hash(q)}", use_container_width=True):
                st.session_state.pending_query = q
                st.rerun()
    else:
        st.caption("No queries yet.")

# ==================================================================
# Hero
# ==================================================================
hero_left, hero_right = st.columns([2.1, 1])
with hero_left:
    st.markdown(
        f"""
        <div class="hero-eyebrow">Multimodal RAG · Gemini + ChromaDB</div>
        <div class="observatory-title">Research Observatory</div>
        <div class="hero-sub">Explore the Transformer paper 'Attention is all you Need' through intelligent multimodal
        retrieval — text, tables, and figures embedded in one shared space and
        answered with grounded, page-cited context.</div>
        <div class="badge-row">
            <div class="badge">📄 Text</div>
            <div class="badge">🖼 Figures</div>
            <div class="badge">📊 Tables</div>
            <div class="badge">🧠 Semantic Search</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with hero_right:
    st.markdown(hero_illustration_svg(), unsafe_allow_html=True)

st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

if st.session_state.collection is None:
    st.info("👈 Build the knowledge base from the sidebar first — it extracts text, "
            "tables & figures from the paper, then embeds everything into one vector store.")
    st.stop()

# ==================================================================
# Pipeline visualization (idle state until a query runs)
# ==================================================================
st.markdown('<div class="section-eyebrow">How it works</div>', unsafe_allow_html=True)
pipeline_placeholder = st.empty()
pipeline_placeholder.markdown(render_pipeline(0), unsafe_allow_html=True)

st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)

# ==================================================================
# Search section
# ==================================================================
st.markdown('<div class="search-card">', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-title">Ask the paper</div>',
    unsafe_allow_html=True,
)

question = st.text_input(
    "Ask anything about the Transformer paper...",
    value=st.session_state.pending_query,
    placeholder="e.g. What BLEU score did the Transformer achieve?",
    label_visibility="collapsed",
)

st.markdown('<div class="pill-label">Try a sample query</div>', unsafe_allow_html=True)
chip_cols = st.columns(len(SAMPLE_CHIPS))
clicked_query = None
for col, (label, full_q) in zip(chip_cols, SAMPLE_CHIPS.items()):
    with col:
        if st.button(label, key=f"chip_{label}", use_container_width=True):
            clicked_query = full_q

k = st.slider("Number of retrieved chunks", min_value=3, max_value=10, value=5)
ask = st.button("🔭 Search", type="primary", use_container_width=True) or clicked_query is not None
st.markdown("</div>", unsafe_allow_html=True)

if clicked_query is not None:
    question = clicked_query
    st.session_state.pending_query = clicked_query

# ==================================================================
# Run search
# ==================================================================
if ask and question and question.strip():
    st.session_state.history.append(question.strip())
    st.session_state.pending_query = ""

    with st.spinner("Retrieving context and generating a grounded answer..."):
        retrieved, answer, elapsed = run_query(
            question.strip(), st.session_state.collection, pipeline_placeholder, k=k
        )
    st.session_state.last_result = (question.strip(), retrieved, answer, elapsed)

# ==================================================================
# Results
# ==================================================================
if st.session_state.last_result:
    q, retrieved, answer, elapsed = st.session_state.last_result

    st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-eyebrow">Query</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">"{q}"</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    answer_col = st.columns([1, 2.4, 1])[1]
    with answer_col:
        st.markdown(
            f"""
            <div class="answer-card">
                <div class="answer-header">✨ Grounded Answer</div>
                <div class="answer-body">{answer}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pages = sorted({r["page"] for r in retrieved})
        if pages:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown('<div class="section-eyebrow">Sources</div>', unsafe_allow_html=True)
            st.markdown(
                " ".join(
                    f'<span class="badge" style="animation:none;">Page {p}</span>'
                    for p in pages
                ),
                unsafe_allow_html=True,
            )