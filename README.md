# J.A.R.V.I.S - AI Desktop Assistant

**Just A Rather Very Intelligent System**

An advanced, Iron Man-inspired desktop AI agent built with Python.

**JARVIS 6.0 is not just a chatbot.** It is a fully autonomous **OS-Level Agent** that operates using a sophisticated **Agentic ReAct Workflow**. Instead of relying on pre-coded command lists, JARVIS dynamically "thinks", selects tools, observes the results, and corrects itself in real-time to achieve complex goals—all running entirely locally on your machine.

Jarvis can execute abstract, multi-step tasks such as: `Jarvis, read my last 5 emails, summarize any important updates, and then schedule a reminder to write a reply tomorrow.` Jarvis will fetch the emails via IMAP, read them, summarize the content, speak the result to you, and independently schedule a background cron task.

<img width="1913" height="976" alt="image" src="https://github.com/user-attachments/assets/6ddb14de-41ee-497c-b41f-6be9aafb6e20" />

## 🚀 Key Features

### True Agentic Loop (ReAct)
* **Dynamic Tool Selection:** JARVIS doesn't use hardcoded paths. It uses a strict JSON-enforced ReAct (Reason + Act) loop to chain tools together (e.g., `cmd` -> `read` -> `speak` -> `DONE`).
* **Self-Correction:** If JARVIS hallucinates or encounters an error, the local system catches it, feeds the error back into the loop, and forces the LLM to correct its JSON output autonomously.
* **Dual-Model Intent Classification:** A lightweight model (`qwen2.5:0.5b`) rapidly classifies user intent as `CHAT` or `PLAN`, routing simple conversations to a single LLM call and complex tasks to the full agentic loop.

### RAG Long-Term Memory
* **Semantic Memory:** JARVIS remembers past conversations using a local **ChromaDB** vector database. Every interaction is embedded and stored persistently.
* **Context Retrieval:** When you ask a question, JARVIS performs a semantic similarity search to retrieve the most relevant past interactions and injects them as context—giving it long-term memory across sessions.
* **No Cloud Required:** All embeddings and vector search run locally. Your data never leaves your machine.

### Dual Interfaces
- **GUI Mode:** A futuristic Glass-morphism interface with an animated Arc Reactor HUD, real-time system stats (CPU, RAM, Disk Space, Weather), live audio spectrum visualizer, and integrated voice interaction.
- **CLI Mode:** A fast, clean terminal interface with ANSI color coding, execution timers, and asynchronous notification handling.

### Desktop Automation
* **Smart App Launcher:** A 3-layer launch system: `Custom Aliases` -> `System Commands` -> `AppOpener` (Fuzzy Search). It knows that "VS Code" means `code` and "Chrome" means `chrome.exe`.
* **Local Screen Analysis:** Can capture your screen and analyze visual data entirely locally using Ollama vision capabilities.
* **Keyboard & Clipboard Automation:** Can type text, simulate key shortcuts, and interact with the clipboard to fix code or inject content.
* **System Volume Control:** Adjusts Windows master volume through voice or text commands.

### Natural Interaction
* **Neural Voice (TTS):** Uses **Edge-TTS** with the `en-US-ChristopherNeural` voice for high-quality, natural speech output.
* **Voice Input (STT):** Dynamic voice activity detection via microphone with automatic silence detection—just speak and JARVIS starts listening.
* **Time Awareness:** Jarvis dynamically knows the current system time, allowing him to schedule tasks, manage exam deadlines, and understand temporal context.

## ⚙️ Core Architecture (The Brain)

JARVIS operates on a dynamic **Router-Planner-Executor** model:

1.  **The ReAct Loop (`jarvis_brain.py`):** The core engine. It feeds the user's prompt to the local LLM, receives a JSON tool call, executes the tool, and appends the `TOOL RESULT` back to the LLM's memory until the LLM explicitly calls the `DONE` action.
2.  **The RAG Memory (`jarvis_memory.py`):** A ChromaDB-backed semantic memory system that stores every interaction and retrieves relevant past context for each new query.
3.  **The Background Listener (`jarvis_cron.py`):** A daemon thread that monitors `cron_schedule.json`. When a task is due, it wakes up the ReAct loop invisibly in the background.
4.  **The Tool Router:** Safely maps LLM intents to Python functions, handling alias corrections to prevent execution failures.

### Available Tools

| Tool | Description |
|------|-------------|
| `cmd` | Execute Windows terminal commands (with safety whitelist/blacklist) |
| `browser` | Open URLs in the default web browser |
| `open_app` | Launch applications (aliases → system commands → fuzzy search) |
| `read` | Read file contents from disk |
| `write` | Create or overwrite text files |
| `type_text` | Type text into the currently focused application |
| `keyboard_press` | Simulate keyboard shortcuts (e.g., `ctrl+shift+n`) |
| `set_volume` | Set system master volume (0–100%) |
| `analyze_screen` | Capture screenshot and analyze with vision model |
| `speak` | Deliver voice notification to the user |
| `email_imap` | Check Gmail inbox via IMAP and return recent emails |

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Core** | Python 3.11 (Portable Environment) |
| **AI Models** | Ollama — `gemma4:e4b` (main brain), `qwen2.5:0.5b` (intent classifier) |
| **Vector DB** | ChromaDB (persistent local SQLite) |
| **GUI** | PyQt6 |
| **TTS** | Edge-TTS + pygame |
| **STT** | sounddevice + Google Speech Recognition |
| **Automation** | `AppOpener`, `pyperclip`, `pyautogui`, `pynput`, `subprocess` |
| **System** | `psutil` (CPU/RAM/Disk), `pycaw` (volume control) |
| **Email** | `imaplib` (Gmail IMAP) |
| **Weather** | Open-Meteo API |

