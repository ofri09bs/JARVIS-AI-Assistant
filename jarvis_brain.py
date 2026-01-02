import google.generativeai as genai
import webbrowser
import os
from dotenv import load_dotenv
import subprocess
import pyperclip
from AppOpener import open as open_app
import json
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


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
[PLAN MODE]: You are an AI planner.
Return ONLY valid JSON.
Do not explain.
Do not use markdown.
Do not add any extra text.
Your goal is to break down the user's goal into clear, actionable steps.
If you cannot plan, return {"error": "..."}.

The JSON must follow this schema:

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

Available actions:
- {"action": "open_app", "params": {"app_name": string}}
- {"action": "close_app", "params": {"app_name": string}}
- {"action": "open_file", "params": {"path": string}}
- {"action": "set_volume", "params": {"level": int}}
- {"action": "lock_system", "params": {}}
- {"action": "open_website", "params": {"url": string}}

[QUESTION MODE]:
You Need to answer the question as accurately as possible.
Answer ONLY on what you got asked. DO NOT ADD ANY EXTRA INFORMATION.
Just a SHORT and CONCISE answer. (Usally it will be one word)

"""

genai.configure(api_key=API_KEY)

memory = None

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


def set_volume(level):
    level = max(0, min(100, level))

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # level 0-100 -> 0.0-1.0
    volume_level = level / 100
    volume.SetMasterVolumeLevelScalar(volume_level, None)


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


def parse_and_execute_plan(plan_json):    
    
    plan = plan_json
    ALLOWED_ACTIONS = {"open_app", "close_app", "open_file", "set_volume", "lock_system", "open_website"}
    results = []

    add_logs(f"Executing plan for goal: {plan.get('goal')}")
    print(f"[DEBUG] Goal: {plan.get('goal')}")


    for step in plan.get("steps", []):
        action = step.get("action")
        params = step.get("params", {})

        
        if action not in ALLOWED_ACTIONS:
            add_logs(f"Blocked unknown action: {action}")
            results.append({'action': f" {action.replace("_", " ")}", 'status': 'blocked'})
            continue
        
        if action == "open_app":
            app_name = params.get("app_name")
            if app_name:
                try:
                    open_app(app_name, match_closest=True, throw_error=True)
                    add_logs(f"Action Taken: Opened {app_name} as per plan.")
                    results.append({'action': action, 'status': 'success'})
                except Exception as e:
                    add_logs(f"Error: Could not open {app_name} as per plan. Exception: {str(e)}")
                    results.append({'action': f" {action.replace("_", " ")} {app_name}", 'status': 'failed'})
        
        elif action == "close_app":
            app_name = params.get("app_name")
            if app_name:
                try:
                    path = subprocess.check_output(["where", app_name], shell=True).decode().strip()
                    subprocess.run(["taskkill", "/IM", path, "/F"])
                    add_logs(f"Action Taken: Closed {app_name} as per plan.")
                    results.append({'action': action, 'status': 'success'})
                except Exception as e:
                    add_logs(f"Error: Could not close {app_name} as per plan. Exception: {str(e)}")
                    results.append({'action': f" {action.replace("_", " ")} {app_name}", 'status': 'failed'})
            
        elif action == "open_file":
            path = params.get("path")
            if path and os.path.exists(path):
                os.startfile(path)
                add_logs(f"Action Taken: Opened file at {path} as per plan.")
                results.append({'action': action, 'status': 'success'})
            else:
                add_logs(f"Error: File at {path} does not exist as per plan.")
                results.append({'action': f" {action.replace("_", " ")} {path}", 'status': 'failed'})
        
        elif action == "set_volume":
            level = params.get("level")
            if level is not None:
                try:
                    set_volume(level)
                    add_logs(f"Action Taken: Set volume to {level}% as per plan.")
                    results.append({'action': action, 'status': 'success'})
                except Exception as e:
                    add_logs(f"Error: Could not set volume to {level}% as per plan. Exception: {str(e)}")
                    results.append({'action': f" {action.replace("_", " ")} {level}", 'status': 'failed'})
            else:
                results.append({'action': f" {action.replace("_", " ")} {level}", 'status': 'failed'})
        
        elif action == "lock_system":
            subprocess.Popen('rundll32.exe user32.dll,LockWorkStation')
            add_logs("Action Taken: Locked System as per plan.")
            results.append({'action': action, 'status': 'success'})

        elif action == "open_website":
            url = params.get("url")
            if url:
                webbrowser.open(url)
                add_logs(f"Action Taken: Opened website {url} as per plan.")
                results.append({'action': action, 'status': 'success'})
            else:
                add_logs(f"Error: No URL provided for open_website action as per plan.")
                results.append({'action': f" {action.replace("_", " ")}", 'status': 'failed'})


    return results


def clean_json_response(text):
    # Cleans response to extract valid JSON
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()
    

def process_user_input(user_input):

    hardcoded_response = process_hardcoded_command(user_input)
    if hardcoded_response is not None:
        return hardcoded_response

    intent = classify_intent(user_input)
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
        
        return "Plan executed successfully, Sir."
                
    
    if intent == "CHAT":
        chat_prompt = f""" [CHAT MODE]: "{user_input}" """
        return ask_jarvis(chat_prompt)
    
    else:
        return "I'm sorry, Sir, but I couldn't determine the intent of your request."
        
# more functions can be added here for additional Jarvis capabilities


