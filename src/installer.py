import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import subprocess
import os
import sys
import urllib.request

# --- Global Config ---
REPO_URL = "https://github.com/ofri09bs/JARVIS-AI-Assistant.git"
ENTRY_POINT_SCRIPT = os.path.join("src", "jarvis_interface.py") 
EXE_NAME = "Jarvis Assistant"

# --- Python Version Config ---
PYTHON_VERSION = "3.11.9"
PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"

# --- Global Variables ---
root = tk.Tk()
install_directory = tk.StringVar()
install_directory.set(os.path.join(os.getenv("USERPROFILE"), "Jarvis Assistant"))
google_api_var = tk.StringVar()
groq_api_var = tk.StringVar()

jarvis_python_exe = ""

def run_hidden_command(cmd, cwd=None, check=True):
    # run command without showing a console window
    startupinfo = None
    creationflags = 0
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW

    return subprocess.run(
        cmd, cwd=cwd, check=check, 
        startupinfo=startupinfo, creationflags=creationflags,
        capture_output=True, text=True
    )

def setup_isolated_python(progress_callback):
    # Downloads and installs Python 3.11 in an isolated environment
    global jarvis_python_exe
    
    base_dir = os.path.join(os.getenv("USERPROFILE"), "JarvisPythonEnv")
    python_exe = os.path.join(base_dir, "python.exe")
    installer_path = os.path.join(os.getenv("TEMP"), "python_installer.exe")

    if os.path.exists(python_exe):
        jarvis_python_exe = python_exe
        return

    try:
        urllib.request.urlretrieve(PYTHON_INSTALLER_URL, installer_path)
    except Exception as e:
        raise Exception(f"Failed to download Python: {e}")

    cmd = [
        installer_path, "/quiet", "InstallAllUsers=0", 
        f"TargetDir={base_dir}", "PrependPath=0", 
        "Include_test=0", "Include_tcltk=1", "Include_pip=1"
    ]
    run_hidden_command(cmd, check=True)

    if os.path.exists(installer_path):
        os.remove(installer_path)

    if not os.path.exists(python_exe):
        raise Exception("Python installation failed.")

    jarvis_python_exe = python_exe

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

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
    def browse_folder():
        folder = filedialog.askdirectory()
        if folder: install_directory.set(folder)
    ttk.Button(input_frame, text="Browse...", command=browse_folder).pack(side=tk.RIGHT)
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
    btn_frame = ttk.Frame(root, padding=(0, 0, 0, 20))
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
    ttk.Button(btn_frame, text="Save and Install", command=step_four_installing).pack(pady=10)

def create_env_file():
    target_dir = install_directory.get()
    userdata_dir = os.path.join(target_dir, "userdata")
    if not os.path.exists(userdata_dir):
        os.makedirs(userdata_dir)
    env_path = os.path.join(userdata_dir, ".env")
    with open(env_path, 'w') as f:
        f.write(f"GOOGLE_AI_API_KEY={google_api_var.get()}\n")
        f.write(f"GROQ_API_KEY={groq_api_var.get()}\n")

def install_requirements(target_dir):
    req_path = os.path.join(target_dir, "requirements.txt")
    if os.path.exists(req_path):
        run_hidden_command([jarvis_python_exe, "-m", "pip", "install", "-r", req_path])
    run_hidden_command([jarvis_python_exe, "-m", "pip", "install", "pyinstaller"])

