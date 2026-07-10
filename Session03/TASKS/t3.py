"""
Full RAG pipeline in one script — ingest, retrieve, prompt, Groq answer, sources.
Requirements:
Build a simple RAG chatbot.
Use the provided AI Season Bootcamp documents as the knowledge base.
Implement three chunking methods.
Implement two retrieval techniques.
Display all outputs simultaneously for a single query.
Clearly identify which output belongs to each chunking and retrieval method.
Run: t3.py
"""
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import (CharacterTextSplitter, RecursiveCharacterTextSplitter, TokenTextSplitter)

load_dotenv()

CHAR_DB = "db/chroma_character"
RECURSIVE_DB = "db/chroma_recursive"
TOKEN_DB = "db/chroma_token"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_vector_store(splitter_class, persist_dir, embeddings):
    print(f"[1] Loading and chunking documents ({splitter_class.__name__})...")
    loader = TextLoader("aiseason-document.txt")
    documents = loader.load()

    if splitter_class == CharacterTextSplitter:
        splitter = splitter_class(
            separator="\n",
            chunk_size=500,
            chunk_overlap=50
        )
    else:
        splitter = splitter_class(
            chunk_size=500,
            chunk_overlap=50
        )
    chunks = splitter.split_documents(documents)
    print(f"    {len(documents)} docs -> {len(chunks)} chunks")

    print("[2] Embedding and storing in ChromaDB...")
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_metadata={"hnsw:space": "cosine"},
    )

def get_retriever(db, retrieval_type):
    if retrieval_type == "similarity":
        return db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
        )
    elif retrieval_type == "mmr":
        return db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.5},
        )
    else:
        raise ValueError(f"Unknown retrieval_type: {retrieval_type}")

def ask(db, question, retrieval_type, chunk_name, llm, use_mock):
    """
    MODIFIED: now returns a dict of structured data instead of printing to
    the terminal. Retrieval / chunking / prompting logic is UNCHANGED.
    """
    retriever = get_retriever(db, retrieval_type)
    docs = retriever.invoke(question)

    context = "\n".join([f"- {d.page_content}" for d in docs])
    prompt = f"""
You are an AI assistant.

Use ONLY the context below to answer.

If the answer cannot be found in the context,
reply exactly:

"I don't have enough information."

Context:
{context}

Question:
{question}
"""

    if use_mock:
        answer = f"[MOCK LLM] Summary from retrieved docs for: {question}"
    else:
        result = llm.invoke([
            SystemMessage(content=
                    "You are a helpful RAG assistant. "
                    "Answer ONLY from the provided context. "
                    "If the context does not contain the answer, say "
                    "'I don't have enough information.'"),
            HumanMessage(content=prompt),
        ])
        answer = result.content

    sources = []
    for doc in docs:
        sources.append({
            "source": doc.metadata.get("source"),
            "content": doc.page_content,
        })

    return {
        "chunking": chunk_name,
        "retrieval": retrieval_type,
        "answer": answer,
        "sources": sources,
    }


def initialize_pipeline():
    """
    NEW: extracted from main() so a frontend (e.g. Streamlit) can build the
    three vector stores + LLM once and reuse them across questions, without
    needing terminal input(). Logic inside is copy-pasted from main(),
    nothing about chunking/retrieval/prompting was changed.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    db_character = build_vector_store(CharacterTextSplitter, CHAR_DB, embeddings)
    db_recursive = build_vector_store(RecursiveCharacterTextSplitter, RECURSIVE_DB, embeddings)
    db_token = build_vector_store(TokenTextSplitter, TOKEN_DB, embeddings)

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()

    use_mock = (
        provider == "mock"
        or not api_key
        or api_key == "your_groq_key_here"
    )

    llm = None
    llm_model_name = "mock"
    if not use_mock:
        llm_model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        llm = ChatGroq(model=llm_model_name, temperature=0.2)

    return {
        "db_character": db_character,
        "db_recursive": db_recursive,
        "db_token": db_token,
        "llm": llm,
        "use_mock": use_mock,
        "provider": provider,
        "llm_model_name": llm_model_name,
        "embedding_model": EMBEDDING_MODEL,
    }


def main():
    print("=== Full RAG Pipeline ===\n")

    state = initialize_pipeline()

    print(f"GROQ Provider: {state['provider']}")
    print(f"Mock Mode: {state['use_mock']}")

    question = input("Ask a question: ")

    chunkers = [
        ("CharacterTextSplitter", state["db_character"]),
        ("RecursiveCharacterTextSplitter", state["db_recursive"]),
        ("TokenTextSplitter", state["db_token"]),
    ]
    retrievals = ["similarity", "mmr"]

    for chunk_name, db in chunkers:
        for retrieval in retrievals:
            result = ask(db, question, retrieval, chunk_name, state["llm"], state["use_mock"])

            print(f"\nQuestion: {question}")
            print("\n" + "=" * 60)
            print(f"Chunking : {result['chunking']}")
            print(f"Retrieval: {result['retrieval'].upper()}")
            print("=" * 60)
            print("\nAnswer:")
            print(result["answer"])
            print("\nSources:")
            for i, src in enumerate(result["sources"], 1):
                print(f"  [{i}] {src['source']}")
                print(f"      {src['content'][:120]}...")


if __name__ == "__main__":
    main()
