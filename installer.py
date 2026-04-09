import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import os
import shutil
import urllib.request
import zipfile

# --- Global Configuration ---
# GitHub ZIP URL to avoid requiring Git on the user's machine
REPO_ZIP_URL = "https://github.com/ofri09bs/JARVIS-AI-Assistant/archive/refs/heads/main.zip"
EXE_NAME = "Jarvis Assistant"
ENTRY_POINT_SCRIPT = "main.py"  
PYTHON_ZIP_URL = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

# --- Global UI Variables ---
root = tk.Tk()
install_directory = tk.StringVar()
install_directory.set(os.path.join(os.getenv("USERPROFILE", "C:\\"), "Jarvis Assistant"))

# --- Global State ---
jarvis_python_exe = ""

# --- Helper Functions ---

def run_hidden_command(cmd, cwd=None):
    # Runs a command silently without popping up a console window
    startupinfo = None
    creationflags = 0
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW
        
    result = subprocess.run(
        cmd, 
        cwd=cwd, 
        capture_output=True, 
        text=True, 
        startupinfo=startupinfo, 
        creationflags=creationflags
    )
    
    if result.returncode != 0:
        raise Exception(f"Command failed: {' '.join(cmd)}\nError: {result.stderr}")
    return result

def download_file(url, dest):
    # Downloads a file with a fallback to curl if urllib fails
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception:
        run_hidden_command(["curl", "-L", "-o", dest, url])

# --- Core Installation Logic ---