def build_exe(target_dir):
    # Paths
    script_path = os.path.join(target_dir, ENTRY_POINT_SCRIPT)
    assets_dir = os.path.join(target_dir, "assets")
    src_dir = os.path.join(target_dir, "src") # הנתיב לתיקיית הקוד
    icon_path = os.path.join(assets_dir, "jarvis_logo.ico")
    
    if not os.path.exists(script_path):
        print(f"Error: Could not find {ENTRY_POINT_SCRIPT}")
        return False

    cmd = [
        jarvis_python_exe, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", EXE_NAME,
        "--distpath", target_dir,
        "--workpath", os.path.join(target_dir, "build"),
        "--specpath", os.path.join(target_dir, "build"),
        
        f"--paths={src_dir}", 
        
        # Include Assets
        f"--add-data={assets_dir};assets",
        
        script_path
    ]
    
    if os.path.exists(icon_path):
        cmd.insert(-1, f"--icon={icon_path}")
    
    run_hidden_command(cmd, cwd=target_dir)
    return True

def create_desktop_shortcut(target_dir):
    exe_path = os.path.join(target_dir, f"{EXE_NAME}.exe")
    icon_path = os.path.join(target_dir, "assets", "jarvis_logo.ico") # Path to the icon for the shortcut
    desktop = os.path.join(os.getenv("USERPROFILE"), "Desktop")
    shortcut_path = os.path.join(desktop, f"{EXE_NAME}.lnk")
    
    ps_script = f"""
    $s=(New-Object -COM WScript.Shell).CreateShortcut('{shortcut_path}');
    $s.TargetPath='{exe_path}';
    $s.WorkingDirectory='{target_dir}';
    $s.Description='Launch Jarvis Assistant';
    $s.IconLocation='{icon_path}'; 
    $s.Save()
    """
    run_hidden_command(["powershell", "-Command", ps_script])

def install_logic_thread(progress_callback, finished_callback):
    target_dir = install_directory.get()
    try:
        progress_callback(5)
        setup_isolated_python(progress_callback)
        
        progress_callback(15)
        if os.path.exists(os.path.join(target_dir, ".git")):
             run_hidden_command(["git", "pull"], cwd=target_dir, check=False)
        else:
            if not os.path.exists(target_dir): os.makedirs(target_dir)
            if not (os.path.exists(target_dir) and os.listdir(target_dir)):
                 run_hidden_command(["git", "clone", "--depth", "1", REPO_URL, target_dir])
        
        progress_callback(40)
        install_requirements(target_dir)
        
        progress_callback(80)
        build_exe(target_dir)
        
        progress_callback(95)
        create_env_file()
        create_desktop_shortcut(target_dir)
        progress_callback(100)

    except Exception as e:
        messagebox.showerror("Installation Error", f"An error occurred:\n{str(e)}")
        
    time.sleep(1)
    finished_callback()

def step_four_installing():
    clear_window()
    header = tk.Label(root, text="Installing...", font=("Arial", 14))
    header.pack(pady=20)
    progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress.pack(pady=20)
    status_label = tk.Label(root, text="Starting...", font=("Arial", 10))
    status_label.pack()

    def update_progress(value):
        progress['value'] = value
        if value < 15: msg = "Setting up Python 3.11 Environment..."
        elif value < 40: msg = "Downloading Repository..."
        elif value < 80: msg = "Installing Libraries..."
        elif value < 95: msg = "Compiling Jarvis App..."
        else: msg = "Done!"
        status_label.config(text=msg)

    def on_install_finished():
        root.after(0, step_five_finish)

    threading.Thread(target=install_logic_thread, args=(update_progress, on_install_finished), daemon=True).start()

def step_five_finish():
    clear_window()
    header = tk.Label(root, text="Installation Complete!", font=("Arial", 14, "bold"), fg="green")
    header.pack(pady=20)
    desc = tk.Label(root, text=f"Installed to:\n{install_directory.get()}", padx=20)
    desc.pack(pady=10)
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn_frame, text="Finish", command=root.quit).pack(side=tk.RIGHT)

def main():
    root.title("Jarvis Assistant Installer")
    root.geometry("500x400")
    if os.path.exists("jarvis_logo.ico"):
        root.iconbitmap("jarvis_logo.ico")
    step_one_welcome()
    root.mainloop()

if __name__ == "__main__":
    main()