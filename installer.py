import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import subprocess
import os
import shutil
import urllib.request
import sys

# --- Global Config ---
REPO_URL = "https://github.com/ofri09bs/JARVIS-AI-Assistant.git"
EXE_NAME = "Jarvis Assistant"
PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"

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

def setup_isolated_python(progress_callback):
    global jarvis_python_exe
    base_dir = os.path.join(os.getenv("USERPROFILE"), "JarvisPythonEnv")
    python_exe = os.path.join(base_dir, "python.exe")
    if os.path.exists(python_exe):
        jarvis_python_exe = python_exe
        return
    installer_path = os.path.join(os.getenv("TEMP"), "python_installer.exe")
    try:
        urllib.request.urlretrieve(PYTHON_INSTALLER_URL, installer_path)
        cmd = [installer_path, "/quiet", "InstallAllUsers=0", f"TargetDir={base_dir}", "PrependPath=0", "Include_test=0", "Include_tcltk=1", "Include_pip=1"]
        run_hidden_command(cmd, check=True)
    finally:
        if os.path.exists(installer_path): os.remove(installer_path)
    if not os.path.exists(python_exe): raise Exception("Python installation failed.")
    jarvis_python_exe = python_exe

def install_requirements(target_dir):
    req_path = os.path.join(target_dir, "requirements.txt")
    if os.path.exists(req_path):
        run_hidden_command([jarvis_python_exe, "-m", "pip", "install", "-r", req_path])
    run_hidden_command([jarvis_python_exe, "-m", "pip", "install", "pyinstaller"])

def build_exe(target_dir):
    src_dir = os.path.join(target_dir, "src")
    assets_dir = os.path.join(target_dir, "assets")
    
    
    if os.path.exists(src_dir):
        for filename in os.listdir(src_dir):
            source_file = os.path.join(src_dir, filename)
            dest_file = os.path.join(target_dir, filename)
            if os.path.isfile(source_file):
                print(f"Moving {filename} to root...")
                shutil.move(source_file, dest_file)
    
    script_path = os.path.join(target_dir, "jarvis_interface.py") 
    
    if not os.path.exists(script_path):
        raise Exception(f"Critical Error: jarvis_interface.py not found in {target_dir} after flattening.")

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
    
    print(f"Building EXE from root directory...")
    
    run_hidden_command(cmd, cwd=target_dir)
    return True

def create_desktop_shortcut(target_dir):
    exe_path = os.path.join(target_dir, f"{EXE_NAME}.exe")
    desktop = os.path.join(os.getenv("USERPROFILE"), "Desktop")
    shortcut_path = os.path.join(desktop, f"{EXE_NAME}.lnk")
    ps_script = f"""
    $s=(New-Object -COM WScript.Shell).CreateShortcut('{shortcut_path}');
    $s.TargetPath='{exe_path}';
    $s.WorkingDirectory='{target_dir}';
    $s.Description='Launch Jarvis Assistant';
    $s.IconLocation='{exe_path},0'; 
    $s.Save()
    """
    run_hidden_command(["powershell", "-Command", ps_script])

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
        setup_isolated_python(progress_callback)
        
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
    tk.Label(root, text="Jarvis Installer", font=("Arial", 16, "bold")).pack(pady=20)
    tk.Label(root, text="One-Click Installation.", padx=20).pack(pady=10)
    btn = tk.Frame(root); btn.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn, text="Next >", command=step_two_directory).pack(side=tk.RIGHT)
    ttk.Button(btn, text="Cancel", command=root.quit).pack(side=tk.RIGHT, padx=5)

def step_two_directory():
    clear_window()
    tk.Label(root, text="Installation Folder", font=("Arial", 14)).pack(pady=20)
    fr = tk.Frame(root); fr.pack(pady=10, padx=20, fill=tk.X)
    ttk.Entry(fr, textvariable=install_directory).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
    ttk.Button(fr, text="Browse...", command=lambda: install_directory.set(filedialog.askdirectory() or install_directory.get())).pack(side=tk.RIGHT)
    btn = tk.Frame(root); btn.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn, text="Next >", command=step_three_setup_environment).pack(side=tk.RIGHT)
    ttk.Button(btn, text="< Back", command=step_one_welcome).pack(side=tk.RIGHT, padx=5)

def step_three_setup_environment():
    clear_window()
    ttk.Label(root, text="API Keys", font=("Segoe UI", 16, "bold")).pack(pady=20)
    fr = ttk.Frame(root, padding=20); fr.pack(fill=tk.BOTH, expand=True)
    gf = ttk.Frame(fr); gf.pack(fill=tk.X); gf.columnconfigure(1, weight=1)
    ttk.Label(gf, text="Google AI Key:").grid(row=0, column=0, sticky="w", pady=10)
    ttk.Entry(gf, textvariable=google_api_var).grid(row=0, column=1, sticky="ew", padx=10)
    ttk.Label(gf, text="Groq API Key:").grid(row=1, column=0, sticky="w", pady=10)
    ttk.Entry(gf, textvariable=groq_api_var).grid(row=1, column=1, sticky="ew", padx=10)
    btn = ttk.Frame(root, padding=(0,0,0,20)); btn.pack(side=tk.BOTTOM, fill=tk.X)
    ttk.Button(btn, text="Install Now", command=step_four_installing).pack(pady=10)

def step_four_installing():
    clear_window()
    tk.Label(root, text="Installing...", font=("Arial", 14)).pack(pady=20)
    pb = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate'); pb.pack(pady=20)
    lbl = tk.Label(root, text="Init..."); lbl.pack()
    
    def update(val):
        pb['value'] = val
        if val < 40: lbl.config(text="Downloading...")
        elif val < 70: lbl.config(text="Deps...")
        elif val < 90: lbl.config(text="Building...")
        else: lbl.config(text="Done!")

    threading.Thread(target=install_logic_thread, args=(update, lambda: root.after(0, step_five_finish)), daemon=True).start()

def step_five_finish():
    clear_window()
    tk.Label(root, text="Done!", font=("Arial", 14, "bold"), fg="green").pack(pady=20)
    tk.Label(root, text=f"Installed to:\n{install_directory.get()}", padx=20).pack(pady=10)
    btn = tk.Frame(root); btn.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn, text="Exit", command=root.quit).pack(side=tk.RIGHT)

if __name__ == "__main__":
    root.title("Jarvis Installer")
    root.geometry("500x400")
    if os.path.exists("jarvis_logo.ico"): root.iconbitmap("jarvis_logo.ico")
    step_one_welcome()
    root.mainloop()