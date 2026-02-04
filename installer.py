import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import subprocess
import os
import shutil
import urllib.request
import sys
import zipfile

# --- Global Config ---
REPO_URL = "https://github.com/ofri09bs/JARVIS-AI-Assistant.git"
EXE_NAME = "Jarvis Assistant"
# שימוש בגרסת EMBEDDED (ZIP) במקום במתקין EXE - הרבה יותר יציב!
PYTHON_ZIP_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

root = tk.Tk()
install_directory = tk.StringVar()
install_directory.set(os.path.join(os.getenv("USERPROFILE"), "Jarvis Assistant"))
google_api_var = tk.StringVar()
groq_api_var = tk.StringVar()

jarvis_python_exe = ""

def run_hidden_command(cmd, cwd=None, check=True):
    startupinfo = None
    creationflags = 0
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW
    return subprocess.run(cmd, cwd=cwd, check=check, startupinfo=startupinfo, creationflags=creationflags)

def download_file(url, dest):
    print(f"[INFO] Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as e:
        # Fallback to curl if urllib fails
        subprocess.run(["curl", "-L", "-o", dest, url], check=True, capture_output=True)

def setup_portable_python(progress_callback):
    """
    Sets up a Portable (Embedded) Python environment.
    Does NOT require Admin rights or installation!
    """
    global jarvis_python_exe
    base_dir = os.path.join(os.getenv("USERPROFILE"), "JarvisPythonEnv")
    python_exe = os.path.join(base_dir, "python.exe")
    
    # אם כבר קיים, נדלג
    if os.path.exists(python_exe):
        jarvis_python_exe = python_exe
        return

    # ניקוי התקנה ישנה
    if os.path.exists(base_dir):
        try: shutil.rmtree(base_dir)
        except: pass
    os.makedirs(base_dir, exist_ok=True)

    zip_path = os.path.join(os.getenv("TEMP"), "python_embed.zip")
    
    try:
        # 1. הורדת ה-ZIP
        download_file(PYTHON_ZIP_URL, zip_path)
        
        # 2. חילוץ ה-ZIP
        print("[INFO] Extracting Python...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(base_dir)
            
        # 3. תיקון קובץ ._pth כדי לאפשר התקנת ספריות (קריטי!)
        pth_file = os.path.join(base_dir, "python311._pth")
        if os.path.exists(pth_file):
            with open(pth_file, 'r') as f:
                content = f.read()
            # ביטול ההערה על 'import site'
            content = content.replace("#import site", "import site")
            with open(pth_file, 'w') as f:
                f.write(content)
        
        # 4. התקנת PIP (לא מגיע עם הגרסה הניידת)
        get_pip_path = os.path.join(base_dir, "get-pip.py")
        download_file(GET_PIP_URL, get_pip_path)
        
        print("[INFO] Installing pip...")
        run_hidden_command([os.path.join(base_dir, "python.exe"), get_pip_path], cwd=base_dir)
        
    finally:
        if os.path.exists(zip_path): 
            try: os.remove(zip_path)
            except: pass

    if not os.path.exists(python_exe):
        raise Exception("Portable Python setup failed.")
    
    jarvis_python_exe = python_exe

def install_requirements(target_dir):
    # שדרוג pip ו-setuptools ליתר ביטחון
    run_hidden_command([jarvis_python_exe, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    
    req_path = os.path.join(target_dir, "requirements.txt")
    if os.path.exists(req_path):
        run_hidden_command([jarvis_python_exe, "-m", "pip", "install", "-r", req_path])
    
    run_hidden_command([jarvis_python_exe, "-m", "pip", "install", "pyinstaller"])

def build_exe(target_dir):
    script_path = os.path.join(target_dir, "jarvis_interface.py")
    assets_dir = os.path.join(target_dir, "assets")
    
    # Flattening logic
    src_dir = os.path.join(target_dir, "src")
    if os.path.exists(src_dir):
        for f in os.listdir(src_dir):
            try: shutil.move(os.path.join(src_dir, f), os.path.join(target_dir, f))
            except: pass
        try: shutil.rmtree(src_dir)
        except: pass

    if not os.path.exists(script_path):
        print(f"[ERROR] jarvis_interface.py not found at {script_path}")
        return False

    cmd = [
        jarvis_python_exe, "-m", "PyInstaller",
        "jarvis_interface.py", 
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", EXE_NAME,
        "--add-data", "assets;assets",
        "--hidden-import=jarvis_brain",
        "--hidden-import=jarvis_voice",
        "--hidden-import=jarvis_visualizer",
        "--hidden-import=groq",
        "--hidden-import=google.generativeai",
        "--hidden-import=PIL",
        "--hidden-import=pynput"
    ]
    
    icon_path = os.path.join(assets_dir, "jarvis_logo.ico")
    if os.path.exists(icon_path):
        cmd.insert(-1, f"--icon=assets/jarvis_logo.ico")
    
    run_hidden_command(cmd, cwd=target_dir)
    return True

def create_desktop_shortcut(target_dir):
    exe_path = os.path.join(target_dir, f"{EXE_NAME}.exe")
    desktop = os.path.join(os.getenv("USERPROFILE"), "Desktop")
    shortcut_path = os.path.join(desktop, f"{EXE_NAME}.lnk")
    
    vbs_script = f"""
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{exe_path}"
    oLink.WorkingDirectory = "{target_dir}"
    oLink.Description = "Launch Jarvis Assistant"
    oLink.IconLocation = "{exe_path}, 0"
    oLink.Save
    """
    vbs_file = os.path.join(target_dir, "shortcut.vbs")
    with open(vbs_file, "w") as f:
        f.write(vbs_script)
    
    run_hidden_command(["cscript", "//Nologo", vbs_file])
    if os.path.exists(vbs_file): os.remove(vbs_file)

def create_env_file():
    target_dir = install_directory.get()
    userdata_dir = os.path.join(target_dir, "userdata")
    if not os.path.exists(userdata_dir): os.makedirs(userdata_dir)
    with open(os.path.join(userdata_dir, ".env"), 'w') as f:
        f.write(f"GOOGLE_AI_API_KEY={google_api_var.get()}\n")
        f.write(f"GROQ_API_KEY={groq_api_var.get()}\n")

def install_logic_thread(progress_callback, finished_callback):
    target_dir = install_directory.get()
    try:
        progress_callback(5)
        # שינוי: שימוש בגרסה הניידת
        setup_portable_python(progress_callback)
        
        progress_callback(15)
        if os.path.exists(os.path.join(target_dir, ".git")):
             run_hidden_command(["git", "pull"], cwd=target_dir)
        else:
            if not os.path.exists(target_dir): os.makedirs(target_dir)
            run_hidden_command(["git", "clone", "--depth", "1", REPO_URL, target_dir])

        progress_callback(40)
        install_requirements(target_dir)
        
        progress_callback(70)
        build_exe(target_dir)
        
        progress_callback(90)
        create_env_file()
        create_desktop_shortcut(target_dir)
        progress_callback(100)

    except Exception as e:
        messagebox.showerror("Error", f"Installation Failed:\n{str(e)}")
    
    time.sleep(1)
    finished_callback()

# --- GUI ---
def clear_window():
    for widget in root.winfo_children(): widget.destroy()

def step_one_welcome():
    clear_window()
    header = tk.Label(root, text="Welcome to the Installer", font=("Arial", 16, "bold"))
    header.pack(pady=20)
    desc = tk.Label(root, text="This wizard will install Jarvis AI Assistant.\nIt includes a dedicated Python environment.\nClick 'Next' to continue.", padx=20)
    desc.pack(pady=10)
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn_frame, text="Next >", command=step_two_directory).pack(side=tk.RIGHT)
    ttk.Button(btn_frame, text="Cancel", command=root.quit).pack(side=tk.RIGHT, padx=5)

def step_two_directory():
    clear_window()
    header = tk.Label(root, text="Select Installation Folder", font=("Arial", 14))
    header.pack(pady=20)
    input_frame = tk.Frame(root)
    input_frame.pack(pady=10, padx=20, fill=tk.X)
    ttk.Entry(input_frame, textvariable=install_directory).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    ttk.Button(input_frame, text="Browse...", command=lambda: install_directory.set(filedialog.askdirectory() or install_directory.get())).pack(side=tk.RIGHT)
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn_frame, text="Next >", command=step_three_setup_environment).pack(side=tk.RIGHT)
    ttk.Button(btn_frame, text="< Back", command=step_one_welcome).pack(side=tk.RIGHT, padx=5)

def step_three_setup_environment():
    clear_window()
    header = ttk.Label(root, text="Setting Up Environment", font=("Segoe UI", 16, "bold"))
    header.pack(pady=(30, 20))
    content_frame = ttk.Frame(root, padding=20)
    content_frame.pack(fill=tk.BOTH, expand=True)
    form_frame = ttk.Frame(content_frame)
    form_frame.pack(fill=tk.X, padx=20)
    form_frame.columnconfigure(1, weight=1)
    ttk.Label(form_frame, text="Google AI API Key:").grid(row=0, column=0, sticky="w", pady=10)
    ttk.Entry(form_frame, textvariable=google_api_var, width=40).grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=10)
    ttk.Label(form_frame, text="Groq API Key:").grid(row=1, column=0, sticky="w", pady=10)
    ttk.Entry(form_frame, textvariable=groq_api_var, width=40).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=10)
    btn_frame = ttk.Frame(root, padding=(0,0,0,20))
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
    ttk.Button(btn_frame, text="Save and Install", command=step_four_installing).pack(pady=10)

