import sounddevice as sd
import speech_recognition as sr
import scipy.io.wavfile as wav
import numpy as np
import os
import asyncio
import edge_tts
import pygame
import time
import glob # Library for finding files

# Hide startup messages
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# --- CONFIGURATION ---
VOICE = "en-US-ChristopherNeural" 
RATE = "+25%" 
# Change: No longer using a fixed filename, generating dynamically
INPUT_FILE = "temp_voice.wav"
SAMPLE_RATE = 44100

# Sensitivity settings (works well at 3 according to your log)
SILENCE_THRESHOLD = 3    
SILENCE_LIMIT = 2.0      

pygame.mixer.init()

def cleanup_old_files():
    """Deletes old MP3 files to prevent accumulation"""
    try:
        files = glob.glob("tts_*.mp3")
        for f in files:
            try:
                os.remove(f)
            except:
                pass # If the file is still in use, skip it
    except:
        pass

async def generate_speech(text, filename):
    """Generates MP3 with unique filename"""
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(filename)

def speak(text):
    """
    Main speak function with File Locking Fix.
    """
    try:
        # 1. stop current playback if any
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        
        # 2. Cleanup old files
        cleanup_old_files()

        # 3. Create unique filename (prevents Permission denied)
        unique_filename = f"tts_{int(time.time())}.mp3"

        # 4. Generate audio
        asyncio.run(generate_speech(text, unique_filename))
        
        # 5. play audio
        pygame.mixer.music.load(unique_filename)
        pygame.mixer.music.play()
        
        # Log output
        print(f"[JARVIS SPEAKING]: {text}")
            
    except Exception as e:
        print(f"TTS Error: {e}")

def listen_dynamic():
    print(f"Listening (Threshold: {SILENCE_THRESHOLD})...")
    
    audio_buffer = []
    chunk_duration = 0.1 
    chunk_samples = int(SAMPLE_RATE * chunk_duration)
    
    silence_start = None
    has_started_speaking = False
    
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
            while True:
                data, overflowed = stream.read(chunk_samples)
                audio_data = data[:, 0]
                
                rms = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
                volume = rms / 100 

                if volume > SILENCE_THRESHOLD:
                    if not has_started_speaking:
                        print("\nVoice Detected! Recording...")
                        has_started_speaking = True
                    
                    silence_start = None 
                    audio_buffer.append(data)
                
                else:
                    # שקט
                    if has_started_speaking:
                        audio_buffer.append(data) 
                        
                        if silence_start is None:
                            silence_start = time.time()
                        
                        if time.time() - silence_start > SILENCE_LIMIT:
                            print("\nProcessing speech...")
                            break
                    else:
                        pass

        if len(audio_buffer) > 0:
            full_recording = np.concatenate(audio_buffer, axis=0)
            
            if len(full_recording) < SAMPLE_RATE * 0.5:
                print("Audio too short, ignoring.")
                return None

            wav.write(INPUT_FILE, SAMPLE_RATE, full_recording)
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(INPUT_FILE) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language="en-US")
                    print(f"[HEARD]: {text}")
                    return text
                except sr.UnknownValueError:
                    print("...")
                    return None
                except sr.RequestError:
                    print("Offline / Connection Error")
                    return None
        return None

    except Exception as e:
        print(f"Mic Error: {e}")
        return None