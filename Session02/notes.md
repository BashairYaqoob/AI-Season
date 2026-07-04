# AI Season - Day 2: Prompt Engineering & Agent Architectures

## Overview

This session focused on **Prompt Engineering**, **Context Engineering**, **AI Agents**, and **Vibe Coding**. The main takeaway is that the quality of an AI's response depends largely on the quality of the prompt provided.

---

# What is Prompt Engineering?

Prompt Engineering is the process of writing clear and structured instructions that guide an AI model to produce accurate, relevant, and predictable responses.

### Golden Rule

```
Good Prompt
      ↓
Better Context
      ↓
Better Reasoning
      ↓
Better Output
```

### Why It Matters

AI does not understand human intentions—it predicts the most likely next words based on the context it receives. The clearer the context, the better the response.

---

# Anatomy of a Good Prompt

A good prompt consists of **five key components**.

## 1. Role Assignment

Tell the AI who it should act as.

**Example**

```text
You are a Senior React Developer.
```

---

## 2. Clear Task

Clearly define what needs to be done.

❌ Bad

```text
Build a website.
```

✅ Good

```text
Create a responsive travel booking homepage using React.
```

---

## 3. Context

Provide background information about the project.

**Example**

```text
Tech Stack:
- React
- Tailwind CSS
- Vite
```

The more relevant context you provide, the better the AI can understand your requirements.

---

## 4. Constraints

Specify what the AI should avoid.

**Example**

```text
- Don't use Bootstrap
- Don't use TypeScript
- Don't include explanations
```

Constraints help reduce unwanted outputs.

---

## 5. Output Format

Tell the AI exactly how to respond.

**Examples**

```text
Return only Python code.
```

```text
Return JSON.
```

```text
Return a Markdown table.
```

This is especially useful when another program needs to process the output.

---

# Bad Prompt vs Good Prompt

### ❌ Bad Prompt

```text
Write a responsive e-commerce website.
```

Problems:

- Generic layout
- Random CSS
- Extra comments
- Inconsistent structure

---

### ✅ Good Prompt

```text
Act as a React UI Engineer.

Create a responsive e-commerce landing page.

Use Tailwind CSS.

Return only modular React components.

Do not include explanations.
```

Result:

- Cleaner code
- Better UI
- Production-ready output
- Less unnecessary text

---

# Core Prompting Techniques

## 1. Zero-Shot Prompting

No examples are provided.

Simply ask the AI to complete a task.

**Example**

```text
Translate this sentence into French.
```

### Best Used For

- General questions
- Simple coding tasks
- Summaries
- Basic translations

---

## 2. Few-Shot Prompting

Provide examples before asking the actual question.

**Example**

```text
Input: Cat
Output: Animal

Input: Rose
Output: Plant

Input: Car
Output:
```

The AI follows the demonstrated pattern.

### Best Used For

- Classification
- Consistent formatting
- Specific writing styles

---

## 3. Chain of Thought (CoT)

Ask the AI to reason through the problem before providing the answer.

**Example**

```text
Solve this problem step by step, then provide the final answer.
```

### Best Used For

- Mathematics
- Algorithms
- Debugging
- System design
- Complex reasoning

---

## 4. Role Prompting

Assign a professional role to the AI.

**Examples**

```text
You are a Senior Software Engineer.
```

```text
You are a Cybersecurity Expert.
```

```text
You are a UI/UX Designer.
```

The AI answers from the perspective of that role.

---

## 5. System Instructions

These are high-level instructions that define the AI's behavior throughout a conversation.

**Example**

```text
Always respond in Markdown.

Keep answers under 200 words.

Never include explanations unless requested.
```

Unlike normal prompts, system instructions remain active for the conversation or application.

---

# Zero-Shot vs Few-Shot

| Zero-Shot | Few-Shot |
|------------|-----------|
| No examples | Examples provided |
| Faster | More accurate formatting |
| Suitable for simple tasks | Suitable for pattern-based tasks |
| AI chooses the style | AI follows the demonstrated style |

---

# Chain of Thought Workflow

```
Problem
      ↓
Step-by-Step Reasoning
      ↓
Verification
      ↓
Final Answer
```

Breaking complex problems into smaller reasoning steps usually improves accuracy.

---

# Role Prompting Examples

### Architect

Focuses on:

- System design
- Scalability
- Maintainability
- Deployment

---

### Security Expert

Checks:

- Vulnerabilities
- Secure coding practices
- Dependencies
- Authentication

---

### QA Engineer

Focuses on:

- Bugs
- Edge cases
- Testing
- Performance

---

# Context Engineering

Context is one of the most important factors when working with AI.

Instead of saying:

```text
Fix my project.
```

Provide additional context:

```text
Here is my React component.

Here is my API.

Here is the database schema.

Fix the authentication issue.
```

More context generally produces better and more accurate responses.

---

# Structured Outputs

Instead of asking for general explanations, specify the desired format.

Examples:

```text
Return JSON.
```

```text
Return Markdown.
```

```text
Return only SQL queries.
```

```text
Return only Python code.
```

Structured outputs are easier to integrate into applications and workflows.

---

# Prompt Chaining

Instead of asking AI to complete an entire project in one prompt, divide the work into smaller steps.

Example workflow:

```
Step 1
Design Database

↓

Step 2
Build APIs

↓

Step 3
Create UI

↓

Step 4
Test & Debug
```

Prompt chaining improves accuracy and makes debugging much easier.

---

# AI Agents & Tool Calling

Large Language Models only know the information they were trained on.

To access real-time information or perform actions, they use **tools and APIs**.

Example:

```
User asks:
What's the weather today?

↓

AI calls Weather API

↓

API returns live weather

↓

AI generates the response
```

This is called **Tool Calling**.

---

# Common Prompt Engineering Mistakes

Avoid these common mistakes:

- Writing vague prompts
- Providing little or no context
- Forgetting constraints
- Asking AI to do everything in one prompt
- Not specifying the desired output format

---

# Vibe Coding

Vibe Coding is a modern development workflow where developers focus less on writing every line of code and more on:

- Designing solutions
- Writing high-level prompts
- Reviewing AI-generated code
- Testing
- Debugging
- Deploying

The AI writes much of the code, while the developer acts as the planner and reviewer.

---

# Modern Developer Workflow

Today's developers spend more time:

- Planning systems
- Guiding AI
- Reviewing generated code
- Testing applications
- Debugging issues

instead of manually writing every line of code.

---

# 25-Minute Production Build Workflow

The practical session follows these steps:

## Step 1 — Identify the Target

Choose the application to build.

Example:

```
Travel Planner App
```

---

## Step 2 — Apply Prompt Engineering

Write detailed prompts that include:

- Role
- Task
- Context
- Constraints
- Output format

---

## Step 3 — Iterative Refinement

Develop the project in stages:

1. Build the UI
2. Connect APIs
3. Debug issues
4. Improve the application

---

## Step 4 — Deploy

Deploy the completed application to a live staging server.

---

# Key Takeaways

- Better prompts produce better AI outputs.
- Always define the **Role**, **Task**, **Context**, **Constraints**, and **Output Format**.
- Provide enough context instead of expecting AI to guess.
- Use **Few-Shot** prompting for consistent formatting.
- Use **Chain of Thought** for complex reasoning.
- Use **Prompt Chaining** to break large tasks into smaller ones.
- Modern developers increasingly guide, review, and validate AI-generated code rather than writing everything from scratch.
