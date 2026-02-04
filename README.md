# J.A.R.V.I.S - AI Assistant

**Just A Rather Very Intelligent System**

An advanced, Iron Man-inspired desktop AI agent built with Python.

**jarvis 3.0 is not just a chatbot.** It creates its own code in real-time. It features a sophisticated **Agentic Workflow** that classifies intent, plans **complex multi-step** tasks using JSON, and safely executes them on your PC.

Jarvis can execute almost **every complex task you will give him**, such as: `Jarvis, I want to code. Open VS Code, create a new python file called 'test.py', and write a Hello World loop inside it. also set the volume to 30% and open youtube for me and search there "Avengers Doomsday leaks" please `. (Jarvis will open VS code , creat a new file , paste there the code , open youtube and searchs there , and also sets the computers volume to 30%. And all of this without ONE precodded command!)

<img width="1913" height="976" alt="image" src="https://github.com/user-attachments/assets/6ddb14de-41ee-497c-b41f-6be9aafb6e20" />

## 🚀 Key Features

### GUI Features
- Shows the **current time**
- Shows the **CPU load** In percentages
- Shows the **RAM usage** In percentages
- Shows how much **space is free** on the disk (in GB)
- Shows the current **Local weather** temperature

### 🖥️ Desktop Automation & Focus Management
* **Tactical Typing:** Solves the "focus stealing" issue by minimizing the UI, waiting for the active window, and using **Tactical Paste** (Clipboard Injection) instead of slow keystrokes.
* **Smart App Launcher:** A 3-layer launch system: `Custom Aliases` -> `System Commands` -> `AppOpener` (Fuzzy Search). It knows that "VS Code" means `code` and "Chrome" means `chrome.exe`.
* **Volume Control:** Native integration via `pycaw` for precise audio management.
* **Screen Analysis:** Can Screenshot and analyze your screen with **Groq Meta-Llama 4 image recognition**

### 🛡️ Security Sandbox
* **Command Filtering:** Access to the terminal (`cmd`) is protected by a **Blacklist** to prevent dangerous commands (like deletion or formatting).
* **Scoped Tools:** The AI can only access specific registered functions, preventing hallucinations from executing arbitrary code.

### 🗣️ Natural Interaction
* **Neural Voice:** Uses **Edge-TTS** for high-quality, low-latency British/American speech.
* **Glass-morphism GUI:** A futuristic PyQt6 interface with real-time feedback and logs.


## 🧠 Core Architecture (The Brain)

Unlike standard assistants that use hardcoded `if/else` logic, JARVIS uses a dynamic **Router-Planner-Executor** model:

1.  **⚡ Fast Router:** A static analysis engine quickly handles common commands (0.1s latency) and only delegates complex reasoning to the LLM when necessary.
2.  **📝 JSON Planner:** Powered by **Google Gemma**, it breaks down abstract goals (e.g., *"Set up a coding environment"*) into a list of atomic **Primitive Actions**.
3.  **🛠️ Safe Executor:** A Python engine that parses the plan and executes tools from a strict Registry.
4.  **Executor:** A Python engine parses the JSON and performs the actions using system libraries.

## Core Workflow:

Getting **speech/text** input → Checking for **Hardcoded commands** → deciding if you want to **CHAT** or to **PLAN** a series of tasks 

 - If **CHAT**: Sends the input to Gemma
 - If **PLAN**: Creats a json formated list of primitive actions , parses them and executes them (if possible)


## 🛠️ Tech Stack

* **Core:** Python 3.14
* **AI Model:** Google Generative AI (`google-generativeai`)
* **GUI:** PyQt6 (Modern Glass-morphism UI)
* **Automation:** `AppOpener`, `pycaw`, `pyperclip`, `webbrowser`, `subprocess`
* **Audio:** `sounddevice`, `numpy` (VAD), `edge-tts`

## 📂 Project Structure

```text
📁 JARVIS-SYSTEM
│
├── jarvis_interface.py     # Entry point. Handles GUI, Threading, and logic integration.
├── jarvis_brain.py         # AI Logic. Handles API connection and command routing.
├── jarvis_voice.py         # Hearing & Speaking. VAD logic, TTS generation, and cleanup.
├── jarvis_visualizer.py    # FFT Logic. Custom QWidget for the audio spectrum.
├── installer.py            # The Automated Setup Wizard.
│
├── assets/                 # Folder containing icons and background images
│   ├── ironman_bg.jpg      
│   └── jarvis_logo.ico
│
└── README.md               # Documentation
```

## 📦 Installation
You **do not** need to install Python or libraries manually. The installer handles everything. (I worked very hard for you :)

**1. Get the API Keys**

You need a free **Google Gemini** API Key and a **Groq** API KEY

[Get Google AI Key Here](aistudio.google.com)
[Get Groq AI Key Here](console.groq.com/keys)

**2. Run the installer**

Download the exe file `JarvisInstaller.exe` and run it 
The installation could take from **5 to 10 minutes** 



**3. Follow the wizard**

1. The installer will ask for an Installation Folder.

2. It will ask you to paste your API Keys.

3. Click Install.

The installer will automatically:

✅ Download a dedicated Python environment (isolated from your system).

✅ Clone the latest code from GitHub.

✅ Install all required dependencies (sounddevice, numpy, etc.).

✅ Create a Desktop Shortcut.


## ▶️ Usage
Run the main application:

**To Speak**: Click the Microphone Icon (bottom right). It will turn Cyan.

**To Stop:** Click the Microphone Icon again.

**Typing:** You can always type commands in the text box and press Enter.


## ⚠️ Security Notice
This AI has access to shell commands (subprocess). While a blacklist is implemented to prevent accidental damage (rm, format, etc.), always use caution when giving "Administrator" privileges to an AI agent.
