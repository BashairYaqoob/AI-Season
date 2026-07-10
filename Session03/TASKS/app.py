"""
AI Season RAG Explorer — Streamlit frontend.

Wraps the existing t3.py backend (LangChain + ChromaDB + HuggingFace
embeddings + Groq) with a dark, terminal-themed dashboard matching the
AI Season Bootcamp branding.

Run with:
    streamlit run app.py

Nothing in the retrieval / chunking / prompting logic is touched here —
this file only calls t3.initialize_pipeline() and t3.ask().
"""
import streamlit as st

import t3

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Season RAG Explorer",
    page_icon=">_",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------
# Theme — dark terminal console matching aiseason.com branding
# --------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --as-bg: #0a0a0a;
    --as-panel: #121212;
    --as-panel-2: #161513;
    --as-border: #2a2620;
    --as-amber: #f5a623;
    --as-amber-dim: #b9811f;
    --as-text: #f2f1ec;
    --as-muted: #9a978d;
    --as-mono: 'IBM Plex Mono', monospace;
    --as-sans: 'Inter', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--as-sans);
}

.stApp {
    background: radial-gradient(circle at 80% 0%, #171310 0%, #0a0a0a 45%) fixed;
    color: var(--as-text);
}

#MainMenu, footer, header {visibility: hidden;}

/* ---- top command bar ---- */
.as-cmdbar {
    font-family: var(--as-mono);
    font-size: 0.85rem;
    color: var(--as-amber);
    background: var(--as-panel);
    border: 1px solid var(--as-border);
    border-radius: 6px;
    padding: 10px 16px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.as-cmdbar .dim { color: var(--as-muted); }
.as-cmdbar .cursor {
    display: inline-block;
    width: 8px; height: 16px;
    background: var(--as-amber);
    animation: as-blink 1.1s steps(1) infinite;
}
@keyframes as-blink { 50% { opacity: 0; } }

/* ---- badge row ---- */
.as-badge-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 28px; }
.as-badge {
    font-family: var(--as-mono);
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    color: var(--as-muted);
    background: var(--as-panel);
    border: 1px solid var(--as-border);
    border-radius: 999px;
    padding: 7px 14px;
    display: flex;
    align-items: center;
    gap: 7px;
}
.as-badge b { color: var(--as-amber); font-weight: 600; }
.as-badge .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--as-amber);
}

/* ---- hero title ---- */
.as-hero-eyebrow {
    font-family: var(--as-mono);
    color: var(--as-amber);
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.as-hero-title {
    font-family: var(--as-mono);
    font-weight: 700;
    font-size: 2.6rem;
    line-height: 1.15;
    color: var(--as-text);
    margin-bottom: 6px;
}
.as-hero-title span { color: var(--as-amber); }
.as-hero-sub {
    color: var(--as-muted);
    font-size: 0.98rem;
    margin-bottom: 26px;
    max-width: 720px;
}

/* ---- ask panel ---- */
.as-ask-label {
    font-family: var(--as-mono);
    font-size: 0.78rem;
    color: var(--as-muted);
    margin-bottom: 4px;
}
div[data-testid="stTextInput"] input {
    background: var(--as-panel) !important;
    border: 1px solid var(--as-border) !important;
    color: var(--as-text) !important;
    font-family: var(--as-mono) !important;
    border-radius: 6px !important;
    padding: 12px 14px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--as-amber) !important;
    box-shadow: 0 0 0 1px var(--as-amber-dim) !important;
}
div[data-testid="stTextInput"] label { display: none; }

.stButton > button {
    background: var(--as-amber) !important;
    color: #14110b !important;
    font-family: var(--as-mono) !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.4rem !important;
    transition: filter 0.15s ease;
}
.stButton > button:hover { filter: brightness(1.08); }

