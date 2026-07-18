# LangChain — AI Season Session 6 Notes

> **Topic:** LangChain Fundamentals
> **Goal:** Build AI applications faster by connecting prompts, LLMs, memory, tools, and RAG into reusable pipelines.

---

# What is LangChain?

LangChain is an **AI application framework** that provides reusable building blocks for LLM applications.

Instead of manually writing API calls, prompts, memory handling, tool execution, and retrieval every time, LangChain standardizes everything into one framework.

Think of it as:

```
Without LangChain
API Call → Prompt → Response → Parse → Store Memory → Call Tool

With LangChain
Prompt → Model → Parser
        │
      Memory
        │
      Tools
        │
      RAG
```

It **does NOT replace** OpenAI, Gemini, Groq, etc.

It simply wraps them into a consistent interface.

---

# Why use LangChain?

Instead of writing lots of repetitive code, LangChain lets you:

- Switch between AI providers easily
- Reuse prompts
- Build pipelines
- Add memory
- Use tools
- Build agents
- Create RAG systems

---

# Core Concept: Everything is a Runnable

The most important concept of LangChain.

Almost everything is a **Runnable**.

Examples:

- Prompt
- LLM
- Parser
- Retriever
- Tool

Since they're all Runnable, they can be connected together.

```
Prompt
   │
   ▼
LLM
   │
   ▼
Parser
```

---

# LCEL (LangChain Expression Language)

LCEL is LangChain's pipeline syntax.

Instead of writing many function calls:

```python
prompt.format()
llm.invoke()
parser.parse()
```

You simply write:

```python
prompt | llm | parser
```

The `|` operator passes the output of one component to the next.

---

# Basic Flow

```
User Question
      │
      ▼
Prompt Template
      │
      ▼
LLM
      │
      ▼
Output Parser
      │
      ▼
Final Response
```

---

# invoke()

Runs the chain once.

```python
chain.invoke(...)
```

Used for:

- Chat
- Single questions
- One request

---

# batch()

Runs multiple inputs together.

```python
chain.batch([...])
```

Useful when processing many prompts at once.

---

# stream()

Streams tokens as they are generated.

Instead of waiting for the entire response, text appears gradually.

Better UX for chatbots.

---

# Prompt Templates

Instead of hardcoding prompts:

```
Explain Python.
Explain Java.
Explain C++.
```

Create one reusable template.

Example:

```
Explain {topic} in simple words.
```

Now the same prompt works for any topic.

Benefits:

- Reusable
- Cleaner code
- Easy customization

---

# Few-Shot Prompting

Provide examples before the real question.

Example:

```
Input → Output
Input → Output

Now solve:
```

Helps the model imitate the desired format.

---

# Output Parsers

Normally LLMs return plain text.

Sometimes we need structured data.

Instead of manually parsing strings,

LangChain converts responses into:

- JSON
- Python dictionaries
- Objects

Much easier to use in applications.

---

# Runnable Types

## RunnableSequence

Runs tasks one after another.

```
A
↓
B
↓
C
```

---

## RunnableLambda

Wraps a custom Python function inside a LangChain pipeline.

Useful when adding your own logic.

---

## RunnableParallel

Runs multiple tasks simultaneously.

```
      Input
     /  |  \
    A   B   C
```

Useful when independent tasks can execute together.

---

## RunnablePassthrough

Passes input unchanged while allowing extra processing.

Useful for branching pipelines.

---

# Memory

LLMs are stateless.

Without memory:

```
User:
My name is Ali.

Later:
What's my name?

LLM:
I don't know.
```

Memory stores previous conversations.

Now the chatbot remembers context.

In LangChain, memory is managed automatically using a **session_id**.

---

# Structured Output

Instead of receiving:

```
The price is $25.
```

Receive:

```python
{
    "price": 25
}
```

Benefits:

- Reliable
- Easy to process
- Works well with APIs and databases

---

# Tools

