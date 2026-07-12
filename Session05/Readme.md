# AI Season — Session 5: Multi-Modal Agents

---

## 1. The Modality Gap — Why This Topic Matters

- Traditional LLMs are **text-constrained** — they only understand strings of characters.
- The core question of the session: *"If an LLM could only understand text, how would it analyze an image, a PDF, or a voice message?"*
- Humans experience the world through **multiple channels at once** (eyes, ears, touch), but classic LLMs get only one channel: text.
- A **Multimodal Agent** closes this gap by accepting different types of input (images, audio, video, documents) and reasoning over all of them together.

---

## 2. What is a "Modality"?

> A modality = a type of information or a sensory channel — i.e., a category of input/output data an LLM can work with.

| Modality | Examples |
|---|---|
| **Text** | PDFs, code, reports, books |
| **Vision** | Images, charts, maps |
| **Audio** | Speech, music, noise |
| **Temporal** | Video, motion, LiDAR |
| **Structured** | Tables, sensor data |
| **Multimodal** | The fusion of all of the above |

---

## 3. Why Do We Need Multimodal AI?

**Core idea:** Real-world data is never *only* text.

### Case Study — Healthcare
A doctor doesn't just read a note. They simultaneously process:
- X-ray imagery (vision)
- Blood reports (structured tables)
- Patient speech — tone & stress (audio)
- Medical history (text)

→ A Multimodal Agent fuses all these signals for a claimed **~10x more accurate diagnosis**.

### Case Study — Self-Driving Cars
Autonomous navigation needs real-time synthesis of **Cameras + LiDAR + GPS + Speed telemetry + Radar** — one modality is never enough for safety.

### Case Study — Customer Support
A customer might upload a screenshot of an error, send a voice complaint, **and** write a text description — all in one interaction.

---

## 4. Traditional AI vs Multimodal AI

| Feature | Traditional AI | Multimodal AI |
|---|---|---|
| **Inputs** | Single (text only) | Multiple (any data type) |
| **Understanding** | Limited / semantic only | Rich / context-aware |
| **Architecture** | Separate model per task | One unified reasoning core |
| **Output** | Text / classification | Images, actions, reasoning |

---

## 5. System Architecture (High-Level)

A multimodal system is generally structured as:

```
Raw Input (image/audio/video/text)
        ↓
     Encoders  (convert raw data → embeddings)
        ↓
 Shared Embedding Space  (unified representation)
        ↓
   LLM / Reasoning Core
        ↓
  Output (text, action, generation)
```

---

## 6. Encoders — The Translators

**Definition:** Encoders convert raw, unstructured data (pixels, sound waves) into **vectors (embeddings)** that an LLM can actually process.

> **Key insight: the LLM never sees raw pixels or sound waves — it only sees the embeddings the encoders produce.**

| Modality | Common Encoders |
|---|---|
| Vision | ViT (Vision Transformer), CLIP Encoder |
| Audio | Whisper, Wav2Vec, Audio-MAE |
| Video | VideoMAE, TimeSformer (adds temporal reasoning) |

---

## 7. Shared Embedding Space

**Question:** How does an AI know an image of a cat and the word "Cat" mean the same thing?

- **Contrastive learning** forces matching pairs (e.g., an image of a cat + the text "cat") to land as **similar vectors** in a high-dimensional space.
- Process:
  1. An image of a cat is encoded → vector A
  2. The text "Cat" is encoded → vector B
  3. Training pulls vector A and vector B close together in latent space
- This conceptual alignment is exactly what lets an LLM **reason across completely different modalities** using one shared "map."

---

## 8. Real-World Reasoning: Self-Driving Example

Self-driving cars must fuse 4 modalities **simultaneously**:
- **Cameras** → visual context
- **LiDAR** → depth / mapping
- **GPS** → localization
- **Radar** → speed / distance

The agent reasons across all four at once — no single sensor is trusted alone (safety-critical redundancy).

---

## 9. Vision Language Models (VLMs)

- A **VLM** is the modern standard: it directly fuses a high-fidelity **vision network** with **language logic**, enabling natural conversation about visual content.
- **Leading VLMs (as presented in the session):**
  - OpenAI — GPT-4.1 & GPT-5 Vision
  - Google — Gemini Pro & Ultra
  - Anthropic — Claude 3 Vision
  - Meta — Llama Vision
  - Alibaba — Qwen-VL

---

## 10. Audio & Video Understanding

### Audio
- Models like **Whisper, SpeechLM, SeamlessM4T** handle spoken language.
- Classic pipeline: **Speech → Text → Reasoning → Response**

### Video — "The Video Challenge"
- Video = **thousands of images + audio + time.**
- This introduces the need for **Temporal Reasoning**:
  - Understanding motion
  - Recognizing actions across frames
  - Detecting complex events over time