## 📂 Project Structure

```text
JARVIS-AI-Assistant/
├── main.py                  # Entry point. Unified launcher for CLI & GUI.
├── installer.py             # Automated Setup Wizard (Tkinter GUI).
├── test_jarvis.py           # System diagnostics and automated health checks.
├── requirements.txt         # Python dependencies
├── cron_schedule.json       # Active scheduled background tasks
├── jarvis_memory.json       # High-priority rules and facts for JARVIS
├── .env                     # Email credentials (not tracked in git)
├── assets/                  # Icons and UI images
│   ├── ironman_bg.jpg
│   └── jarvis_logo.ico
├── core/                    # The Brain & Logic
│   ├── __init__.py
│   ├── jarvis_brain.py      # ReAct engine, tool registry, LLM interface
│   ├── jarvis_memory.py     # ChromaDB RAG memory system
│   └── user_profile.json    # User personalization data
├── ui/                      # User Interfaces
│   ├── __init__.py
│   ├── jarvis_cli.py        # Terminal interface
│   └── jarvis_interface.py  # PyQt6 GUI with Arc Reactor HUD
├── features/                # Additional Capabilities
│   ├── __init__.py
│   ├── jarvis_voice.py      # TTS (Edge-TTS) & STT (microphone)
│   ├── jarvis_cron.py       # Background task scheduler
│   └── jarvis_visualizer.py # Real-time audio spectrum visualizer
├── Data/                    # Application registry
│   ├── data.json            # App names → Windows AppIDs/exe paths
│   ├── app_names.json       # Normalized app name catalog
│   └── reference.txt        # Raw installed apps reference
├── user_data/               # Personal schedule & task files
│   ├── HEARTBEAT.md         # Daily briefing checklist
│   ├── LECTURES.md          # Academic lecture schedule
│   └── SCHOOL_CALENDAR.md   # Exam and event calendar
└── db_memory/               # ChromaDB persistent vector store
```


## 📦 Installation

Since Jarvis runs entirely locally, you **do not** need external API keys (except a standard Google App Password for IMAP email features).

### 1. Prerequisites (Crucial)
You must have **Ollama** installed on your system to run the AI model locally.

1. Download and install [Ollama](https://ollama.com/).

2. Open your terminal/CMD and pull the required models:

```bash
ollama pull gemma4:e4b
ollama pull qwen2.5:0.5b
```

*(Keep Ollama running in the background.)*

### 2. Run the Installer
Download `Jarvis_Setup.exe` from the [Releases](https://github.com/ofri09bs/JARVIS-AI-Assistant/releases) tab and run it.

The installer will automatically:
- Download and set up a **portable Python 3.11** environment (does not touch your system Python)
- Pull the latest JARVIS source code from GitHub
- Install all dependencies
- Detect Ollama and offer to install it if missing
- Pull the required AI models
- Create a **Desktop Shortcut** and launcher scripts

The installation takes about **2 to 5 minutes** depending on your internet speed.

### 3. Configure .env File (Optional — for Email Features)
Create an `.env` file in the installation directory with your Gmail credentials:

```
EMAIL_ADDRESS=YOUR_EMAIL_ADDRESS
APP_PASSWORD=YOUR_APP_PASSWORD
```

*[How to get a Google App Password](https://support.google.com/accounts/answer/185833?hl=en)*

## ▶️ Usage
Run the **Jarvis Assistant** desktop shortcut, or execute `main.py`.

You will be greeted by the Main System Menu:

1. **Command Line Interface (CLI):** Best for fast, text-based tasks, coding help, and raw speed.

2. **Graphical User Interface (GUI):** Best for voice interaction, screen stats, and audio visualization.

*(Note: The Cron Background Thread automatically starts upon launching the main menu.)*

### Example Commands

| Command | What Happens |
|---------|-------------|
| `"Open VS Code and Chrome"` | Launches both applications |
| `"Read my last 5 emails"` | Connects to Gmail, fetches & summarizes emails |
| `"Fix this code"` | Reads clipboard, fixes code via LLM, copies result back |
| `"Analyze my screen"` | Screenshots display, sends to vision model for analysis |
| `"Set volume to 30"` | Adjusts system volume |
| `"Schedule a reminder to check emails every hour"` | Creates a recurring cron task |
| `"What did we talk about yesterday?"` | Searches RAG memory for past conversations |

## ⚠️ Security Notice
This AI has access to shell commands (subprocess). While a strict whitelist/blacklist is implemented to prevent accidental damage (`rm`, `format`, `del`, `shutdown`, etc.), always use caution when allowing an AI agent to execute commands on your operating system.