A Tool is a Python function the LLM can use.

Examples:

- Calculator
- Weather API
- Search
- Database
- File Reader

Instead of guessing answers, the model can call the appropriate tool.

---

# Agents

An Agent decides:

- Which tool to use
- When to use it
- How many times to use it

Workflow:

```
Question
   │
   ▼
Agent
   │
Chooses Tool
   │
Runs Tool
   │
Gets Result
   │
Final Answer
```

Unlike a normal chatbot, agents can reason and take actions.

---

# Retrieval-Augmented Generation (RAG)

Instead of relying only on training data:

```
Question
     │
     ▼
Retriever
     │
Relevant Documents
     │
     ▼
LLM
     │
Answer
```

Main components:

- Embeddings
- Vector Store
- Retriever
- LLM

LangChain hides most of the implementation details.

---

# Vector Store

Stores document embeddings.

Popular options:

- FAISS
- ChromaDB
- Pinecone

Allows semantic search instead of keyword search.

---

# Retriever

Searches the vector database.

Returns only the most relevant chunks.

Those chunks become context for the LLM.

---

# Agent + RAG

RAG can also be exposed as a Tool.

Now an Agent decides:

```
Should I:

- Search documents?
- Use calculator?
- Search web?
```

This combines reasoning with retrieval.

---

# Advantages of LangChain

- Standard interface for multiple LLM providers
- Reusable prompt templates
- Built-in memory
- Easy RAG pipelines
- Tool integration
- Agent framework
- Structured outputs
- Modular architecture

---

# LangChain vs Raw API Calls

| Raw API | LangChain |
|----------|-----------|
| Manual prompts | Prompt Templates |
| Manual parsing | Output Parsers |
| Manual conversation history | Memory |
| Manual tool execution | Agents |
| Manual RAG pipeline | Built-in Retrievers |
| Different SDK for each provider | Unified interface |

---

# Session Flow

```
Hello LangChain
        ↓
Prompt Templates
        ↓
LCEL Chains
        ↓
Runnable Types
        ↓
Structured Output
        ↓
Memory
        ↓
Tools
        ↓
Agents
        ↓
RAG
        ↓
Agent + RAG
```

---

# Key Terms to Remember

- **LangChain** → Framework for LLM applications
- **Runnable** → Core building block
- **LCEL** → Pipeline syntax (`|`)
- **invoke()** → Run once
- **batch()** → Run many inputs
- **stream()** → Token streaming
- **Prompt Template** → Reusable prompt
- **Output Parser** → Structured responses
- **Memory** → Conversation history
- **Tool** → External function/API
- **Agent** → Chooses and uses tools automatically
- **Retriever** → Finds relevant documents
- **Vector Store** → Stores embeddings
- **RAG** → Retrieval + Generation

---

# Interview / Viva Questions

### What is LangChain?

A framework that simplifies building LLM applications using reusable components like prompts, models, memory, tools, agents, and RAG.

---

### Does LangChain replace OpenAI, Gemini, or Groq?

No. It provides a common interface to interact with different LLM providers.

---

### What is a Runnable?

A component that accepts input and produces output. Prompts, models, parsers, retrievers, and tools are all Runnables.

---

### What is LCEL?

LangChain Expression Language, which connects components using the `|` operator to form pipelines.

---

### Why use Prompt Templates?

To reuse prompts with different inputs instead of rewriting them.

---

### What is Memory?

A mechanism that stores conversation history so the chatbot can maintain context across interactions.

---

### Difference between Tools and Agents?

- **Tool:** Performs a specific task.
- **Agent:** Decides which tool(s) to use and when.

---

### What is RAG?

Retrieval-Augmented Generation retrieves relevant documents from a vector database before generating an answer, reducing hallucinations.

---

### What is a Vector Store?

A database that stores embeddings for semantic search.

---

### Why use Structured Output?

To receive machine-readable data (JSON/Python objects) instead of parsing plain text manually.
