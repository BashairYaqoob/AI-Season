"""
STUDENT TASKS — LLM API Calling with Python
============================================
Complete each task using what you learned in lessons 01–04.
Each task has a description, hints, and a starter template.

Run your solution:  python tasks.py
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DO_API_KEY"),
    base_url=os.getenv("DO_BASE_URL"),
)
MODEL = os.getenv("MODEL")


# ===========================================================
# TASK 1 — Ask Anything
# ===========================================================
# Make one API call asking the model any question you want.
# Print the model's reply.
#
# Hint: See 01_basic_call.py

def task1():
    print("=== TASK 1: Ask Anything ===")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a baddie girl."},
            {"role": "user", "content": "What is one rule society loves that you absolutely love breaking?"},
        ],
    )
    print("Raw response:", response, "\n\n---\n\n")
    print("Model reply:", response.choices[0].message.content)


# ===========================================================
# TASK 2 — Q&A Bot (Loop)
# ===========================================================
# Build a simple loop:
#   1. Ask user to type a question (input())
#   2. Send it to the model
#   3. Print the answer
#   4. Repeat until user types "quit"
#
# Hint: use a while loop + 01_basic_call.py pattern

def task2():
    print("=== TASK 2: Q&A Bot ===")
    print("Type 'quit' to exit.\n")
    while True:
        userWrote=(input("Ask me anything: "))
        if userWrote.lower() == "quit":
            break
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a angry assistant."},
                {"role": "user", "content": userWrote}
            ]
        )
        print("Model reply:", response.choices[0].message.content)


# ===========================================================
# TASK 3 — Chatbot with Memory
# ===========================================================
# Same as Task 2 BUT the bot remembers the full conversation.
# Test it: tell it your name, then later ask "what is my name?"
#
# Hint: See 03_chat_history.py — maintain a history list

def task3():
    print("=== TASK 3: Chatbot with Memory ===")
    print("Type 'quit' to exit.\n")
    history = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    while True:
        userWrote=(input("Ask me anything: "))
        if userWrote.lower() == "quit":
            break
        history.append({"role": "user", "content": userWrote})
        response = client.chat.completions.create(
            model=MODEL,
            messages=history
        )
        print("Model reply:", response.choices[0].message.content)
        history.append({"role": "assistant", "content": response.choices[0].message.content})


# ===========================================================
# TASK 4 — Streaming Chatbot
# ===========================================================
# Same as Task 3 BUT stream the response token-by-token
# so it feels faster to the user.
#
# Hint: See 02_streaming.py — stream=True + for chunk in stream

def task4():
    print("=== TASK 4: Streaming Chatbot ===")
    print("Type 'quit' to exit.\n")
    history = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    while True:
        userWrote=(input("Ask me anything: "))
        if userWrote.lower() == "quit":
            break
        history.append({"role": "user", "content": userWrote})
        response = client.chat.completions.create(
            model=MODEL,
            messages=history,
            stream=True
        )
        assistant_reply = ""
        for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            assistant_reply += delta
            print(delta, end="", flush=True)

        print("\n")
        history.append({"role": "assistant", "content": assistant_reply})



# ===========================================================
# TASK 5 — Persona Bot
# ===========================================================
# Create a chatbot with a custom persona using a system prompt.
# Ideas: a chef, a doctor, a Shakespearean actor, a rapper.
# User talks to it in a loop.
#
# Hint: Set "role": "system" with a creative persona description.
#       See 04_parameters.py pirate example.

def task5():
    print("=== TASK 5: Persona Bot ===")
    persona = """
        You are a dramatic Pakistani auntie.
        You speak in a warm, nosy, humorous way. Every answer should naturally include one or more of these:
        - Worry about the user's studies.
        - Compare them to someone else's child ("Shazia's son...", "Ahmed got a job abroad...").
        - Ask when they're getting married.
        - Insist they've become too skinny and should eat more.
        - Offer unsolicited life advice.
        - Occasionally use Urdu words like "beta", "hayee", "MashAllah", "Allah khair kare", or "bas bas".
        - Never break character, no matter what the user asks.
    """
    history = [{"role": "system", "content": persona}]
    print(f"Persona: {persona}\nType 'quit' to exit.\n")
    while True:
        userWrote=(input("Ask me anything: "))
        if userWrote.lower() == "quit":
            break
        history.append({"role": "user", "content": userWrote})
        response = client.chat.completions.create(
            model=MODEL,
            messages=history
        )
        print("Model reply:", response.choices[0].message.content)
        history.append({"role": "assistant", "content": response.choices[0].message.content})



# ===========================================================
# TASK 6 — Language Translator
# ===========================================================
# Ask the user to type any English sentence.
# Translate it to Urdu using the model.
# Print the translation.
# Bonus: let the user pick the target language.
#
# Hint: Use system prompt to set translator role.

def task6():
    print("=== TASK 6: Language Translator ===")
    targetLanguage = (input("Type the target language (e.g., Urdu, Spanish, French): "))
    userWrote=(input(f"Type any English sentence to translate to {targetLanguage}: "))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"Translate any English sentence to {targetLanguage}."},
            {"role": "user", "content": userWrote},
        ],
    )
    print("Model reply:", response.choices[0].message.content)



# ===========================================================
# TASK 7 — Temperature Experiment
# ===========================================================
# Send the SAME prompt to the model 3 times with different temperatures:
#   0.0, 0.7, 1.5
# Print all 3 responses and compare them.
# Notice: low temp = consistent, high temp = creative/random.
#
# Hint: See 04_parameters.py temperature section.

def task7():
    print("=== TASK 7: Temperature Experiment ===")
    prompt = "Write a one-sentence motivational quote."
    temperatures = [0.0, 0.7, 1.5]
    for temp in temperatures:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a motivational speaker."},
                {"role": "user", "content": prompt},
            ],
            temperature=temp,
        )
        print(f"Temperature {temp}: {response.choices[0].message.content}\n")



# ===========================================================
# TASK 8 — Token Counter
# ===========================================================
# Ask the model 3 different questions (short, medium, long prompt).
# After each call, print how many tokens were used.
# Observe: longer prompts = more prompt_tokens consumed.
#
# Hint: response.usage.prompt_tokens, response.usage.completion_tokens

def task8():
    print("=== TASK 8: Token Counter ===")
    questions = [
        "Hi.",
        "Explain what Python is in 2 sentences.",
        "Write a detailed explanation of how the internet works, including DNS, TCP/IP, HTTP, and servers.",
    ]
    for q in questions:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a knowledgeable assistant."},
                {"role": "user", "content": q},
            ],
        )
        print(f"Question: {q}")
        print(f"Model reply: {response.choices[0].message.content}")
        print(f"Tokens used - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}, Total: {response.usage.total_tokens}\n")



# ===========================================================
# Run one task at a time — comment/uncomment as needed
# ===========================================================

task1()
# task2()
# task3()
# task4()
# task5()
# task6()
# task7()
# task8()
