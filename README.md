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
* **Cron Task:** It can schedule recurring tasks (cron) and alert and check them at regular times.

### Dual Interfaces
- **GUI Mode:** A futuristic Glass-morphism interface showing real-time stats (CPU, RAM, Disk Space, Weather) and audio visualization.
- **CLI Mode:** A fast, clean terminal interface with ANSI color coding and execution timers.
*Idea for the future: Integration with Discord*

### Desktop Automation
* **Smart App Launcher:** A 3-layer launch system: `Custom Aliases` -> `System Commands` -> `AppOpener` (Fuzzy Search). It knows that "VS Code" means `code` and "Chrome" means `chrome.exe`.
* **Local Screen Analysis:** Can capture your screen and analyze visual data entirely locally using Ollama vision capabilities.

### Natural Interaction
* **Neural Voice:** Uses **Edge-TTS** for high-quality British/American speech.
* **Time Awareness:** Jarvis dynamically knows the current system time, allowing him to schedule tasks, manage exam deadlines, and understand temporal context.

## ⚙️ Core Architecture (The Brain)

JARVIS operates on a dynamic **Router-Planner-Executor** model:

1.  **The ReAct Loop (`jarvis_brain.py`):** The core engine. It feeds the user's prompt to the local LLM, receives a JSON tool call, executes the tool, and appends the `TOOL RESULT` back to the LLM's memory until the LLM explicitly calls the `DONE` action.
2.  **The Background Listener (`jarvis_cron.py`):** A daemon thread that monitors `cron_schedule.json`. When a task is due, it wakes up the ReAct loop invisibly in the background.
3.  **The Tool Router:** Safely maps LLM intents to Python functions, handling alias corrections to prevent execution failures.

## 🛠️ Tech Stack

* **Core:** Python 3.11 (Portable Environment)
* **AI Model:** `ollama` (Local Execution, Default: `gemma4:e4b`)
* **GUI:** PyQt6
* **Automation:** `AppOpener`, `pyperclip`, `pyautogui`, `subprocess`, `webbrowser`
* **Audio:** `sounddevice`, `numpy`, `edge-tts`

## 📂 Project Structure

```text
JARVIS-AI-Assistant/
├── main.py                  # Entry point. Unified launcher for CLI & GUI.
├── installer.py             # The Automated Setup Wizard source code.
├── test_jarvis.py           # System diagnostics and automated health checks.
├── requirements.txt         # Dependencies
├── assets/                  # Icons and UI images
│   ├── ironman_bg.jpg      
│   └── jarvis_logo.ico
├── core/                    # The Brain & Logic
│   ├── __init__.py
│   └── jarvis_brain.py
├── ui/                      # User Interfaces
│   ├── __init__.py
│   ├── jarvis_cli.py
│   └── jarvis_interface.py
└── features/                # Additional Capabilities
    ├── __init__.py
    ├── jarvis_voice.py
    ├── jarvis_cron.py
    └── jarvis_visualizer.py
```


## 📦 Installation
Since Jarvis runs entirely locally, you **do not** need external API keys (except a standard Google App Password for IMAP features).

### 1. Prerequisites (Crucial)
You must have **Ollama** installed on your system to run the AI model locally.

1. Download and install [Ollama](https://ollama.com/).

2. Open your terminal/CMD and run:

`ollama run gemma4:e4b`

*(Keep Ollama running in the background).*

### 2. Run the Installer
Download the executable `Jarvis_Setup.exe` from the Releases tab and run it.
The installation takes about **2 to 5 minutes**.

### 3. Follow the Wizard
1. Select an installation folder.

2. Click Install. The installer will automatically download a portable Python environment, pull the latest code, install all dependencies without touching your system's Python, and create a Desktop Shortcut.

### 4. Configure .env file
Create an `.env` file and write there the following credentials:

`EMAIL_ADDRESS=YOUR_EMAIL_ADDRESS`

`APP_PASSWORD=YOUR_APP_PASSWORD`

*[Get your app password here](https://support.google.com/accounts/answer/185833?hl=en)*

## ▶️ Usage
Run the **Jarvis Assistant** desktop shortcut, or execute `main.py`.

You will be greeted by the Main System Menu:

1. **Command Line Interface (CLI):** Best for fast, text-based tasks, coding help, and raw speed.

2. **Graphical User Interface (GUI):** Best for voice interaction, screen stats, and audio visualization.

*(Note: The Cron Background Thread automatically starts upon launching the main menu).*


## ⚠️ Security Notice
This AI has access to shell commands (subprocess). While a strict blacklist is implemented to prevent accidental damage (rm, format, etc.), always use caution when allowing an AI agent to execute commands on your operating system.