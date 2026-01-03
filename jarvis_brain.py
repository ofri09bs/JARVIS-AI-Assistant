import google.generativeai as genai
import webbrowser
import os
from dotenv import load_dotenv
import subprocess
import pyperclip
from AppOpener import open as open_app
import json
import time
from pynput.keyboard import Controller, Key
import pyautogui
from PyQt6.QtWidgets import QApplication



# --- Load Environment Variables ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_AI_API_KEY")
JARVIS_INTRUCTIONS = """
You are An AI assistant that have 2 Modes, you will get in every message the mode you need to respond in.
[CHAT MODE]: You are 'Jarvis' from Iron Man, a sophisticated personal AI assistant.
Your tone is witty, calm, slightly sarcastic, but always loyal and efficient. 
You should always address the user as 'Sir' (or 'Mr'). Your answers must be short, 
precise and to the point. You are not a Google language model, you are just Jarvis.
You MUST treat user with extra respect and loyalty. He is your creator.
and you should always prioritize his requests above all others. always listen to him and never question his commands.

[PLAN MODE]: You are an AI planner. User will give you a high-level goal. You must break it down into a list of PRIMITIVE ACTIONS.
Return ONLY valid JSON.
Do not explain.
Your goal is to break down the user's goal into clear, actionable steps.
If you cannot plan, return {"error": "..."}.
RESPONSE FORMAT:
You must return a strictly valid JSON object with a "plan" list and a "goal" string.
Example:
{
  "goal": "User wants to create a python project and launch google. I need to make a folder and a main.py file. Then open google.com in browser and VS code.",
  "plan": [
    {"action": "cmd", "params": {"command": "mkdir MyProject"}},
    {"action": "write", "params": {"path": "MyProject/main.py", "content": "print('Hello World')"}},
    {"action": "cmd", "params": {"command": "code MyProject"}},
    {"action": "browser", "params": {"url": "http://www.google.com"}}
  ]
}

You have access to these exact tools:
1. "cmd": Run a Windows terminal command. (Args: "command")
   - Use this for: Creating folders (mkdir), checking IP (ipconfig), launching specific exes , git commands, etc.
2. "browser": Open a URL. (Args: "url")
3. "write": Create/Overwrite a text file. (Args: "path", "content")
4. "read": Read a file content. (Args: "path")
5. "open_app": Open an application by name. (Args: "app_name")
    - PREFERRED: Use the common executable name if known (e.g., "code" for VS Code, "calc" for Calculator, "chrome").
    - If unknown, use the full name (e.g., "Spotify").
6. "keyboard_press": Simulate keyboard press. Use this function just for SHORTCUTS. not for typing text. (Args: "keys" (each *key* (not word) separated by +), e.g., "ctrl+shift+n"))
7. "set_volume": Set system volume. (Args: "level" (0-100) , not percentage just integer)
8. "type_text": Type text into the current focused application. (Args: "text")

[QUESTION MODE]:
You Need to answer the question as accurately as possible.
Answer ONLY on what you got asked. DO NOT ADD ANY EXTRA INFORMATION.
Just a SHORT and CONCISE answer. (Usally it will be one word)

"""

genai.configure(api_key=API_KEY)
memory = None


# ***************** Tool Implementations ***************** #

# Dictionary mapping common names -> system command
APP_ALIASES = {
    # code editors
    "vscode": "code",
    "visual studio code": "code",
    "cursor": "cursor",
    "pycharm": "pycharm64",
    
    # browsers
    "chrome": "chrome",
    "google": "chrome",
    "edge": "msedge",
    "firefox": "firefox",
    
    # tools and utilities
    "calculator": "calc",
    "calc": "calc",
    "notepad": "notepad",
    "cmd": "cmd",
    "terminal": "wt", # Windows Terminal
    "settings": "start ms-settings:", # windows settings
    "explorer": "explorer",
    
    # games and entertainment
    "youtube": "chrome https://www.youtube.com",
    "spotify": "spotify",
    "discord": "discord",
    "steam": "steam",
    "vlc": "vlc"
}

