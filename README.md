# 🧠 StudentHub AI

**StudentHub AI** is an **agentic AI system** built using **LangGraph**, designed to help students interact intelligently with their academic content.
It uses a structured flow of tools (agents) to perform summarization, quiz generation, document-based Q&A (RAG), and fallback web search when needed.

---

## 🔁 Agentic AI Flow

StudentHub uses **LangGraph** to manage a multi-step decision flow with the following tools:

- **Intent Classifier** – Identifies the user's intent: `qa`, `quiz`, `summary`, or `fallback`.
- **Summarizer Tool** – Summarizes provided content based on the subject.
- **Quiz Generator Tool** – Creates subject-specific quiz questions.
- **RAG Tool** – Retrieves answers from embedded documents using FAISS.
- **Fallback Tool** – Uses DuckDuckGo search and summarization for general queries.

Each tool is modular and only invoked when its corresponding intent is detected.

---

## ✨ Features

- 📚 Subject-specific support (e.g., Machine Learning, OS, CN)
- 💬 Chat UI with persistent session history
- 🔎 Intent-aware agent routing via LangGraph
- 📄 Upload PDFs and perform Q&A over them (RAG-based)
- 📝 Generate quizzes automatically from queries
- 📑 Summarize any academic or general content
- 🌐 Fallback to web search for non-subject queries

---

## 🧰 Tech Stack

- **LangGraph** – Agent orchestration & conditional routing
- **LangChain** – LLM tooling and prompt management
- **Streamlit** – Chat-based web UI
- **ChromaDB** – For Storing Document embedding 
- **Google Generative AI (Gemini)** – LLM backend for all tools
- **Tavily and DuckDuckGo API** – Web search fallback
- **Python** – Core language for the app logic
