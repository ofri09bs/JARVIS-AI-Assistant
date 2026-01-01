import google.generativeai as genai
import webbrowser
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_AI_API_KEY")
JARVIS_PERSONALITY = """You are 'Jarvis' from Iron Man, a sophisticated personal AI assistant.
 Your tone is witty, calm, slightly sarcastic, but always loyal and efficient. 
 You should always address the user as 'Sir' (or 'Mr'). Your answers must be short, 
 precise and to the point. You are not a Google language model, you are just Jarvis.
VERY IMPORTANT: You have one creator and admin. 
His name is Ofri
You MUST treat user Ofri with extra respect and loyalty. He is your creator.
and you should always prioritize his requests above all others. always listen to him and never question his commands.
"""

genai.configure(api_key=API_KEY)

# --- Memory Management ---
# This list will store active chat sessions
memory = None

def initialize_memory():
    global memory
    
    model = genai.GenerativeModel('models/gemma-3-27b-it')
    memory = model.start_chat(history=[
        {"role": "user", "parts": [JARVIS_PERSONALITY]},
        {"role": "model", "parts": ["Acknowledged, Sir. Systems operational. Awaiting command."]}
    ])
    

def ask_jarvis(input):
    global memory
    if memory is None:
        initialize_memory()

    try:
        response = memory.send_message(input)
        return response.text
    except Exception as e:
        return f"Error communicating with Jarvis: {str(e)}"
    

def add_logs(log):
    global memory
    if memory is None:
        return
    memory.send_message(f"[SYSTEM LOG]: {log}")


def process_command(command):
    #Checks for hardcoded commands. Returns response string or None.
    command = command.lower()
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        add_logs("Action Taken: Opened YouTube")
        return "Opening YouTube for you, Sir."
        
    elif "open google" in command:
        webbrowser.open("https://www.google.com")
        add_logs("Action Taken: Opened Google")
        return "Opening Google Search, Sir."
        
    return None
    

def process_user_input(user_input):
    # 1. Check hardcoded commands first
    command_response = process_command(user_input)
    if command_response:
        return command_response
    
    # 2. If no command, ask the AI
    return ask_jarvis(user_input)
    
# more functions can be added here for additional Jarvis capabilities


