import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import subprocess
import os
import sys

# --- Global Config ---
REPO_URL = "https://github.com/ofri09bs/JARVIS-AI-Assistant.git"
ENTRY_POINT_SCRIPT = "jarvis_interface.py"  
EXE_NAME = "Jarvis Assistant"

# --- Global Variables ---
root = tk.Tk()
install_directory = tk.StringVar()
install_directory.set(os.path.join(os.getenv("USERPROFILE"), "Jarvis Assistant"))
google_api_var = tk.StringVar()
groq_api_var = tk.StringVar()

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

def step_one_welcome():
    clear_window()
    header = tk.Label(root, text="Welcome to the Installer", font=("Arial", 16, "bold"))
    header.pack(pady=20)
    desc = tk.Label(root, text="This wizard will guide you through the installation process.\nClick 'Next' to continue.", padx=20)
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
        if folder:
            install_directory.set(folder)

    ttk.Button(input_frame, text="Browse...", command=browse_folder).pack(side=tk.RIGHT)

    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    
    ttk.Button(btn_frame, text="Next >", command=step_three_setup_environment).pack(side=tk.RIGHT)
    ttk.Button(btn_frame, text="< Back", command=step_one_welcome).pack(side=tk.RIGHT, padx=5)

def step_three_setup_environment():
    """
    Step 3: Collect Keys ONLY (Don't write file yet!)
    """
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
    """
    Creates the .env file in the userdata folder.
    """
    target_dir = install_directory.get()
    userdata_dir = os.path.join(target_dir, "userdata")
    
    if not os.path.exists(userdata_dir):
        os.makedirs(userdata_dir)
    
    env_path = os.path.join(userdata_dir, ".env")
    with open(env_path, 'w') as f:
        f.write(f"GOOGLE_AI_API_KEY={google_api_var.get()}\n")
        f.write(f"GROQ_API_KEY={groq_api_var.get()}\n")

def install_requirements(target_dir):
    """
    Installs the requirements.txt and pyinstaller using pip.
    """
    req_path = os.path.join(target_dir, "requirements.txt")
    
    # 1. Install project requirements
    if os.path.exists(req_path):
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_path], check=True)
    
    # 2. Install PyInstaller (needed to build the exe)
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)


def build_exe(target_dir):
    """
    Runs PyInstaller to create the EXE file.
    """
    script_path = os.path.join(target_dir, ENTRY_POINT_SCRIPT)
    
    if not os.path.exists(script_path):
        print(f"Error: Could not find {ENTRY_POINT_SCRIPT} in {target_dir}")
        return False

    # Command to build: onefile, windowed (no console), distpath = installation folder
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",  # Remove this if you WANT a console window
        "--name", EXE_NAME,
        "--distpath", target_dir,  # Output exe directly to install folder
        "--workpath", os.path.join(target_dir, "build"), # Keep build files inside temp
        "--specpath", os.path.join(target_dir, "build"),
        "--add-data", os.path.join(target_dir, "ironman_bg.jpg") + ";.",  # Include background image 
        "--add-data", os.path.join(target_dir, "jarvis_logo.ico") + ";icons",  # Include icons folder
        script_path
    ]
    
    subprocess.run(cmd, cwd=target_dir, check=True)
    return True

def create_desktop_shortcut(target_dir):
    """
    Creates a shortcut (.lnk) on the user's desktop using PowerShell.
    This is more robust than using external libraries like winshell.
    """
    exe_path = os.path.join(target_dir, f"{EXE_NAME}.exe")
    desktop = os.path.join(os.getenv("USERPROFILE"), "Desktop")
    shortcut_path = os.path.join(desktop, f"{EXE_NAME}.lnk")
    
    # PowerShell command to create shortcut
    ps_script = f"""
    $s=(New-Object -COM WScript.Shell).CreateShortcut('{shortcut_path}');
    $s.TargetPath='{exe_path}';
    $s.WorkingDirectory='{target_dir}';
    $s.Description='Launch Jarvis Assistant';
    $s.Save()
    """
    
    subprocess.run(["powershell", "-Command", ps_script], check=True)


def install_logic_thread(progress_callback, finished_callback):
    """
    Main Logic: Clone -> Requirements -> Build EXE -> Env File -> Shortcut
    """
    target_dir = install_directory.get()
    
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # --- Step 1: Clone Repo (0-20%) ---
        progress_callback(5)
        if os.path.exists(os.path.join(target_dir, ".git")):
            subprocess.run(["git", "pull"], cwd=target_dir, startupinfo=startupinfo, check=True)
        else:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if not (os.path.exists(target_dir) and os.listdir(target_dir)):
                 subprocess.run(["git", "clone", "--depth", "1", REPO_URL, target_dir], 
                               startupinfo=startupinfo, check=True)
        progress_callback(20)

        # --- Step 2: Install Requirements (20-50%) ---
        # Note: This might take time depending on internet speed
        print("Installing dependencies...")
        install_requirements(target_dir)
        progress_callback(50)

        # --- Step 3: Build EXE (50-90%) ---
        print("Building EXE...")
        build_success = build_exe(target_dir)
        if not build_success:
            raise Exception("Failed to build EXE")
        progress_callback(90)

        # --- Step 4: Create .env (90-95%) ---
        create_env_file()
        progress_callback(95)

        # --- Step 5: Create Shortcut (95-100%) ---
        create_desktop_shortcut(target_dir)
        progress_callback(100)

    except Exception as e:
        print(f"Critical Error: {e}")
        # In a real app, send a message to the UI thread to show an error popup
        
    time.sleep(1)
    finished_callback()

def step_four_installing():
    clear_window()
    header = tk.Label(root, text="Installing & Building...", font=("Arial", 14))
    header.pack(pady=20)

    # Added 'mode' indeterminate because building exe time is unpredictable
    progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress.pack(pady=20)
    
    status_label = tk.Label(root, text="Starting installation...", font=("Arial", 10))
    status_label.pack()

    def update_progress(value):
        progress['value'] = value
        if value < 20: msg = "Cloning repository..."
        elif value < 50: msg = "Installing Python libraries..."
        elif value < 90: msg = "Compiling EXE (This may take a few minutes)..."
        elif value < 100: msg = "Finalizing..."
        else: msg = "Done!"
        status_label.config(text=msg)

    def on_install_finished():
        root.after(0, step_five_finish)

    threading.Thread(target=install_logic_thread, args=(update_progress, on_install_finished), daemon=True).start()
def step_five_finish():
    clear_window()
    header = tk.Label(root, text="Installation Complete!", font=("Arial", 14, "bold"), fg="green")
    header.pack(pady=20)
    desc = tk.Label(root, text=f"The application has been installed to:\n{install_directory.get()}", padx=20)
    desc.pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
    ttk.Button(btn_frame, text="Finish", command=root.quit).pack(side=tk.RIGHT)

def main():
    root.title("Jarvis Assistant Installer")
    root.geometry("500x400")
    root.resizable(False, False)
    step_one_welcome()
    root.mainloop()

if __name__ == "__main__":
    main()