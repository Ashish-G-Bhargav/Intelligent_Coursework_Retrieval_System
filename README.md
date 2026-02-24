<!-- Animated Banner -->
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6a11cb,100:2575fc&height=200&section=header&text=Telegram%20Study%20Bot&fontSize=48&fontColor=ffffff&fontAlignY=38&desc=Your%20AI-Powered%20RAG%20Study%20Companion&descAlignY=58&descSize=18&animation=fadeIn" width="100%"/>

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=2575FC&center=true&vCenter=true&width=600&lines=Ask+questions+from+your+notes+%F0%9F%93%96;Download+study+materials+instantly+%F0%9F%93%A5;Powered+by+RAG+%2B+LLMs+%F0%9F%A4%96;Runs+on+Telegram+%E2%9C%88%EF%B8%8F" alt="Typing SVG" />
</a>

<br/><br/>

<img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
&nbsp;
<img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white"/>
&nbsp;
<img src="https://img.shields.io/badge/LangChain-Enabled-121212?style=for-the-badge&logo=chainlink&logoColor=white"/>
&nbsp;
<img src="https://img.shields.io/badge/Vector%20DB-ChromaDB-FF6B6B?style=for-the-badge&logo=databricks&logoColor=white"/>

<br/>

<img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge"/>
&nbsp;
<img src="https://img.shields.io/github/stars/harshithreddy1903-cmyk/Telegram_Study_Bot?style=for-the-badge&color=f59e0b&logo=github"/>
&nbsp;
<img src="https://img.shields.io/github/forks/harshithreddy1903-cmyk/Telegram_Study_Bot?style=for-the-badge&color=8b5cf6&logo=github"/>
&nbsp;
<img src="https://img.shields.io/github/issues/harshithreddy1903-cmyk/Telegram_Study_Bot?style=for-the-badge&color=ef4444&logo=github"/>

</div>

---

## 🌟 What is This?

<table>
<tr>
<td width="60%">

**Telegram Study Bot** is an **AI-powered study companion** that lives inside Telegram. It uses **Retrieval-Augmented Generation (RAG)** to deeply understand your subject materials — then answers your questions based on *your actual syllabus*, not generic internet knowledge.

> 💡 Stop Googling. Stop scrolling PDFs.  
> Just **ask the bot** and get instant, contextual answers.

</td>
<td width="40%" align="center">

```
🧑‍🎓  You ask a question
        ↓
📚  Bot searches your notes
        ↓
🧠  LLM generates the answer
        ↓
💬  Answer sent to Telegram
```

</td>
</tr>
</table>

---

## ✨ Feature Highlights

<div align="center">

| 🚀 Feature | 📝 Description |
|:---:|:---|
| 📥 **Smart Downloader** | Download branch & subject-specific notes in seconds |
| 🤖 **RAG Q&A Engine** | Get answers grounded in *your* study material |
| 📚 **Subject Explorer** | Browse the full subject catalog with one command |
| 🌐 **Auto Web Scraper** | Scrapes & indexes educational resources automatically |
| ⚡ **Vector Semantic Search** | Finds the most relevant chunks from thousands of pages |
| 💬 **Telegram Native** | Fully chat-based — no app downloads, no signups |
| 🔐 **Secure Config** | `.env`-based secrets management, nothing hardcoded |

</div>

---

## 🏗️ System Architecture

```
╔══════════════════════════════════════════════════════════╗
║                    🧑‍💻  Telegram User                    ║
║              /start  /ask  /download  /subjects           ║
╚══════════════════════════╦═══════════════════════════════╝
                           ║
                           ▼
╔══════════════════════════════════════════════════════════╗
║              📡  telegram_bot.py                         ║
║         Command Handler, Router & Response Manager       ║
╚══════════╦═══════════════════════════╦═══════════════════╝
           ║                           ║
           ▼                           ▼
╔══════════════════╗        ╔═══════════════════════════╗
║  🌐 scraper.py   ║        ║       🧠 rag.py            ║
║  ─────────────── ║        ║  ─────────────────────────║
║  Web Scraping    ║        ║  1. Chunk Documents        ║
║  PDF Downloading ║        ║  2. Generate Embeddings    ║
║  Content Parsing ║        ║  3. Store in Vector DB     ║
╚════════╦═════════╝        ║  4. Retrieve & Re-rank     ║
         ║                  ║  5. LLM Answer Generation  ║
         ▼                  ╚══════════╦════════════════╝
╔════════════════╗                     ║
║  📁 notes/     ║      ╔══════════════▼═══════════════╗
║  Downloaded    ║      ║   🗄️  vector_db/              ║
║  PDFs & Docs   ║      ║   ChromaDB / FAISS Store      ║
╚════════════════╝      ╚══════════════════════════════╝
```