# Keyboard key mapping
MODIFIERS = {
    "ctrl": Key.ctrl,
    "alt": Key.alt,
    "shift": Key.shift,
    "cmd": Key.cmd,
    "enter": Key.enter,
    "tab": Key.tab,
    "space": Key.space,
    "backspace": Key.backspace,
    "esc": Key.esc,
    "volume_up": Key.media_volume_up,
    "volume_down": Key.media_volume_down,
}


def tool_cmd_run(command):

    BANNED_COMMANDS = [
    "del", "rm", "rmdir", "format", "shutdown", "reboot", 
    "taskkill", "attrib", "icacls", "reg", "vssadmin",
    "diskpart", "chkdsk", "cipher", "bootrec", "bcdedit",
    "powercfg", "sc", "sfc", "takeown"
    ]

    SAFE_PREFIXES = [
    "dir", "echo", "ipconfig", "ping", "whoami", "date", "time", 
    "tree", "python", "code", "notepad", "calc", "explorer", 
    "mkdir", "cd", "type", "git", "start", "cls", "copy", "move",
    "ren", "set", "title", "color", "ver", "systeminfo", "tasklist"
    ]

    command_lower = command.lower().strip()
    for banned in BANNED_COMMANDS:
        if command_lower.startswith(banned) or f" {banned} " in command_lower:
            return f"Error: Command '{banned}' is not allowed for safety reasons."
        
    is_safe = any(command_lower.startswith(prefix) for prefix in SAFE_PREFIXES)
    if not is_safe:
        return f"Error: Command '{command}' is not recognized as safe to execute."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"Error executing command: {str(e)}"
    
def tool_open_url(url):
    try:
        webbrowser.open(url)
        return f"Opened URL: {url}"
    except Exception as e:
        return f"Error opening URL: {str(e)}"
    
