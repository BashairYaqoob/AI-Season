# AI Season — Session 3: How AI Answers From Your Data (RAG)

---

# What problem does RAG solve?

LLMs like GPT, Claude, or Llama are trained on public data. They **do not know**:

* Company documents
* PDFs
* Policies
* Research papers
* Your database
* Recently uploaded files

Instead of retraining the model every time new information appears, we retrieve relevant documents and provide them to the LLM as context.

This architecture is called **Retrieval Augmented Generation (RAG).**

---

# Complete RAG Pipeline

```text
                 OFFLINE (One Time)

Documents
     ↓
Load Files
     ↓
Extract Text
     ↓
Chunk Text
     ↓
Create Embeddings
     ↓
Store in Vector Database

──────────────────────────────────────────

                 ONLINE (Every Question)

User Question
      ↓
Embed Question
      ↓
Vector Search
      ↓
Retrieve Top-K Chunks
      ↓
Build Prompt
      ↓
LLM (Groq)
      ↓
Final Answer
```

---

# Two Pipelines

## 1. Ingestion Pipeline

Runs once.

Purpose:

Prepare documents for searching.

Includes:

* File loading
* Text extraction
* Chunking
* Embedding creation
* Vector database storage

---

## 2. Retrieval Pipeline

Runs for every user question.

Purpose:

Find relevant information and send it to the LLM.

---

# Step 1 — File Conversion (`1_file_conversion.py`)

### Purpose

Different document types cannot be directly embedded.

Convert everything into plain text.

Supported examples:

* PDF
* DOCX
* TXT

Output:

```text
policy.pdf

↓

policy.txt
```

### Why?

Embedding models understand text.

Not PDF formatting.

---

# Step 2 — Ingestion (`2_ingestion_pipeline.py`)

Purpose:

Create the searchable knowledge base.

Flow

```text
Load Documents

↓

Chunk Documents

↓

Create Embeddings

↓

Store in Chroma
```

Nothing is sent to the LLM here.

You're only preparing the database.

---

# Documents

LangChain stores each file as a **Document object**.

A document contains

```python
page_content

metadata
```

Example

```text
page_content

"Premium members can..."

metadata

{
 source: policy.pdf,
 page: 4
}
```

Metadata is later used for citations.

---

# Step 3 — Chunking

Large documents are split into smaller pieces.

Example

Instead of

```text
100-page PDF
```

↓

```text
250 chunks
```

### Why?

* Better search
* Better embeddings
* Fits model context window
* Easier retrieval

---

## Bad Chunk

Sentence gets cut in half.

Meaning disappears.

---

## Large Chunk

Contains

* history
* shipping
* refunds
* warranty

Retriever becomes confused.

---

## Good Chunk

Contains only one idea.

Typical size

* 300–800 tokens

Overlap

* 10–20%

---

### Code

The project uses

```python
RecursiveCharacterTextSplitter
```

Purpose:

Split documents while preserving context.

Why "Recursive"?

It tries splitting using

Paragraph

↓

Line

↓

Sentence

↓

Character

until chunk size becomes acceptable.

Much smarter than

```python
text[:500]
```

---

# Step 4 — Embeddings

Embedding

=

Convert text into numbers.

Example

```text
"I love AI"

↓

[0.13, 0.54, ...]
```

Thousands of numbers represent meaning.

---

## Important

LLMs generate text.

Embedding models generate vectors.

Different models.

Different jobs.

---

Similar meanings produce nearby vectors.

Example

```text
Course Fee

Program Cost

Tuition Fee
```

All become similar vectors.

---

# Step 5 — Vector Database

The project uses

**ChromaDB**

Purpose

Store embeddings.

Each record stores

```text
Embedding

Original Text

Metadata

Chunk ID
```

Unlike SQL

SQL searches

```text
Exact values
```

Vector DB searches

```text
Meaning
```

---

# Retrieval (`3_retrieval_pipeline.py`)

When user asks

```text
Can I return opened headphones?
```

The question is also embedded.

```text
Question

↓

Embedding

↓

Compare against stored vectors

↓

Top-K Results
```

Retriever never searches using keywords.

It searches semantic meaning.

---

# Cosine Similarity

Used to compare vectors.

Closer to **1**

↓

More similar.

Closer to **0**

↓

Less similar.

This is how Chroma decides which chunks are relevant.

---

# Top-K

Retriever returns

Top K chunks.

Example

K = 3

Returns

Chunk 1

Chunk 2

Chunk 3

Choosing K is important.

Small K

↓

Missing information.

Large K