---

## 🛠️ Tech Stack

<div align="center">
<img src="https://skillicons.dev/icons?i=python,github,vscode&theme=dark" />
</div>

<br/>

| Layer | Technology | Purpose |
|:---:|:---:|:---|
| 🤖 **Bot Framework** | `python-telegram-bot` | Telegram API integration & command routing |
| 🔗 **AI Orchestration** | `LangChain` | RAG pipeline, prompt management |
| 🗄️ **Vector Database** | `ChromaDB / FAISS` | Semantic embedding storage & retrieval |
| 📡 **Web Scraping** | `BeautifulSoup + Requests` | Scrape and index educational content |
| 🧠 **LLM Backend** | `OpenAI API / Ollama` | Natural language answer generation |
| 🔐 **Config** | `python-dotenv` | Secure environment variable management |

---

## 📁 Project Structure

```bash
📦 Telegram_Study_Bot/
│
├── 📂 src/
│   ├── 🤖 telegram_bot.py      # Command handlers, routing, user interaction
│   ├── 🌐 scraper.py           # Web scraper & notes downloader
│   ├── 🧠 rag.py               # Full RAG pipeline
│   └── 🐍 __init__.py
│
├── 📂 data/
│   ├── 📄 sources.json         # Subject codes → scraping source URLs
│   ├── 📄 notes_link.json      # Subject codes → downloadable note links
│   └── 📄 sub_name.json        # Subject codes → human-readable names
│
├── 📂 notes/                   # 📥 Downloaded study material storage
├── 📂 vector_db/               # 🗄️ Persisted vector embeddings
│
├── 📄 .env.example             # 🔐 Environment variable template
├── 📄 requirements.txt         # 📦 Python dependencies
├── 📄 setup.py                 # ⚙️ Package metadata
└── 📖 README.md
```

---

## 🚀 Getting Started

### ✅ Prerequisites

- [ ] **Python 3.9+** → [Download](https://python.org/downloads)
- [ ] **Telegram Bot Token** → Get from [@BotFather](https://t.me/BotFather)
- [ ] **OpenAI API Key** → [Get here](https://platform.openai.com/api-keys) *(or use Ollama locally)*

---

### ⚡ Quick Setup

**Step 1 — Clone & Enter**
```bash
git clone https://github.com/harshithreddy1903-cmyk/Telegram_Study_Bot.git
cd Telegram_Study_Bot
```

**Step 2 — Virtual Environment**
```bash
python -m venv venv

# 🐧 Linux/macOS
source venv/bin/activate

# 🪟 Windows
venv\Scripts\activate
```

**Step 3 — Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4 — Configure & Launch**
```bash
cp .env.example .env
# Edit .env with your API keys, then:
python src/telegram_bot.py
```

> 🎉 **Done!** Head to Telegram, find your bot, and start studying smarter.

---

## 🤖 Bot Commands

<div align="center">

| Command | 🛠️ Action | 💡 Example |
|:---|:---:|:---|
| `/start` | Launch bot & show main menu | `/start` |
| `/help` | View all commands | `/help` |
| `/subjects` | Browse full subject catalog | `/subjects` |
| `/download <branch> <code>` | Download notes | `/download CSE CS401` |
| `/ask <question>` | Ask AI from your notes | `/ask Explain Dijkstra's algorithm` |

</div>

---

## 🔐 Environment Variables

| Variable | Required | Description |
|:---|:---:|:---|
| `TELEGRAM_BOT_TOKEN` | ✅ | Token from [@BotFather](https://t.me/BotFather) |
| `OPENAI_API_KEY` | ✅ | Your OpenAI secret key |
| `VECTOR_DB_PATH` | ⚙️ Optional | Custom vector DB path *(default: `./vector_db`)* |
| `NOTES_DIR` | ⚙️ Optional | Custom notes directory *(default: `./notes`)* |

> ⚠️ **Never commit your `.env`!** It's already in `.gitignore`.

---

## 🤝 Contributing

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/Telegram_Study_Bot.git

# 2. Create your branch
git checkout -b feature/amazing-feature

# 3. Commit with conventional commits
git commit -m "feat: add amazing feature"

# 4. Push & open a PR
git push origin feature/amazing-feature
```

Check [open issues](https://github.com/harshithreddy1903-cmyk/Telegram_Study_Bot/issues) for contribution ideas!

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](./LICENSE) for details.

---

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2575fc,100:6a11cb&height=120&section=footer" width="100%"/>

<div align="center">

*If this helped you, drop a ⭐ — it means the world!*

[![Star](https://img.shields.io/github/stars/harshithreddy1903-cmyk/Telegram_Study_Bot?style=social)](https://github.com/harshithreddy1903-cmyk/Telegram_Study_Bot/stargazers)

</div>
