# AI Season Notes

## 1. The Big Picture
```text
User
   │
   ▼
Python Code
   │
   ▼
OpenAI SDK
   │
   ▼
API
   │
   ▼
AI Model
   │
   ▼
Response
```
I am NOT building an AI.
I am building software that USES an AI.

# 2. New Words

| Term | Meaning |
|------|---------|
| **Model** | The AI brain (GPT, Llama, Gemini, DeepSeek, etc.) |
| **API** | Bridge between my code and the AI |
| **SDK** | Python library that makes using the API easy |
| **API Key** | Secret password that authenticates my requests |
| **Base URL** | Address of the AI server |
| **Model Name** | Specifies which AI model to use |

# 3. Project Structure
```text
project/
│
├── tasks.py
├── .env
├── .gitignore
└── README.md
```
`.env`
```env
DO_API_KEY=...
DO_BASE_URL=...
MODEL=...
```
Never upload `.env` to GitHub.

---
# 4. Python Imports
```python
import os  # Used for operating system features. Mostly to read environment variables.
from dotenv import load_dotenv # Imports the OpenAI SDK.
from openai import OpenAI

load_dotenv()

client = OpenAI( #creates connection
    api_key=os.getenv("DO_API_KEY"),
    base_url=os.getenv("DO_BASE_URL")
)

MODEL = os.getenv("MODEL")
```
---

# 5. Basic API Call
Every task follows this pattern:
```text
User Input
      ↓
Create messages
      ↓
Call API
      ↓
Read response
```

```python
response = client.chat.completions.create(  #sends request
    model=MODEL,
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)

print(response.choices[0].message.content)
```

---

# 6 . Messages
The AI reads a **list of messages**, not a single string.

```python
messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
]
```

---

# 7. Roles
| Role      | Purpose                               |
| --------- | ------------------------------------- |
| system    | Gives the AI instructions/personality |
| user      | User's message                        |
| assistant | AI's previous replies                 |

# 8. Chat History (Memory)
LLMs are **stateless**. The **history list is the memory.**

```python
history.append({"role": "user", "content": user_input})
response = client.chat.completions.create(
    model=MODEL,
    messages=history
)
assistant_reply = response.choices[0].message.content
history.append({
    "role": "assistant", "content": assistant_reply
})
```

Flow:
```text
User
 ↓
Append user
 ↓
Send history
 ↓
Receive reply
 ↓
Append assistant
```
---

# 9. Streaming

Without streaming
```text
Wait...
↓↓↓
Whole response
```

With streaming
```text
H
He
Hel
Hell
Hello
```

```python
assistant_reply = ""
for chunk in response:
    delta = chunk.choices[0].delta.content or ""
    assistant_reply += delta
    print(delta, end="", flush=True)

history.append({
    "role": "assistant",
    "content": assistant_reply
})
```
- `delta` = one small piece
- `assistant_reply` = full response

---
# 10. Parameters
### Persona
The system prompt controls the AI's behavior.

```python
{
    "role": "system", "content": "You are a pirate."
}
```

---

### temperature
Controls creativity.

| Temperature | Result |
|-------------|--------|
| 0.0 | Consistent |
| 0.7 | Balanced |
| 1.5 | Creative |
---

### max_tokens

Maximum length of the response.

---

# 11. Tokens
AI counts **tokens**, not words.

```python
response.usage.prompt_tokens
response.usage.completion_tokens
response.usage.total_tokens
```

- Longer prompt → more prompt tokens
- Longer answer → more completion tokens
- More tokens → higher cost

---

# 12. Response Object

The API returns a large object.

```text
response
├── choices
├── usage
├── model
└── id
```

Most commonly used:
```python
response.choices[0].message.content
```
---

# 13. Common Errors
| Error | Cause |
|-------|-------|
| ModuleNotFoundError | Package not installed |
| Authentication Error | Wrong API key |
| Model Not Found | Wrong model name |
| None from getenv() | `.env` not loaded |

---
# 14. Mental Model
Don't read
```python
client.chat.completions.create(...)
```
Read
> Send this message to the AI.

Don't read
```python
response.choices[0].message.content
```
Read
> Get the AI's answer.

Translate code into English first.
---
# 15. Golden Rule ⭐

Programming isn't about memorizing syntax.
It's about understanding **the flow of data**.

```text
Input
 ↓
Prompt
 ↓
API Call
 ↓
AI Model
 ↓
Response
 ↓
Display
```

Almost every AI application follows this exact pattern.

---

# 16. GitHub Rules
Never upload
```text
.env
```
Always ignore it.
```text
.gitignore
.env
```
---

# 🚗 Parking Lot (Things to Learn Later)

- REST API
- JSON
- HTTP request & response
- Async programming
- Embeddings
- Vector database
- RAG
- Function calling / Tools
- Agents
- MCP
- Tokenization
