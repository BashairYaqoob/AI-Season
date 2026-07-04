# AI Season – Session 1

## Overview

This repository contains my solutions for Session 1 of the AI Season course.

## Topics Covered

- Basic API Calls
- Chatbot
- Chat History (Memory)
- Streaming Responses
- Persona Bot
- Language Translator
- Temperature
- Token Usage

## Tech Stack

- Python
- OpenAI Python SDK
- python-dotenv
- Groq API

## Project Structure

```
tasks.py
requirements.txt
.gitignore
README.md
```

## Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
DO_API_KEY=your_api_key
DO_BASE_URL=your_base_url
MODEL=your_model
```

Run

```bash
python tasks.py
```

## Note

The `.env` file is intentionally excluded because it contains private API credentials.