def step_four_installing():
    clear_window()
    header = tk.Label(root, text="Installing...", font=("Arial", 14))
    header.pack(pady=20)
    pb = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate'); pb.pack(pady=20)
    lbl = tk.Label(root, text="Starting..."); lbl.pack()
    def update(val):
        pb['value'] = val
        if val < 15: lbl.config(text="Setting up Python 3.11 Environment...")
        elif val < 40: lbl.config(text="Downloading Repository...")
        elif val < 70: lbl.config(text="Installing Libraries...")
        elif val < 90: lbl.config(text="Compiling Jarvis App...")
        else: lbl.config(text="Done!")
    threading.Thread(target=install_logic_thread, args=(update, lambda: root.after(0, step_five_finish)), daemon=True).start()

def step_five_finish():
    clear_window()
    header = tk.Label(root, text="Installation Complete!", font=("Arial", 14, "bold"), fg="green")
    header.pack(pady=20)
    desc = tk.Label(root, text=f"The application has been installed to:\n{install_directory.get()}", padx=20)
    desc.pack(pady=10)
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn_frame, text="Finish", command=root.quit).pack(side=tk.RIGHT)

if __name__ == "__main__":
    root.title("Jarvis Assistant Installer")
    root.geometry("500x400")
    if os.path.exists("jarvis_logo.ico"): root.iconbitmap("jarvis_logo.ico")
    step_one_welcome()
    root.mainloop()