---

## 11. Document AI & OCR

- PDFs are **not just text files** — they contain tables, images, charts, headers/footers, and layouts that plain text parsers can't understand.
- **The Pipeline (classic approach):** Image → Raw OCR text → Clean structured JSON
- **Use cases:** Invoice extraction, resume parsing, contract analysis, medical report processing.

---

## 12. Multimodal RAG Pipeline

Extends classic RAG (text-only) so retrieval works across **all modalities**.

1. **Storage** — Vector databases store embeddings for text **alongside** image, audio, video, and PDF data.
2. **Query** — The user submits a query, which can itself be text, an image, or an audio clip.
3. **Retrieval** — The system fetches related multimedia chunks (tables, charts, audio fragments, images).
4. **Generation** — The LLM synthesizes context across all retrieved modalities to produce one grounded final answer.

---

## 13. Automatic Tool Calling (Agentic Behavior)

Agents act autonomously by calling the right tool for the right job:

| Category | Example Tools |
|---|---|
| **Perception Tools** | Image API, OCR Engine, Speech Recognizer, Camera Integration |
| **Data & Web** | Web Search, Browser Automation, Database Queries, Maps & GPS |
| **Compute & Action** | Python Runtime, Calculator, Calendar Sync, Email Automation |

---

## 14. The Multimodal Agent — "Action Beyond Words"

Agents don't just *talk* — they **act**, using tools such as:
- **OCR Tool** — read receipts
- **Image Tool** — edit or generate images
- **Search Tool** — look up live data
- **Python Tool** — run math / analysis

---

## 15. Hands-On Code Walkthrough (from session repo)

All demo scripts follow **one repeating pattern**:
> `contents = [some media, some text]` → model → answer. Only the media type changes.

| File | Topic | Core Idea |
|---|---|---|
| `00_create_samples.py` | Setup | Generates demo images/audio/PDF for the exercises |
| `01_vlm.py` | Vision Language Model | Send `image + question` → get an answer; also compares two images side by side |
| `02_audio_lm.py` | Audio (classic route) | `wave` + `numpy` extract signal measurements (loudness, silence, energy); offline CMU Sphinx produces a rough transcript; the **LLM never hears the audio** — it only reasons over numbers + text |
| `03_video_understanding.py` | Video (classic + direct) | OpenCV samples frames to measure brightness/colour/motion and detect scene changes → LLM narrates from the timeline (classic). Also shows the **direct** approach: uploading the raw video via the File API so the model watches it itself |
| `04_ocr_pipeline.py` | OCR Pipeline | Tesseract extracts raw text from an image → LLM structures it into clean JSON (shop name, items, total) |
| `05_document_understanding.py` | Full Document Understanding | Sends an entire PDF directly to the model (no manual parsing) to summarize, extract tables, explain charts, and describe structure |
| `06_multimodal_rag.py` | Multimodal RAG | Caption every image with a VLM → embed captions → embed the user's question → cosine-similarity search finds the best-matching image → send that real image + question back to the model for the final answer |
| `07_tool_calling.py` | Tool / Function Calling | Shows both **manual** (see each step: model requests a call → you run it → you return the result) and **automatic** (SDK handles the loop) function calling — this is what turns a model into an **agent** |
| `08_audio_whisper_llm.py` | Audio (modern route) | Same two-step idea as File 2, but uses a modern Whisper STT model (via Groq) instead of classic Sphinx for a far more accurate transcript before the LLM reasons over the text |

### Key contrast repeated across files: Classic vs Direct pipelines
- **Classic pipeline:** dumb, specialized tool extracts *numbers/text* from raw media (OpenCV, wave+numpy, Tesseract, Sphinx) → LLM only ever sees those numbers/text, never the raw pixels/audio. Cheap, fast, explainable (you can inspect the intermediate values).
- **Direct pipeline:** the raw media (image, video, PDF) is hand to a natively multimodal model (VLM), which perceives it itself. Fewer moving parts, but less explainable — no intermediate numbers to inspect.

---

## 16. Big-Picture Takeaways

- A modality is just a "channel" of data — text, vision, audio, video, structured data — and multimodal AI reasons across all of them together instead of one at a time.
- Encoders turn raw data into embeddings; the LLM only ever "sees" embeddings, never raw pixels or sound waves.
- **Contrastive learning** creates a shared embedding space so different modalities (image of a cat / word "cat") can be compared and reasoned over together.
- VLMs are today's standard architecture for combining vision + language.
- Multimodal RAG follows the same storage → query → retrieval → generation loop as text RAG, just extended to images/audio/video/PDFs.
- Tool calling is what turns a multimodal model into an **agent**: it can perceive (OCR, image, speech), fetch (web, DB, maps), and act (Python, calendar, email) — not just talk.