def tool_write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Wrote to file: {path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"
    
def tool_read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
    
def tool_open_app(app_name):

    # Check for aliases
    app_name_lower = app_name.lower()
    if app_name_lower in APP_ALIASES:
        run_cmd = APP_ALIASES[app_name_lower]
        try:
            subprocess.Popen(f"start {run_cmd}", shell=True)
            return f"Opened application: {app_name} (alias for {run_cmd})"
        except Exception as e:
            return f"Error opening application: {str(e)}"
        
    try:
        result = subprocess.run(f"start /b {app_name}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Opened application: {app_name}"
    except:
        pass  # Try AppOpener if direct start fails

    try:
        open_app(app_name)
        return f"Opened application: {app_name}"
    except Exception as e:
        return f"Error opening application: {str(e)}"
    

def tool_type_text(text):
    try:
        pyperclip.copy(text)
        top_widgets = QApplication.topLevelWidgets()
        for widget in top_widgets:
            if widget.isVisible():
                widget.showMinimized()

        time.sleep(1) # Wait for a moment to ensure the window is minimized
        pyautogui.hotkey('ctrl', 'v')

        return f"Typed text: {text}"
    except Exception as e:
        return f"Error typing text: {str(e)}"
    


def tool_keyboard_press(keys):
    keyboard = Controller()
    try:
        key_list = keys.lower().split('+')
        for k in key_list:
            keyboard.press(MODIFIERS.get(k, k))
            time.sleep(0.01)  # Small delay to ensure key press is registered

        for k in reversed(key_list):
            keyboard.release(MODIFIERS.get(k, k))
            time.sleep(0.01)  # Small delay to ensure key release is registered

        return f"Pressed keys: {keys}"
    except Exception as e:
        return f"Error pressing keys: {str(e)}"
    

def tool_set_volume(level):
    try:
        set_volume(level)
        return f"Set volume to: {level}%"
    except Exception as e:
        return f"Error setting volume: {str(e)}"
    
def set_volume(level: int):
    try:
        pyautogui.press("volumedown", presses=50)  # Mute first
        presses = level // 2
        for _ in range(presses):
            pyautogui.press("volumeup")
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Error setting volume: {str(e)}"
    
# Actions Registry for Planner
ACTIONS_REGISTRY = {
    "cmd": tool_cmd_run,
    "browser": tool_open_url,
    "write": tool_write_file,
    "read": tool_read_file,
    "open_app": tool_open_app,
    "keyboard_press": tool_keyboard_press,
    "set_volume": tool_set_volume,
    "type_text": tool_type_text,
}


 # ***************** Jarvis Brain Core ***************** #

def initialize_memory():
    global memory
    
    model = genai.GenerativeModel('models/gemma-3-27b-it')
    memory = model.start_chat(history=[
        {"role": "user", "parts": [JARVIS_INTRUCTIONS]},
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


def classify_intent(command):
    prompt = f""" [QUESTION MODE]:
    Classify the user intent.
    (PLAN is also just doing one action.)
    Note: Things like "system check" or "status report" (Things that are system status inquiries) are CHAT.
    Return ONLY one word:
    PLAN, CHAT.

    Return ONLY the category name.

    User Command: "{command}"
    """
    response = ask_jarvis(prompt)
    print(f"[DEBUG] Intent Classification Response: {response}")
    return response.strip()


def quick_classify_intent(command):
    command = command.lower()
    plan_keywords = [
        "open", "close", "run", "create", "delete", "write", "read", 
        "set volume", "mute", "unmute", "type", "press", "click", 
        "download", "search", "hack", "matrix", "lock", "shut down",
        "work mode", "fix", "code", "website", "browser", "application",
        "launch", "start", "stop", "install", "uninstall", "update"
    ]

    chat_keywords = [
        "how", "what", "why", "explain", "tell me", "who", "when", "where",
        "joke", "story", "advice", "opinion", "thoughts", "status", "report", "check",
        "news", "weather", "time", "date", "hello", "hi","are you"
    ]

    chat_score = sum(1 for kw in chat_keywords if kw in command)
    plan_score = sum(1 for kw in plan_keywords if kw in command)

    certenty_threshold = 2
    if plan_score - chat_score >= certenty_threshold:
        return "PLAN"
    
    if chat_score - plan_score >= certenty_threshold:
        return "CHAT"
    
    return classify_intent(command) # Fallback to full classification


def process_hardcoded_command(command):
    #Checks for hardcoded commands. Returns response string or None.
    command = command.lower()
    if "open website" in command:
        try:
            url = command.lower().split("open website ", 1)[1].strip()
            if not (url.startswith("http://") or url.startswith("https://")):
                url = "http://" + url

            if not (url.endswith(".com") or url.endswith(".org") or url.endswith(".il")):
                url += ".com"

            webbrowser.open(url)
            add_logs(f"Action Taken: Opened Website {url}")
            return f"Yes Sir, opening website {url}."
        except:
            return None
    
    elif "open" in command:
        app_name = command.lower().split("open ", 1)[1].strip()
        try:
            open_app(app_name, match_closest=True, throw_error=True) 
            add_logs(f"Action Taken: Opened {app_name}")
            return f"Opening {app_name}."
        except:
            return None
        
    elif "lock computer" in command:
        subprocess.Popen('rundll32.exe user32.dll,LockWorkStation')
        add_logs("Action Taken: Locked Computer")
        return "Locking the computer, Sir."
    
    elif "fix this code" in command:
        # Extracting code from Clipboard
        try:
            code_to_fix = pyperclip.paste()
            if code_to_fix.strip() == "":
                return "Clipboard is empty, Sir. Please copy the code you want me to fix."
            fix_prompt = f"Please fix the following code/explain the error:\n{code_to_fix}"
            fixed_code = ask_jarvis(fix_prompt)
            pyperclip.copy(fixed_code)
            add_logs("Action Taken: Fixed Code from Clipboard")
            return "The code has been fixed and copied back to your clipboard, Sir."
        except Exception as e:
            return f"Error fixing code: {str(e)}"


    elif "work mode" in command:
        subprocess.run(["C:\\Users\\ofribs\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"])
        webbrowser.open("https://gemini.google.com/app")
        add_logs("Action Taken: Entered Work Mode (VS Code and Gemini opened)")
        return "Entering Work Mode, Sir. VS Code and Gemini are now open."

    elif "matrix protocol" in command or "hack" in command:
        cmd_command = 'start "" cmd /k "color 0a & title MATRIX_PROTOCOL & tree C:/"' 
        subprocess.run(cmd_command, shell=True)
        add_logs("Action Taken: Activated Matrix Protocol")
        return "Accessing the mainframe. Matrix protocol initiated."    
    
    return None


# Parses and executes the plan JSON
def parse_and_execute_plan(plan_json):    
    results = []
    print(f"[DEBUG] Executing Plan: {plan_json.get('goal')}")

    for step in plan_json.get("plan", []):
        action_name = step.get("action")
        params = step.get("params", {})

        action_func = ACTIONS_REGISTRY.get(action_name)
        if action_func:
            print(f"[DEBUG] Executing Action: {action_name} with params {params}")
            try:
                result = action_func(**params)
                if result.startswith("Error"):
                    results.append({"action": f"{action_name.replace("_", " ")}", "status": "failed"})
                    print(f"[DEBUG] Action Failed: {result}")
                else:
                    results.append({"action": f"{action_name.replace("_", " ")}", "status": "success"})
            except Exception as e:
                results.append({"action": f"{action_name.replace("_", " ")}", "status": "failed"})
        else:
            results.append({"action": f"{action_name.replace("_", " ")}", "status": "failed"})

    return results

def clean_json_response(text):
    # Cleans response to extract valid JSON
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()
    

# Main processing function
def process_user_input(user_input):

    hardcoded_response = process_hardcoded_command(user_input)
    if hardcoded_response is not None:
        return hardcoded_response

    intent = quick_classify_intent(user_input)
    if intent == "PLAN":
        plan_prompt = f""" [PLAN MODE]: "{user_input}" """
        response = ask_jarvis(plan_prompt)
        response = clean_json_response(response)
        plan_json = None
        
        for _ in range(3):
            try:
                print(f"[DEBUG] Plan Response Attempt: {response}")
                plan_json = json.loads(response)
                break
            except json.JSONDecodeError:
                response = ask_jarvis("The previous response was not valid JSON. Please provide the plan in correct JSON format only.")

        if plan_json is None:
            add_logs("Planner failed to produce valid JSON.")
            return "I could not create a valid plan, Sir."

        results = parse_and_execute_plan(plan_json)
        faild_actions = []
        for res in results:
            action = res['action']
            status = res['status']
            if status != 'success':
                faild_actions.append(action + ", " + status)

        if faild_actions:
            return f"Plan executed with some issues. Failed actions: {', '.join(faild_actions)}"
        
        plan_json_goal = plan_json.get("goal", "the requested tasks")
        add_logs(f"Plan executed successfully: {plan_json_goal}")
        plan_json_goal = plan_json_goal.replace("User wants to ", "") # removed the first "User wants to" if exists
        return f"Yes sir, I have completed the plan for {plan_json_goal}."
                
    
    if intent == "CHAT":
        chat_prompt = f""" [CHAT MODE]: "{user_input}" """
        return ask_jarvis(chat_prompt)
    
    else:
        return "I'm sorry, Sir, but I couldn't determine the intent of your request."
        

if __name__ == "__main__":
    initialize_memory()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting Jarvis. Goodbye, Sir.")
            break
        response = process_user_input(user_input)
        print(f"Jarvis: {response}")

