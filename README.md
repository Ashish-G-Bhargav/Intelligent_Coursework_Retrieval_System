<div align="center">

# 🤖 RAG-Based Telegram Study Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" />
  <img src="https://img.shields.io/badge/RAG-Powered-orange?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
  <img src="https://img.shields.io/github/stars/harshithreddy1903-cmyk/Telegram_Study_Bot?style=for-the-badge" />
</p>

<p align="center">
  An AI-powered <strong>Retrieval-Augmented Generation (RAG)</strong> study assistant built on Telegram — helping students <em>download notes</em>, <em>ask subject-specific questions</em>, and <em>ace their exams</em>.
</p>

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Bot Commands](#-bot-commands)
- [Environment Variables](#-environment-variables)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧠 Overview

The **Telegram Study Bot** is an intelligent AI assistant designed to streamline study sessions for students. It combines **web scraping**, **vector-based retrieval**, and **large language models** to deliver accurate, context-aware answers directly through Telegram.

> Instead of digging through PDFs and bookmarks, just ask the bot — it knows your syllabus!

---

## ✨ Features

| Feature | Description |
|---|---|
| 📥 **Note Downloader** | Download subject-specific study materials by branch and subject code |
| 🔍 **RAG Q&A Engine** | Ask questions and get answers grounded in your actual study materials |
| 📚 **Subject Explorer** | Browse all available subjects in an organized way |
| 🌐 **Web Scraper** | Automatically scrapes and indexes content from educational sources |
| 💬 **Telegram UI** | Friendly, command-driven interface accessible from any device |
| ⚡ **Vector Search** | Lightning-fast semantic search powered by a local vector database |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Telegram User                       │
└──────────────────────────┬──────────────────────────────┘
                           │  /ask, /download, /subjects
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   telegram_bot.py                        │
│              (Command Handler & Router)                  │
└───────┬────────────────────────┬────────────────────────┘
        │                        │
        ▼                        ▼
┌───────────────┐       ┌────────────────────┐
│  scraper.py   │       │      rag.py         │
│ (Web Scraper  │       │  (RAG Pipeline:     │
│  & Downloader)│       │  Embed → Store →    │
└───────┬───────┘       │  Retrieve → Answer) │
        │               └────────┬───────────┘
        ▼                        ▼
┌───────────────┐       ┌────────────────────┐
│  notes/       │       │   vector_db/        │
│ (Downloaded   │       │ (ChromaDB / FAISS   │
│   PDFs)       │       │  Vector Store)      │
└───────────────┘       └────────────────────┘
```

---

## 🛠️ Tech Stack

- **Python 3.9+** — Core language
- **python-telegram-bot** — Telegram Bot API wrapper
- **LangChain** — RAG pipeline orchestration
- **ChromaDB / FAISS** — Vector database for semantic retrieval
- **BeautifulSoup / Requests** — Web scraping & note downloading
- **OpenAI / Ollama** — LLM for answer generation
- **dotenv** — Secure environment variable management

---

## 📁 Project Structure

```
Telegram_Study_Bot/
├── src/
│   ├── telegram_bot.py       # Main bot logic, command handlers & routing
│   ├── scraper.py            # Web scraper for downloading study materials
│   ├── rag.py                # RAG pipeline: embed, store, retrieve & generate
│   └── __init__.py           # Package initializer
│
├── data/
│   ├── sources.json          # Subject codes → source URLs mapping
│   ├── notes_link.json       # Subject codes → downloadable notes links
│   ├── sub_name.json         # Subject codes → subject names mapping
│   └── .gitkeep
│
├── notes/                    # Downloaded study material PDFs
│   └── .gitkeep
│
├── vector_db/                # Persisted vector embeddings
│   └── .gitkeep
│
├── .env.example              # Template for environment variables
├── .gitignore
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup & metadata
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- A [Telegram Bot Token](https://core.telegram.org/bots/tutorial) from [@BotFather](https://t.me/BotFather)
- An OpenAI API key (or a locally running Ollama instance)

### 1. Clone the Repository

```bash
git clone https://github.com/harshithreddy1903-cmyk/Telegram_Study_Bot.git
cd Telegram_Study_Bot
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Then open `.env` and fill in your credentials (see [Environment Variables](#-environment-variables)).

### 5. Run the Bot

```bash
python src/telegram_bot.py
```

Your bot is now live! Open Telegram and search for your bot to start chatting. 🎉

---

## 💬 Usage

Once the bot is running, interact with it through Telegram:

1. Search for your bot by name in Telegram
2. Hit **Start** or type `/start`
3. Use `/subjects` to explore available study materials
4. Use `/download` to grab notes for a specific subject
5. Use `/ask` followed by your question to get AI-powered answers

---

## 🤖 Bot Commands

| Command | Description | Example |
|---|---|---|
| `/start` | Start the bot & view main menu | `/start` |
| `/help` | Display all available commands | `/help` |
| `/subjects` | List all available subjects | `/subjects` |
| `/download <branch> <subject_code>` | Download notes for a subject | `/download CSE CS101` |
| `/ask <question>` | Ask a question about study materials | `/ask What is a B-tree?` |

---

## 🔐 Environment Variables

Create a `.env` file based on `.env.example` and fill in the following:

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from BotFather |
| `OPENAI_API_KEY` | Your OpenAI API key (if using OpenAI) |
| `VECTOR_DB_PATH` | Path to store the vector database (default: `./vector_db`) |
| `NOTES_DIR` | Directory for downloaded notes (default: `./notes`) |

> **Tip:** Never commit your `.env` file. It's already included in `.gitignore`.

---

## 🤝 Contributing

Contributions are warmly welcome! Here's how to get involved:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit** your changes:
   ```bash
   git commit -m "feat: add your feature description"
   ```
4. **Push** to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open** a Pull Request and describe your changes

Please check open [Issues](https://github.com/harshithreddy1903-cmyk/Telegram_Study_Bot/issues) before creating new ones.

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.

---

  ⭐ If you found this project helpful, consider giving it a star!
</div>
