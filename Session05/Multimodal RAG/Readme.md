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
├── AttentionIsAllYouNeed.pdf
├── multimodal_rag.py
├── requirements.txt
├── .env
├── .gitignore
├── images/
└── chroma_db/
```

---

## Pipeline

1. Load the research paper.
2. Extract:
   - Text
   - Headings
   - Tables
   - Figures
3. Describe figures using Gemini Vision.
4. Generate embeddings for every extracted document.
5. Store embeddings inside ChromaDB.
6. Embed the user's question.
7. Retrieve the most relevant chunks.
8. Generate a grounded answer using only the retrieved context.

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
