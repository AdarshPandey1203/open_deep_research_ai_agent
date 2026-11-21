# 🔬 Open Deep Research AI Agent

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black.svg)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg)](https://ai.google.dev)
[![arXiv](https://img.shields.io/badge/Papers-arXiv%20API-b31b1b.svg)](https://arxiv.org)
[![Deploy on Render](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](https://render.com)

An autonomous multi-agent AI research assistant that conducts full literature reviews, synthesizes arXiv academic papers, scrapes live URLs, and answers document-grounded questions — all from a modern web interface.

---

## ✨ Features

- 🔬 **Deep Research Mode** — Autonomous 4-step pipeline: Plan → Search arXiv → Extract → Synthesize
- ⚡ **Fast Chat Mode** — Quick Q&A, URL scraping, PDF/DOCX analysis
- 📚 **arXiv Integration** — Fetches real peer-reviewed papers with abstracts & citations
- 🌐 **Web Intelligence** — Scrapes and analyzes any URL
- 📄 **Document RAG** — Upload PDF, DOCX, TXT for grounded answers
- 💡 **Executive Summaries** — Every response summarized in 1-2 sentences
- 📥 **Markdown Export** — Download full research sessions as `.md`
- ⚙️ **Live API Key** — Set/update Gemini key from the UI without restart
- 🌙 **Dark / Light Theme** — Persistent user preference
- 🛡️ **Zero-Crash Fallback** — Works even without an API key (built-in synthesizer)

---

## 📁 Project Structure

```
open_deep_research_ai_agent/
├── app.py                  # Flask backend (all routes & API endpoints)
├── genai_client.py         # Gemini LLM client with auto-fallback
├── research_summarizer.py  # 4-agent research pipeline (Plan→Search→Read→Write)
├── search_tool.py          # arXiv + DuckDuckGo unified search
├── scraper.py              # Resilient web scraper
├── document_processor.py   # PDF, DOCX, TXT extractor
├── summarizer.py           # Text summarization utilities
├── memory.py               # Persistent JSON session memory
├── frontend/
│   ├── index.html          # Modern SPA interface
│   ├── style.css           # Design system (dark/light, glassmorphism)
│   └── script.js           # Client logic (chat, history, pipeline tracker)
├── sessions/               # Auto-created: saved chat sessions
├── uploads/                # Auto-created: uploaded document storage
├── requirements.txt        # Python dependencies
├── Procfile                # Render/Heroku process definition
├── render.yaml             # Render Infrastructure-as-Code config
└── Dockerfile              # Docker container spec
```

---

## 🚀 Deploy on Render (Free — Recommended)

### Step 1 — Fork / Push to GitHub
Make sure this repository is on your GitHub account.

### Step 2 — Create a Render Web Service
1. Go to [Render Dashboard](https://dashboard.render.com) → **New +** → **Web Service**
2. Connect your GitHub repository
3. Use these settings:

| Setting | Value |
|---|---|
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT` |
| **Plan** | Free |

### Step 3 — Set Environment Variable
In Render dashboard → **Environment** tab, add:

| Key | Value |
|---|---|
| `GEMINI_API_KEY` | Your key from [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `PYTHON_VERSION` | `3.11.9` |

### Step 4 — Deploy!
Click **Create Web Service** — your live URL will be ready in ~2 minutes.

> 💡 You can also set/update the API key directly in the app's **Settings ⚙️** menu without redeploying.

---

## 💻 Run Locally

```bash
# 1. Clone
git clone https://github.com/AdarshPandey1203/open_deep_research_ai_agent.git
cd open_deep_research_ai_agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY="AIzaSy..."

# 4. Run
python app.py
```

Open → **http://127.0.0.1:5001**

---

## 🐳 Docker

```bash
docker build -t deep-research-agent .
docker run -p 5001:5001 -e GEMINI_API_KEY="your_key_here" deep-research-agent
```

---

## 🔑 Get a Free Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **Create API Key**
3. Paste it in `.env` **or** directly in the app's ⚙️ Settings modal