/* ---- result cards ---- */
.as-card {
    background: var(--as-panel);
    border: 1px solid var(--as-border);
    border-radius: 10px;
    margin-bottom: 18px;
    overflow: hidden;
}
.as-card-titlebar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    background: var(--as-panel-2);
    border-bottom: 1px solid var(--as-border);
    font-family: var(--as-mono);
    font-size: 0.78rem;
}
.as-dots { display: flex; gap: 5px; margin-right: 6px; }
.as-dots span {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--as-border);
}
.as-dots span.a { background: #d9534f; }
.as-dots span.b { background: var(--as-amber-dim); }
.as-dots span.c { background: #5c8f3a; }
.as-card-path { color: var(--as-amber); }
.as-card-path .sep { color: var(--as-muted); }

.as-card-body { padding: 14px 16px 6px 16px; }
.as-tag-row { display: flex; gap: 8px; margin-bottom: 10px; }
.as-tag {
    font-family: var(--as-mono);
    font-size: 0.68rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--as-amber);
    background: rgba(245, 166, 35, 0.1);
    border: 1px solid rgba(245, 166, 35, 0.3);
    border-radius: 4px;
    padding: 3px 8px;
}
.as-tag.alt {
    color: #9fb8e8;
    background: rgba(120, 150, 220, 0.08);
    border-color: rgba(120, 150, 220, 0.25);
}
.as-answer-label {
    font-family: var(--as-mono);
    font-size: 0.68rem;
    color: var(--as-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.as-answer-text {
    color: var(--as-text);
    font-size: 0.92rem;
    line-height: 1.55;
    margin-bottom: 6px;
}

div[data-testid="stExpander"] {
    background: transparent;
    border: 1px solid var(--as-border) !important;
    border-radius: 6px !important;
    margin: 8px 14px 14px 14px;
}
div[data-testid="stExpander"] summary {
    font-family: var(--as-mono) !important;
    font-size: 0.75rem !important;
    color: var(--as-muted) !important;
}
.as-source {
    font-family: var(--as-mono);
    font-size: 0.72rem;
    color: var(--as-muted);
    border-left: 2px solid var(--as-amber-dim);
    padding: 4px 0 4px 10px;
    margin-bottom: 8px;
}
.as-source b { color: var(--as-text); }

hr.as-divider { border: none; border-top: 1px solid var(--as-border); margin: 30px 0 20px 0; }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Backend init (cached — vector stores + LLM built once per server process)
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_pipeline():
    return t3.initialize_pipeline()


# --------------------------------------------------------------------------
# Layout: top command bar
# --------------------------------------------------------------------------
st.markdown("""
<div class="as-cmdbar">
    <span>$</span> aiseason --module=rag-explorer --status=live
    <span class="cursor"></span>
</div>
""", unsafe_allow_html=True)

try:
    with st.spinner("Booting pipeline — embedding chunks into ChromaDB..."):
        state = get_pipeline()
    pipeline_error = None
except Exception as e:  # noqa: BLE001
    state = None
    pipeline_error = str(e)

# --------------------------------------------------------------------------
# Badges: Knowledge Base / Embedding Model / LLM Model
# --------------------------------------------------------------------------
if state is not None:
    llm_label = state["llm_model_name"] if not state["use_mock"] else "mock (no GROQ key)"
    st.markdown(f"""
    <div class="as-badge-row">
        <div class="as-badge"><span class="dot"></span>KNOWLEDGE BASE&nbsp;<b>aiseason-document.txt</b></div>
        <div class="as-badge"><span class="dot"></span>EMBEDDING MODEL&nbsp;<b>{state['embedding_model']}</b></div>
        <div class="as-badge"><span class="dot"></span>LLM MODEL&nbsp;<b>{llm_label}</b></div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Hero
# --------------------------------------------------------------------------
st.markdown("""
<div class="as-hero-eyebrow">PAKISTAN-FOCUSED AI AGENTS BOOTCAMP &middot; RAG LAB</div>
<div class="as-hero-title">AI Season <span>RAG Explorer</span></div>
<div class="as-hero-sub">
    Ask one question, watch it run through 3 chunking strategies × 2 retrieval
    techniques, and compare all six answers side by side.
</div>
""", unsafe_allow_html=True)

if pipeline_error:
    st.error(f"Pipeline failed to initialize: {pipeline_error}")
    st.stop()

# --------------------------------------------------------------------------
# Ask panel
# --------------------------------------------------------------------------
st.markdown('<div class="as-ask-label">$ ask --question=</div>', unsafe_allow_html=True)
col_in, col_btn = st.columns([5, 1])
with col_in:
    question = st.text_input(
        "question",
        placeholder="e.g. What is included in the AI Season bootcamp?",
        label_visibility="collapsed",
    )
with col_btn:
    ask_clicked = st.button("Ask →", use_container_width=True)

st.markdown('<hr class="as-divider">', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Run all 6 combinations and render result cards
# --------------------------------------------------------------------------
COMBOS = [
    ("CharacterTextSplitter", "Character"),
    ("RecursiveCharacterTextSplitter", "Recursive"),
    ("TokenTextSplitter", "Token"),
]
RETRIEVALS = [("similarity", "Similarity"), ("mmr", "MMR")]

DB_MAP = {
    "CharacterTextSplitter": "db_character",
    "RecursiveCharacterTextSplitter": "db_recursive",
    "TokenTextSplitter": "db_token",
}


def render_card(result, chunk_label, retrieval_label):
    sources_html = ""
    for i, src in enumerate(result["sources"], 1):
        snippet = src["content"][:180].replace("<", "&lt;").replace(">", "&gt;")
        source_name = src["source"] or "unknown"
        sources_html += (
            f'<div class="as-source"><b>[{i}] {source_name}</b><br>{snippet}...</div>'
        )

    answer_text = result["answer"].replace("<", "&lt;").replace(">", "&gt;")

    st.markdown(f"""
    <div class="as-card">
        <div class="as-card-titlebar">
            <div class="as-dots"><span class="a"></span><span class="b"></span><span class="c"></span></div>
            <span class="as-card-path">chunk={chunk_label.lower()}<span class="sep"> · </span>retrieval={retrieval_label.lower()}</span>
        </div>
        <div class="as-card-body">
            <div class="as-tag-row">
                <span class="as-tag">{chunk_label}</span>
                <span class="as-tag alt">{retrieval_label}</span>
            </div>
            <div class="as-answer-label">LLM Answer</div>
            <div class="as-answer-text">{answer_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(f"Sources ({len(result['sources'])})"):
        st.markdown(sources_html, unsafe_allow_html=True)


if ask_clicked:
    if not question.strip():
        st.warning("Type a question first.")
    else:
        with st.spinner("Retrieving across 3 chunkers × 2 retrieval techniques..."):
            results = []
            for splitter_key, chunk_label in COMBOS:
                db = state[DB_MAP[splitter_key]]
                for retrieval_key, retrieval_label in RETRIEVALS:
                    result = t3.ask(
                        db,
                        question,
                        retrieval_key,
                        chunk_label,
                        state["llm"],
                        state["use_mock"],
                    )
                    results.append((result, chunk_label, retrieval_label))

        # 3 columns x 2 rows -> group by chunking method so each column
        # shows one chunker's Similarity result above its MMR result.
        cols = st.columns(3)
        for idx, (splitter_key, chunk_label) in enumerate(COMBOS):
            with cols[idx]:
                pair = [r for r in results if r[1] == chunk_label]
                for result, c_label, r_label in pair:
                    render_card(result, c_label, r_label)
elif state is not None:
    st.info("Enter a question above and click **Ask →** to run the 6-way comparison.")
