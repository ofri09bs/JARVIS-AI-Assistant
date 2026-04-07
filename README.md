# J.A.R.V.I.S - AI Desktop Assistant

**Just A Rather Very Intelligent System**

An advanced, Iron Man-inspired desktop AI agent built with Python.

**jarvis 5.0 is not just a chatbot.** It creates its own code in real-time. It features a sophisticated **Agentic Workflow** that classifies intent, plans **complex multi-step** tasks using JSON, and safely executes them on your PC.

Jarvis can execute almost **every complex task you will give him**, such as: `Jarvis, I want to code. Open VS Code, create a new python file called 'test.py', and write a Hello World loop inside it. also set the volume to 30% and open youtube for me and search there "Avengers Doomsday leaks" please `. (Jarvis will open VS code , creat a new file , paste there the code , open youtube and searchs there , and also sets the computers volume to 30%. And all of this without ONE precodded command!)

<img width="1913" height="976" alt="image" src="https://github.com/user-attachments/assets/6ddb14de-41ee-497c-b41f-6be9aafb6e20" />

## 🚀 Key Features

### Dual Interfaces
- **GUI Mode:** A futuristic Glass-morphism interface showing real-time stats (CPU, RAM, Disk Space, Weather) and audio visualization.
- **CLI Mode:** A fast, clean terminal interface with ANSI color coding and execution timers.
*Idea for the future: Integration with Discord*

### Desktop Automation
* **Tactical Typing:** Solves the "focus stealing" issue by minimizing the UI, waiting for the active window, and using **Tactical Paste** (Clipboard Injection) instead of slow keystrokes.
* **Smart App Launcher:** A 3-layer launch system: `Custom Aliases` -> `System Commands` -> `AppOpener` (Fuzzy Search). It knows that "VS Code" means `code` and "Chrome" means `chrome.exe`.
* **Local Screen Analysis:** Can capture your screen and analyze visual data entirely locally using Ollama vision capabilities.

### Natural Interaction
* **Neural Voice:** Uses **Edge-TTS** for high-quality British/American speech.
* **Time Awareness:** Jarvis dynamically knows the current system time, allowing him to schedule tasks, manage exam deadlines, and understand temporal context.

##  Core Architecture (The Brain)

Unlike standard assistants, JARVIS uses a dynamic **Router-Planner-Executor** model running on your local GPU/CPU:

1.  **⚡ Fast Router:** A static engine handles common hardcoded commands instantly and delegates complex reasoning to the LLM.
2.  **📝 JSON Planner:** Powered by **Local Ollama Models (Gemma)**. It breaks down abstract goals into a list of **Primitive Actions**.
3.  **🛠️ Safe Executor:** A Python engine that parses the JSON plan and safely triggers tools from a strict internal Registry.

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
    └── jarvis_visualizer.py
```


## 📦 Installation
Since Jarvis runs entirely locally, you **do not** need any API keys.

### 1. Prerequisites (Crucial)
You must have **Ollama** installed on your system to run the AI model locally.

1. Download and install [[Ollama](https://ollama.com/)].

2. Open your terminal/CMD and run:

`ollama run gemma4:e4b`

*(Keep Ollama running in the background).*

### 2. Run the Installer
Download the executable `Jarvis_Setup.exe` from the Releases tab and run it.
The installation takes about **2 to 5 minutes**.

### 3. Follow the Wizard
1. Select an installation folder.

2. Click Install. The installer will automatically download a portable Python environment, pull the latest code, install all dependencies without touching your system's Python, and create a Desktop Shortcut.


## ▶️ Usage
Run the **Jarvis Assistant** desktop shortcut, or execute `main.py`.

You will be greeted by the Main System Initialization menu:

1. **Command Line Interface (CLI)**: Best for fast, text-based tasks, coding help, and raw speed.

2. **Graphical User Interface (GUI)**: Best for voice interaction, screen stats, and audio visualization.

In **GUI Mode**:

- **To Speak**: Click the Microphone Icon (it will turn Cyan).

- **To Stop**: Click the Microphone Icon again.

- **Typing**: You can always type commands in the text box and press Enter.


## ⚠️ Security Notice
This AI has access to shell commands (subprocess). While a strict blacklist is implemented to prevent accidental damage (rm, format, etc.), always use caution when allowing an AI agent to execute commands on your operating system.