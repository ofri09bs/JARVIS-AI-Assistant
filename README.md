# J.A.R.V.I.S - AI Assistant

**Just A Rather Very Intelligent System**

An advanced, Iron Man-inspired desktop AI assistant built with Python.
Unlike standard voice assistants, **features an Agentic Workflow**: it doesn't just chat; it intelligently classifies your intent, plans a series of actions in JSON, and executes them on your PC in real-time.
<img width="1913" height="976" alt="image" src="https://github.com/user-attachments/assets/6ddb14de-41ee-497c-b41f-6be9aafb6e20" />

## 🚀 Features & Commands

### 🤖 Smart commands (you dont need to say this exact words, the AI will understand it)
**For this commands , you can say a few together and they will all be executed**

**For example:** Jarvis, open the website youtube , set volume to 30% and also close steam

 - **Open App <app_name>** : Can open (almost) any App you tell it using `AppOpener`
 - **Close App <app_name>**: Terminates the .exe file of the application
 - **Open File <path>**: Opens the given file
 - **Set Volume <level>**: Sets the computers volume to be {level}%
 - **Lock System**: Locking the computer
 - **Open Website <url_name>**: Opens the given website , you dont need to say to full website , just the name (like open website google)

### 🛠️ Hardcoded commands (Need to be in the exact order)
 - **Open Website <url>**: Opens the given url , adds http:// and .com if there isnt.
 - **Open <app_name>**:  Can open (almost) any App you tell it using `AppOpener`
 - **Lock computer**: Locking the computer
 - **Fix this code**: Extracting the clipboard content, telling the AI to fix it, then coping it back to the clipboard
 - **work mode**: Opens VSCode and Gemini
 - **Matrix Protocol**: Opens a CMD window in green and writing every file in root (seems like hacking)

## 🧠 Core Architecture (The Brain)

This project uses a **Router-Planner-Executor** model powered by **Google Gemma**:

1.  **Intent Classification:** The AI analyzes your voice command to decide if it's a **CHAT** (casual conversation) or a **PLAN** (task execution).
2.  **JSON Planner:** If a task is detected, it generates a structured JSON plan breaking down the goal into steps (e.g., "Open Spotify", "Set Volume to 50%", "Lock Screen") in the next format:
   ```
{
   "goal": string,
   "steps": [
     {
       "action": string,
        ....
       "params": object
     }
    ]
 }
```
4.  **Executor:** A Python engine parses the JSON and performs the actions using system libraries.

## Core Workflow:

Getting **speech/text** input → Checking for **Hardcoded commands** → deciding if you want to **CHAT** or to **PLAN** a series of tasks 

 - If **CHAT**: Sends the input to Gemma
 - If **PLAN**: Creats a json formated list of tasks , parses them and executes them (if possible)


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
├── jarvis_interface.py                 # Entry point. Handles GUI, Threading, and logic integration.
├── jarvis_brain.py         # AI Logic. Handles API connection and command routing.
├── jarvis_voice.py         # Hearing & Speaking. VAD logic, TTS generation, and cleanup.
├── jarvis_visualizer.py    # FFT Logic. Custom QWidget for the audio spectrum.
│
├── ironman_bg.jpg          # Background image (Required)
├── .env                    # API Keys (Recommended)
└── README.md               # Documentation
```

## 📦 Installation
**1. Clone the Repository**

```
git clone [https://github.com/ofri09bs/JARVIS-AI-Assistent.git](https://github.com/ofri09bs/JARVIS-AI-Assistent.git)
cd JARVIS-AI-Assistent
```

**2. Install Dependencies**

This project avoids pyaudio due to compatibility issues on newer Python versions. It uses sounddevice instead.
```
pip install -r requirements.txt
```

**3. Setup API Key**

You need a free Google Gemini API Key.
Get your key from Google AI Studio.
make an .env file and write there:
```API_KEY = "YOUR_PASTED_API_KEY_HERE"```

**4. Background Image**

Place an image named ironman_bg.jpg in the project root folder for the UI to load correctly.

## ▶️ Usage
Run the main application:

**To Speak**: Click the Microphone Icon (bottom right). It will turn Cyan.

**To Stop:** Click the Microphone Icon again.

**Typing:** You can always type commands in the text box and press Enter. (More commands comming soon!)

## 🔧 Troubleshooting
Microphone not picking up audio? Open jarvis_voice.py and lower the SILENCE_THRESHOLD (e.g., from 3 to 1.5).

Assistant won't stop listening? Increase the SILENCE_THRESHOLD (e.g., to 10 or 15) if you have background noise.

"Permission Denied" on MP3 files? The system automatically handles unique filenames (tts_{timestamp}.mp3) and cleans up old files to prevent locking issues.
