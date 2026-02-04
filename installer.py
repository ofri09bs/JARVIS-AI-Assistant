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

def create_spec_file(target_dir):

    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

src_path = os.path.join(os.getcwd(), 'src')
assets_path = os.path.join(os.getcwd(), 'assets')

a = Analysis(
    [os.path.join('src', 'jarvis_interface.py')],
    pathex=[src_path], 
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=['jarvis_brain', 'jarvis_voice', 'jarvis_visualizer', 'groq', 'google.generativeai', 'PIL', 'pynput'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{EXE_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Windowed mode (בלי חלון שחור)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join('assets', 'jarvis_logo.ico')
)
"""
    spec_path = os.path.join(target_dir, "jarvis.spec")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)
    return spec_path

def build_exe(target_dir):
    # 1. creating the Spec file
    print("[DEBUG] Generating Spec file...")
    spec_path = create_spec_file(target_dir)
    
    # 2. running PyInstaller with the Spec file
    print("[DEBUG] Running PyInstaller on Spec file...")
    
    cmd = [jarvis_python_exe, "-m", "PyInstaller", "--noconfirm", "jarvis.spec"]
    
    run_hidden_command(cmd, cwd=target_dir)
    
    # 3. copying the EXE out of the dist folder
    dist_exe = os.path.join(target_dir, "dist", f"{EXE_NAME}.exe")
    final_exe = os.path.join(target_dir, f"{EXE_NAME}.exe")
    
    if os.path.exists(dist_exe):
        if os.path.exists(final_exe): os.remove(final_exe)
        shutil.move(dist_exe, final_exe)
        shutil.rmtree(os.path.join(target_dir, "dist"), ignore_errors=True)
        shutil.rmtree(os.path.join(target_dir, "build"), ignore_errors=True)
        return True
    else:
        raise Exception("Build failed: EXE not found in dist folder.")

def create_desktop_shortcut(target_dir):
    exe_path = os.path.join(target_dir, f"{EXE_NAME}.exe")
    
    if not os.path.exists(exe_path):
        print(f"[ERROR] Cannot create shortcut. EXE not found at: {exe_path}")
        return

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
    
    vbs_file = os.path.join(target_dir, "create_shortcut.vbs")
    with open(vbs_file, "w") as f:
        f.write(vbs_script)
    
    run_hidden_command(["cscript", "//Nologo", vbs_file])
    
    if os.path.exists(vbs_file):
        os.remove(vbs_file)

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