↓

Too much irrelevant information.

---

# Answer Generation (`4_answer_generation.py`)

Now the retrieved chunks become part of the prompt.

Prompt

```text
System Prompt

+

Retrieved Chunks

+

User Question
```

Then

↓

Groq API

↓

LLM

↓

Answer

---

Notice

The LLM **never accesses Chroma directly.**

It only receives the retrieved text.

---

# Recursive Chunking Demo (`5_recursive_chunking_demo.py`)

Purpose

Shows how different chunk sizes affect retrieval.

Main lesson

Good chunking often improves results more than changing the LLM.

---

# Retrieval Methods (`6_retrieval_methods.py`)

Shows different ways to retrieve documents.

Examples

* Similarity Search
* Top-K Search
* Filtered Retrieval

Different applications require different retrieval strategies.

---

# Full RAG Pipeline (`7_full_rag_pipeline.py`)

Combines everything.

```text
Load Files

↓

Chunk

↓

Embedding

↓

Store

↓

Question

↓

Retrieve

↓

Prompt

↓

LLM

↓

Answer
```

This is the complete architecture.

---

# Failure Experiments (`8_failure_experiments.py`)

Very important.

Tests why RAG fails.

Examples

Ask

```text
Who founded Google?
```

when document doesn't mention it.

Correct response

"I don't have enough information."

Wrong response

Model invents an answer.

Also experiments with

* Bad chunking
* Different Top-K values
* Weak prompts

---

# Hybrid Retrieval (`9_hybrid_retrieval.py`)

Normal Retrieval

↓

Semantic Search only.

Hybrid Retrieval

↓

Semantic Search

*

Keyword Search (BM25)

Why?

Semantic search may miss exact IDs.

Example

```text
INV-82713
```

Keyword search finds it immediately.

Production systems usually combine both.

---

# Streamlit App (`10_streamlit_app.py`)

Creates a simple chatbot UI.

Flow

```text
User types question

↓

Retriever

↓

LLM

↓

Display answer
```

Streamlit only handles the interface.

The AI logic remains unchanged.

---

# The `aiseason-tech/chatbot` Folder

This folder modularizes the RAG system.

### `file_loader.py`

Reads documents from disk and converts them into LangChain `Document` objects.

### `chunking.py`

Splits documents into smaller chunks using `RecursiveCharacterTextSplitter`.

### `embeddings.py`

Creates embeddings for each chunk using the chosen embedding model.

### `vector_store.py`

Initializes Chroma, stores vectors, and loads the persisted vector database.

### `retrieval.py`

Accepts a user query, embeds it, searches Chroma, and returns the most relevant chunks.

### `llm.py`

Configures the Groq LLM client and sends prompts for generation.

### `pipeline.py`

Orchestrates the entire workflow:

```
Question → Retrieval → Prompt → LLM → Answer
```

### `evaluation.py`

Runs tests to evaluate retrieval quality and answer accuracy.

### `config.py`

Stores reusable configuration such as model names, paths, chunk sizes, and API settings.

---

# LangChain Components Used

| Component       | Purpose                  |
| --------------- | ------------------------ |
| Document Loader | Reads files              |
| Document        | Stores text + metadata   |
| Text Splitter   | Creates chunks           |
| Embedding Model | Converts text to vectors |
| Chroma          | Stores vectors           |
| Retriever       | Finds relevant chunks    |
| LLM             | Generates answers        |

---

# Common Interview Questions

### Why use RAG instead of fine-tuning?

Because documents change frequently. Updating a vector database is much cheaper and faster than retraining a model.

---

### Why chunk documents?

Large documents produce poor retrieval and exceed an LLM's context window.

---

### Why store metadata?

To show citations, filter results, and trace answers back to the original document.

---

### Does Chroma store the original text?

Yes. It stores:

* the embedding vector
* the original chunk text
* metadata
* unique IDs

---

### Does the LLM search the database?

No.

The **retriever** searches the vector database. The LLM only receives the retrieved context inside the prompt.

---

### Can RAG eliminate hallucinations?

No. It reduces them by grounding answers in retrieved evidence, but poor retrieval or missing context can still produce incorrect answers.

---

# Session 3 Summary (Memorize This)

```text
Documents
    ↓
Load
    ↓
Chunk
    ↓
Embeddings
    ↓
Chroma Vector DB
────────────────────────────
User Question
    ↓
Embed Query
    ↓
Similarity Search
    ↓
Top-K Chunks
    ↓
Prompt
    ↓
Groq LLM
    ↓
Grounded Answer
```
