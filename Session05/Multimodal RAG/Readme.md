# Multimodal RAG on the "Attention Is All You Need" Paper

A Multimodal Retrieval-Augmented Generation (RAG) system built in Python that uses the **Attention Is All You Need** research paper as its knowledge base. The project extracts multiple content types from the paper, converts them into embeddings, stores them in a vector database, retrieves the most relevant information for a user query, and generates grounded answers using Google's Gemini models.

---

## Features

- Extracts body text from the research paper
- Detects and stores headings separately
- Extracts tables from the PDF
- Extracts figures and diagrams
- Uses Gemini Vision to understand visual content instead of ignoring it
- Generates embeddings for all extracted content
- Stores everything in a shared ChromaDB vector database
- Retrieves the most relevant context for a query
- Generates answers grounded only in the retrieved context

---

## Tech Stack

- Python
- Google Gemini API
- Gemini Embedding API
- PyMuPDF (fitz)
- pdfplumber
- ChromaDB
- LangChain Text Splitter
- Pillow
- python-dotenv

---

## Project Structure

```
.
├── app.py                      # Streamlit UI (imports multimodal_rag.py, doesn't modify it)
├── multimodal_rag.py            # Core backend: extraction, embedding, retrieval, generation
├── requirements.txt
├── AttentionIsAllYouNeed.pdf    # source document (not included — add your own copy)
├── images/                      # extracted figures (generated at runtime)
├── chroma_db/                   # persistent vector store (generated at runtime)
└── .env                         # GEMINI_API_KEY=... (not committed)
```

---

## Pipeline

### 1. Extraction

Content typeMethodText / headingsPyMuPDF (fitz), using font size (≥14pt) to separate headings from body textTablespdfplumber, flattened into pipe-delimited rows (`cellFiguresPyMuPDF pulls image xrefs page by page, saved as PNGs

### 2. Figure understanding

Each extracted image is passed to Gemini (gemini-3.1-flash-lite) with a prompt asking for:

figure title (if visible)
what the figure represents
architecture or workflow
mathematical concepts
labels and arrows
relationships between components
key observations
what questions the figure could answer


This turns each figure into a text description that can be embedded and retrieved like any other chunk.

### 3. Chunking


Body text: RecursiveCharacterTextSplitter (LangChain) — 800 char chunks, 100 char overlap.
Tables and figure descriptions: kept as single units (not split), since breaking them up would lose their meaning.


### 4. Embedding

All chunks (text, table, figure) are embedded with Gemini's gemini-embedding-001 model and stored together — one shared vector space across all three modalities.

### 5. Storage

Embeddings + metadata (type, page, path, source) are stored in a persistent ChromaDB collection (chroma_db/, collection name attention_paper). Metadata makes every retrieved chunk traceable back to its page and content type.

### 6. Retrieval

The query is embedded with the same embedding model, then ChromaDB returns the top-k nearest chunks by similarity (k is configurable, default 5).

### 7. Generation

Retrieved chunks are passed to Gemini (gemini-3.1-flash-lite) as context, with instructions to:

answer only from the retrieved context
not use outside knowledge
reply "The retrieved context does not contain enough information" if the answer isn't there
mention relevant page numbers


## Tech stack:

LLM / Vision / Embeddings: Gemini API (google-genai) — gemini-3.1-flash-lite for generation and vision, gemini-embedding-001 for embeddings
Vector store: ChromaDB (persistent client)
PDF parsing: PyMuPDF (fitz) for text/headings/images, pdfplumber for tables
Chunking: langchain-text-splitters
UI: Streamlit
Other: python-dotenv, Pillow, numpy
---

## Example Queries

- Explain the Transformer architecture.
- What is Multi-Head Attention?
- What BLEU score did the Transformer achieve?
- Describe the encoder-decoder architecture.
- What does Figure 1 illustrate?

---

## Installation

Clone the repository.

```bash
git clone <repository-url>
cd <repository-name>
```

Create a virtual environment.

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file.

```env
GEMINI_API_KEY=your_api_key_here
```

---

## Run

```bash
python multimodal_rag.py
```

---

## Sample Output

```
QUESTION:
What is Multi-Head Attention?

Retrieved Context

[1] text (page 4)
...

[2] figure (page 3)
...

[3] table (page 8)
...

ANSWER

Multi-Head Attention allows the model to attend to information from multiple representation subspaces simultaneously...
```

---

## Current Capabilities

- ✅ Text extraction
- ✅ Heading extraction
- ✅ Table extraction
- ✅ Figure extraction
- ✅ Vision-based figure understanding
- ✅ Embedding generation
- ✅ Vector search with ChromaDB
- ✅ Grounded answer generation

---

## Future Improvements

- OCR for scanned PDFs
- Formula extraction using Vision models
- Caption-aware retrieval
- Hybrid keyword + vector search
- Interactive Streamlit interface
- Metadata filtering during retrieval

---

## Note

This project was developed for **AI Season - Session 5** to demonstrate a complete Multimodal RAG pipeline using Google's Gemini models and ChromaDB.
