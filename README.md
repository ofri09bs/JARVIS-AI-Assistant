# J.A.R.V.I.S - AI Assistant

**Just A Rather Very Intelligent System**

A fully functional, Iron Man-inspired desktop AI assistant built with Python. This project combines a futuristic **PyQt6 GUI**, real-time **Audio Visualization**, and **Generative AI** (Google Gemini) to create an immersive voice assistant experience.
This project was made with **Vibe-Coding** for fun!
<img width="1913" height="976" alt="image" src="https://github.com/user-attachments/assets/6ddb14de-41ee-497c-b41f-6be9aafb6e20" />


## 🚀 Features

* **🧠 Advanced AI Brain:** Powered by **Google Gemma (gemma-3-27b)** for natural, context-aware conversations.
* **🗣️ Neural Voice:** Uses **Edge-TTS** to provide a high-quality, near-human voice (Microsoft Christopher Neural) with low latency.
* **👂 Smart Listening (VAD):** Custom Voice Activity Detection engine using `sounddevice` and `numpy`. It detects when you speak and stops automatically when you finish—no fixed timers.
* **📊 Real-Time Visualizer:** A dual-mirrored FFT audio spectrum that reacts instantly to voice and system sounds.
* **🖥️ Sci-Fi GUI:** A custom **PyQt6** interface featuring:
    * Arc Reactor animation.
    * Live System stats (CPU, RAM, Disk).
    * Glass-morphism design elements.
* **⚙️ Automation:** Built-in command routing for PC control (YouTube, Google, System Lock, etc.).

## 🛠️ Tech Stack

* **Language:** Python 3.14 (Compatible with 3.10+)
* **GUI:** PyQt6
* **Audio Processing:** SoundDevice, NumPy, SciPy
* **Speech Recognition:** Google Speech Recognition API
* **Text-to-Speech:** Edge-TTS (Cloud-based Neural Voices), Pygame (Playback)
* **AI Model:** Google Generative AI (`google-generativeai`)

## 📂 Project Structure

```text
📁 JARVIS-SYSTEM
│
├── main.py                 # Entry point. Handles GUI, Threading, and logic integration.
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
pip install PyQt6 sounddevice numpy scipy speechrecognition edge-tts pygame google-generativeai psutil glob2
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
