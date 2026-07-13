"""
Task 5: Multimodal RAG on the Attention Is All You Need Paper
Requirements:
- Use the Gemini API (with your own API key loaded from an environment variable — do not hardcode it) for multimodal
understanding and answer generation.
- Use the 'Attention Is All You Need' paper as the source document.
- Extract the different content types from the PDF: body text, headings, tables, figures/diagrams, and charts.
- Pass the visual elements (architecture diagram, attention plots, charts, figures) through Gemini's vision capability
so their meaning is captured, not skipped.
- Generate embeddings for all extracted content (text chunks, table content, and image descriptions) and store them 
together in one shared embedding space / vector store.
- Implement a retrieval step that, given a user query, pulls the most relevant chunks from the vector store.
- Generate a grounded answer from the retrieved context using Gemini, rather than answering from the model's general knowledge.
- Demonstrate the system with sample queries that hit different modalities — e.g. something answerable from a table
(BLEU scores), from a figure (the encoder-decoder architecture), and from the text (what multi-head attention is).
- Print or save the query + retrieved context + final answer so it's clear the pipeline runs end to end.
"""

import os
import numpy as np
import fitz                    # PyMuPDF
import pdfplumber
import chromadb
from dotenv import load_dotenv
from google import genai
from PIL import Image
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)

MODEL = "gemini-2.5-pro"
EMBED_MODEL = "gemini-embedding-001"

PDF_PATH = "AttentionIsAllYouNeed.pdf"

IMAGE_FOLDER = "images"

def extract_images():
    print("Extracting images...")
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    image_info = []
    doc = fitz.open(PDF_PATH)
    for page_no in range(len(doc)):
        page = doc.load_page(page_no)
        for index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:
                path = os.path.join(IMAGE_FOLDER,f"page_{page_no+1}_img_{index}.png")
                pix.save(path)
                image_info.append({"page": page_no + 1,"path": path})
            pix = None

    doc.close()
    print(f"Extracted {len(image_info)} images.")
    return image_info

# Pass visual elements through Gemini Vision so their meaning is captured.

def describe_images(image_info):
    print("Describing images with Gemini Vision...")
    documents = []
    for item in image_info:
        with Image.open(item["path"]) as img:
            response = client.models.generate_content(
                model=MODEL,contents=[img, """..."""])

        response = client.models.generate_content(
            model=MODEL,
            contents=[img,"""
You are analyzing a figure from the research paper
'Attention Is All You Need'.

Provide a detailed explanation including:

- figure title (if visible)
- what the figure represents
- architecture or workflow
- mathematical concepts
- labels and arrows
- relationships between components
- key observations
- what questions this figure could answer

Do not simply describe the picture.
Explain its meaning in the context of the paper.
"""
            ])
        documents.append({"type": "figure","page": item["page"],"path":item["path"],"content": response.text})
    return documents

def extract_text():
    print("Extracting text and headings...")

    documents = []
    doc = fitz.open(PDF_PATH)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    for page_no, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        page_text = ""
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = ""
                max_font = 0
                for span in line["spans"]:
                    line_text += span["text"] + " "
                    max_font = max(max_font, span["size"])
                line_text = line_text.strip()
                if not line_text:
                    continue
                # Large fonts = headings
                if max_font >= 14:
                    documents.append({
                        "type": "heading",
                        "page": page_no + 1,
                        "content": line_text
                    })
                else:
                    page_text += line_text + "\n"
        chunks = splitter.split_text(page_text)
        for chunk in chunks:
            documents.append({
                "type": "text",
                "page": page_no + 1,
                "content": chunk
            })
    doc.close()
    print(f"{len(documents)} text/heading chunks.")
    return documents

def extract_tables():
    print("Extracting tables...")
    documents = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for page_no, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                table_text = "\n".join(
                    [" | ".join([cell or "" for cell in row])for row in table]
                )
                documents.append({"type": "table","page": page_no + 1,"content": table_text})
    print(f"{len(documents)} tables.")
    return documents

def build_vector_store(documents):
    print("Creating embeddings...")
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[d["content"] for d in documents]
    )

    embeddings = [e.values for e in result.embeddings]
    chroma = chromadb.PersistentClient(path="chroma_db")
    try:
        chroma.delete_collection("attention_paper")
    except:
        pass

    collection = chroma.get_or_create_collection("attention_paper")
    for i, (doc, emb) in enumerate(zip(documents, embeddings)):
        collection.add(
            ids=[str(i)],
            documents=[doc["content"]],
            embeddings=[emb],
            metadatas=[
                {
                    "type": doc["type"],
                    "page": doc.get("page", 0),
                    "path":doc.get("path",""),
                    "source":"AttentionIsAllYouNeed.pdf"
                }
            ]
        )
    print(f"Stored {collection.count()} documents.")
    return collection

def retrieve_documents(question, collection, k=5):
    q = client.models.embed_content(
        model=EMBED_MODEL,
        contents=question
    )
    results = collection.query(
        query_embeddings=[q.embeddings[0].values],
        n_results=k
    )
    return results

def answer_question(question, collection):
    print("=" * 60)
    print(question)
    results = retrieve_documents(question, collection)
    docs = results["documents"][0]
    metadata = results["metadatas"][0]
    context = ""
    print("\nRetrieved Context\n")
    for i, (doc, meta) in enumerate(zip(docs, metadata), 1):
        print(
            f"[{i}] "
            f"{meta['type']} "
            f"(page {meta['page']})"
        )
        print(doc[:250])
        print()
        context += doc + "\n\n"
    response = client.models.generate_content(model=MODEL,contents=f"""
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
    print("\nANSWER\n")
    print(response.text)

def main():
    print("="*60)
    print("MULTIMODAL RAG")
    print("="*60)
    image_info = extract_images()
    figure_docs = describe_images(image_info)
    text_docs = extract_text()
    table_docs = extract_tables()

    documents = []
    documents.extend(text_docs)
    documents.extend(table_docs)
    documents.extend(figure_docs)

    collection = build_vector_store(documents)

    answer_question("Explain the Transformer architecture.",collection)
    answer_question("What is Multi-Head Attention?",collection)
    answer_question("What BLEU score did the Transformer achieve?",collection)
    answer_question("Describe the encoder-decoder architecture shown in the figure.",collection)

if __name__ == "__main__":
    main()