def setup_portable_python():
    # Downloads and configures an isolated embeddable Python environment
    global jarvis_python_exe
    base_dir = os.path.join(os.getenv("USERPROFILE", "C:\\"), "JarvisPythonEnv")
    python_exe = os.path.join(base_dir, "python.exe")
    
    if os.path.exists(python_exe):
        jarvis_python_exe = python_exe
        return

    # Clean existing broken setups
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir, ignore_errors=True)
    os.makedirs(base_dir, exist_ok=True)

    zip_path = os.path.join(os.getenv("TEMP"), "python_embed.zip")
    
    try:
        download_file(PYTHON_ZIP_URL, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(base_dir)
            
        # Modify the .pth file to allow pip and third-party packages to work
        pth_file = os.path.join(base_dir, "python311._pth")
        if os.path.exists(pth_file):
            with open(pth_file, 'r') as f:
                content = f.read()
            
            content = content.replace("#import site", "import site")
            
            with open(pth_file, 'w') as f:
                f.write(content)

        # Install pip
        get_pip_path = os.path.join(base_dir, "get-pip.py")
        download_file(GET_PIP_URL, get_pip_path)
        run_hidden_command([python_exe, get_pip_path], cwd=base_dir)
        
    finally:
        if os.path.exists(zip_path): 
            try: os.remove(zip_path)
            except: pass

    if not os.path.exists(python_exe):
        raise Exception("Portable Python setup failed.")
    
    jarvis_python_exe = python_exe

def download_and_extract_repo(target_dir):
    # Downloads the repository as a ZIP file, avoiding the need for Git installation
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    repo_zip_path = os.path.join(os.getenv("TEMP"), "jarvis_repo.zip")
    download_file(REPO_ZIP_URL, repo_zip_path)
    
    with zipfile.ZipFile(repo_zip_path, 'r') as zip_ref:
        # Extract files. GitHub zips contain a root folder (e.g., JARVIS-AI-Assistant-main)
        extract_path = os.path.join(os.getenv("TEMP"), "jarvis_extracted")
        zip_ref.extractall(extract_path)
        
        # Move contents from the inner folder to the target_dir
        inner_folder = os.path.join(extract_path, os.listdir(extract_path)[0])
        for item in os.listdir(inner_folder):
            s = os.path.join(inner_folder, item)
            d = os.path.join(target_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
                
    # Cleanup temp files
    os.remove(repo_zip_path)
    shutil.rmtree(extract_path)

def install_requirements(target_dir):
    # Installs the required libraries using the portable Python's pip
    req_file = os.path.join(target_dir, "requirements.txt")
    
    # Must explicitly install pyinstaller in the portable env first
    run_hidden_command([jarvis_python_exe, "-m", "pip", "install", "pyinstaller"])
    
    if os.path.exists(req_file):
        run_hidden_command([jarvis_python_exe, "-m", "pip", "install", "-r", req_file])

def build_exe(target_dir):
    # Uses PyInstaller from the portable python to compile the script
    script_path = os.path.join(target_dir, ENTRY_POINT_SCRIPT)

    if not os.path.exists(script_path):
        raise Exception(f"Could not find {ENTRY_POINT_SCRIPT} in {target_dir}")

    # Use the portable pyinstaller module to build the executable
    cmd = [
        jarvis_python_exe, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--name", EXE_NAME,
        "--distpath", target_dir,
        "--workpath", os.path.join(target_dir, "build"),
        "--specpath", os.path.join(target_dir, "build"),
        "--paths", target_dir,
        
        # The commands to ensure all modules are packaged
        "--hidden-import=core.jarvis_brain",
        "--hidden-import=ui.jarvis_cli",
        "--hidden-import=ui.jarvis_interface",
        "--hidden-import=features.jarvis_voice",
        "--hidden-import=features.jarvis_visualizer",
        
        "--hidden-import=AppOpener", "--collect-all=AppOpener",
        "--hidden-import=pynput", "--collect-all=pynput",
        "--hidden-import=pyautogui", "--collect-all=pyautogui",
        "--hidden-import=pycaw", "--collect-all=pycaw",
        "--hidden-import=edge_tts", "--collect-all=edge_tts",
        "--hidden-import=sounddevice", "--collect-all=sounddevice",
        "--hidden-import=ollama", "--collect-all=ollama",
        
        script_path
    ]

    icon_path = os.path.join(target_dir, "assets", "jarvis_logo.ico")
    if os.path.exists(icon_path):
        cmd.insert(-1, f"--icon={icon_path}")

    run_hidden_command(cmd, cwd=target_dir)

def create_desktop_shortcut(target_dir):
    # Generates a VBS script to safely create a Windows desktop shortcut
    exe_path = os.path.join(target_dir, f"{EXE_NAME}.exe")
    desktop = os.path.join(os.getenv("USERPROFILE"), "Desktop")
    shortcut_path = os.path.join(desktop, f"{EXE_NAME}.lnk")
    icon_path = os.path.join(target_dir, "assets", "jarvis_logo.ico")
    
    vbs_script = f"""
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{exe_path}"
    oLink.WorkingDirectory = "{target_dir}"
    oLink.Description = "Launch Jarvis Assistant"
    If CreateObject("Scripting.FileSystemObject").FileExists("{icon_path}") Then
        oLink.IconLocation = "{icon_path}, 0"
    End If
    oLink.Save
    """
    vbs_file = os.path.join(target_dir, "shortcut.vbs")
    with open(vbs_file, "w") as f:
        f.write(vbs_script)
    
    run_hidden_command(["cscript", "//Nologo", vbs_file])
    if os.path.exists(vbs_file): 
        os.remove(vbs_file)

def install_logic_thread(update_ui_callback, finished_callback):
    # The main installation sequence running on a separate background thread
    target_dir = install_directory.get()
    try:
        update_ui_callback(10, "Setting up Python 3.11 Environment...")
        setup_portable_python()
        
        update_ui_callback(30, "Downloading Repository...")
        download_and_extract_repo(target_dir)

        update_ui_callback(50, "Installing Libraries...")
        install_requirements(target_dir)
        
        update_ui_callback(75, "Compiling Jarvis App (This may take a few minutes)...")
        build_exe(target_dir)
        
        update_ui_callback(95, "Finalizing Setup...")
        create_desktop_shortcut(target_dir)
        
        update_ui_callback(100, "Done!")
        root.after(1000, finished_callback, True, "")

    except Exception as e:
        # Schedule the error message to show on the main GUI thread
        root.after(0, finished_callback, False, str(e))

# --- GUI Screens ---

def clear_window():
    # Destroys all widgets in the root window to load a new screen
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
    ttk.Button(input_frame, text="Browse...", command=lambda: install_directory.set(filedialog.askdirectory() or install_directory.get())).pack(side=tk.RIGHT)
    
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn_frame, text="Install >", command=step_three_installing).pack(side=tk.RIGHT)
    ttk.Button(btn_frame, text="< Back", command=step_one_welcome).pack(side=tk.RIGHT, padx=5)

def step_three_installing():
    clear_window()
    header = tk.Label(root, text="Installing...", font=("Arial", 14))
    header.pack(pady=20)
    
    pb = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
    pb.pack(pady=20)
    
    lbl = tk.Label(root, text="Starting...")
    lbl.pack()
    
    def update_ui(val, text):
        # Schedule UI updates on the main thread
        root.after(0, lambda: pb.config(value=val))
        root.after(0, lambda: lbl.config(text=text))
        
    def on_finish(success, error_msg):
        if success:
            step_four_finish()
        else:
            messagebox.showerror("Error", f"Installation Failed:\n{error_msg}")
            step_one_welcome() # Go back to start on failure

    # Start the heavy lifting on a daemon thread
    threading.Thread(target=install_logic_thread, args=(update_ui, on_finish), daemon=True).start()

def step_four_finish():
    clear_window()
    header = tk.Label(root, text="Installation Complete!", font=("Arial", 14, "bold"), fg="green")
    header.pack(pady=(20, 10))
    
    desc = tk.Label(root, text=f"The application has been successfully installed to:\n{install_directory.get()}", padx=20)
    desc.pack(pady=5)
    
    # Important reminder for local LLM users
    warning = tk.Label(root, text="Note: Jarvis requires Ollama running locally\nwith the 'gemma4:e4b' model to function.", fg="red", font=("Arial", 9, "italic"))
    warning.pack(pady=10)
    
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn_frame, text="Finish", command=root.quit).pack(side=tk.RIGHT)

if __name__ == "__main__":
    root.title("Jarvis Assistant Installer")
    root.geometry("500x350") # Slightly adjusted height
    if os.path.exists("jarvis_logo.ico"): 
        root.iconbitmap("jarvis_logo.ico")
    step_one_welcome()
    root.mainloop()
