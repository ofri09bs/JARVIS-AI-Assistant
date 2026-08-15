import os
import sys
import threading
import urllib.request
import zipfile
import shutil
import subprocess
import json
import time
import struct
import platform
import socket
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --- Constants & Config ---
APP_NAME = "JARVIS Assistant"
VERSION = "6.5"
GITHUB_REPO_ZIP = "https://github.com/ofri09bs/JARVIS-AI-Assistant/archive/refs/heads/main.zip"
PYTHON_EMBED_ZIP = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
OLLAMA_SETUP_URL = "https://ollama.com/download/OllamaSetup.exe"

MODELS_TO_PULL = ["gemma4:e4b", "qwen2.5:0.5b"]

# Theme Colors
BG_COLOR = "#1a1a2e"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#00e5ff"
BG_ALT_COLOR = "#2a2a4e"

class InstallerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — Setup Wizard")
        self.geometry("600x450")
        self.resizable(False, False)
        self.configure(bg=BG_COLOR)
        
        # Try to set icon
        icon_path = os.path.join(os.path.dirname(__file__), "jarvis_logo.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except:
                pass
                
        self.install_dir = tk.StringVar(value=os.path.join(os.getenv('USERPROFILE', 'C:\\'), 'Jarvis Assistant'))
        self.create_shortcut = tk.BooleanVar(value=True)
        self.launch_now = tk.BooleanVar(value=True)
        
        self.frames = {}
        self.current_frame = None
        
        self.setup_styles()
        self.build_ui()
        self.show_frame("welcome")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure common styles
        style.configure('TFrame', background=BG_COLOR)
        style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR, font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground=ACCENT_COLOR)
        style.configure('Subheader.TLabel', font=('Segoe UI', 12))
        
        style.configure('TButton', background=BG_ALT_COLOR, foreground=FG_COLOR, borderwidth=0, padding=5, font=('Segoe UI', 10))
        style.map('TButton', background=[('active', ACCENT_COLOR)], foreground=[('active', BG_COLOR)])
        
        style.configure('TCheckbutton', background=BG_COLOR, foreground=FG_COLOR, font=('Segoe UI', 10))
        style.map('TCheckbutton', background=[('active', BG_COLOR)])
        
        # Progress bar style
        style.configure('Horizontal.TProgressbar', background=ACCENT_COLOR, troughcolor=BG_ALT_COLOR, borderwidth=0, thickness=15)

    def build_ui(self):
        # Step 1: Welcome
        f1 = ttk.Frame(self)
        self.frames["welcome"] = f1
        ttk.Label(f1, text=f"Welcome to {APP_NAME} {VERSION}", style='Header.TLabel').pack(pady=(40, 10))
        ttk.Label(f1, text="Just A Rather Very Intelligent System - AI Desktop Assistant", style='Subheader.TLabel').pack(pady=10)
        
        reqs = "System Requirements:\n• Windows 10/11 64-bit\n• Active internet connection\n• ~2GB free disk space"
        ttk.Label(f1, text=reqs, justify=tk.LEFT).pack(pady=30, padx=50, anchor="w")
        
        btn_frame1 = ttk.Frame(f1)
        btn_frame1.pack(side="bottom", fill="x", pady=20, padx=20)
        ttk.Button(btn_frame1, text="Next >", command=lambda: self.show_frame("directory")).pack(side="right", padx=5)
        ttk.Button(btn_frame1, text="Cancel", command=self.destroy).pack(side="right", padx=5)

        # Step 2: Directory
        f2 = ttk.Frame(self)
        self.frames["directory"] = f2
        ttk.Label(f2, text="Select Installation Directory", style='Header.TLabel').pack(pady=(40, 20))
        
        dir_frame = ttk.Frame(f2)
        dir_frame.pack(fill="x", padx=40, pady=10)
        ttk.Entry(dir_frame, textvariable=self.install_dir, width=45, font=('Segoe UI', 10)).pack(side="left", padx=(0, 10))
        ttk.Button(dir_frame, text="Browse...", command=self.browse_dir).pack(side="left")
        
        ttk.Label(f2, text="Estimated space required: 2.1 GB").pack(pady=20)
        
        btn_frame2 = ttk.Frame(f2)
        btn_frame2.pack(side="bottom", fill="x", pady=20, padx=20)
        ttk.Button(btn_frame2, text="Install >", command=self.start_installation).pack(side="right", padx=5)
        ttk.Button(btn_frame2, text="< Back", command=lambda: self.show_frame("welcome")).pack(side="right", padx=5)
        ttk.Button(btn_frame2, text="Cancel", command=self.destroy).pack(side="right", padx=5)

        # Step 3: Progress
        f3 = ttk.Frame(self)
        self.frames["progress"] = f3
        ttk.Label(f3, text="Installing...", style='Header.TLabel').pack(pady=(20, 10))
        
        self.lbl_status = ttk.Label(f3, text="Preparing installation...")
        self.lbl_status.pack(pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(f3, variable=self.progress_var, maximum=100, mode='determinate', style='Horizontal.TProgressbar')
        self.progressbar.pack(fill="x", padx=40, pady=10)
        
        self.lbl_pct = ttk.Label(f3, text="0%")
        self.lbl_pct.pack()
        
        self.txt_log = tk.Text(f3, height=10, bg="#000000", fg="#00ff00", font=('Consolas', 9), state='disabled', borderwidth=0)
        self.txt_log.pack(fill="both", expand=True, padx=40, pady=(10, 20))
        
        btn_frame3 = ttk.Frame(f3)
        btn_frame3.pack(side="bottom", fill="x", pady=10, padx=20)
        self.btn_cancel_install = ttk.Button(btn_frame3, text="Cancel", command=self.destroy)
        self.btn_cancel_install.pack(side="right", padx=5)

        # Step 4: Finish
        f4 = ttk.Frame(self)
        self.frames["finish"] = f4
        ttk.Label(f4, text="Installation Complete!", font=('Segoe UI', 18, 'bold'), foreground="#00ff00", background=BG_COLOR).pack(pady=(40, 20))
        
        self.lbl_summary = ttk.Label(f4, text="", justify=tk.CENTER)
        self.lbl_summary.pack(pady=10)
        
        ttk.Checkbutton(f4, text="Create Desktop Shortcut", variable=self.create_shortcut).pack(pady=5)
        ttk.Checkbutton(f4, text=f"Launch {APP_NAME} now", variable=self.launch_now).pack(pady=5)
        
        btn_frame4 = ttk.Frame(f4)
        btn_frame4.pack(side="bottom", fill="x", pady=20, padx=20)
        ttk.Button(btn_frame4, text="Finish", command=self.finish_install).pack(side="right", padx=5)

    def show_frame(self, name):
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = self.frames[name]
        self.current_frame.pack(fill="both", expand=True)

    def browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.install_dir.get(), title="Select Installation Directory")
        if d:
            self.install_dir.set(os.path.normpath(d))

    def log(self, msg):
        self.after(0, self._append_log, msg)

    def _append_log(self, msg):
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')

    def set_progress(self, val, msg=None):
        self.after(0, self._set_progress, val, msg)

    def _set_progress(self, val, msg):
        self.progress_var.set(val)
        self.lbl_pct.config(text=f"{int(val)}%")
        if msg:
            self.lbl_status.config(text=msg)

    def start_installation(self):
        dest = self.install_dir.get()
        if not dest:
            messagebox.showerror("Error", "Please select an installation directory.")
            return
            
        if not check_architecture():
            if not messagebox.askyesno("Warning", "This software requires a 64-bit Windows OS. You are running 32-bit.\nProceed anyway?"):
                return
                
        if not check_internet():
            if not messagebox.askyesno("Warning", "No internet connection detected. Installation requires downloading files.\nProceed anyway?"):
                return

        if os.path.exists(dest) and os.listdir(dest):
            ans = messagebox.askyesno("Directory Exists", "The selected directory already exists and is not empty. Do you want to continue (this will overwrite files)?")
            if not ans:
                return

        self.show_frame("progress")
        self.btn_cancel_install.config(state='disabled')
        threading.Thread(target=self.install_worker, daemon=True).start()

    def install_worker(self):
        dest = self.install_dir.get()
        try:
            os.makedirs(dest, exist_ok=True)
            
            # Phase 1: Python
            self.set_progress(0, "Downloading portable Python...")
            py_dir = os.path.join(dest, ".python")
            py_zip = os.path.join(dest, "python_embed.zip")
            
            if not os.path.exists(py_dir):
                download_file(PYTHON_EMBED_ZIP, py_zip, lambda p: self.set_progress(p*0.1))
                self.set_progress(10, "Extracting Python...")
                self.log("Extracting Python to .python...")
                os.makedirs(py_dir, exist_ok=True)
                with zipfile.ZipFile(py_zip, 'r') as zip_ref:
                    zip_ref.extractall(py_dir)
                os.remove(py_zip)
                
                # Patch python311._pth
                pth_file = os.path.join(py_dir, "python311._pth")
                if os.path.exists(pth_file):
                    with open(pth_file, 'r') as f:
                        lines = f.readlines()
                    with open(pth_file, 'w') as f:
                        for line in lines:
                            if line.strip() == "#import site":
                                f.write("import site\n")
                            else:
                                f.write(line)
                                
                # Install pip
                self.set_progress(15, "Installing pip...")
                get_pip_path = os.path.join(dest, "get-pip.py")
                download_file(GET_PIP_URL, get_pip_path)
                py_exe = os.path.join(py_dir, "python.exe")
                self.run_cmd_log([py_exe, get_pip_path])
                os.remove(get_pip_path)
            else:
                self.log("Python already installed, skipping.")
                py_exe = os.path.join(py_dir, "python.exe")
            
            self.set_progress(20)

            # Phase 2: Source Code
            self.set_progress(20, "Downloading JARVIS source code...")
            src_zip = os.path.join(dest, "source.zip")
            download_file(GITHUB_REPO_ZIP, src_zip, lambda p: self.set_progress(20 + p*0.1))
            self.set_progress(30, "Extracting source code...")
            self.log("Extracting JARVIS source...")
            
            temp_extract = os.path.join(dest, "temp_src")
            os.makedirs(temp_extract, exist_ok=True)
            with zipfile.ZipFile(src_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_extract)
                
            # Find the inner folder and copy contents
            inner_folder = None
            for item in os.listdir(temp_extract):
                if os.path.isdir(os.path.join(temp_extract, item)) and not item.startswith(("__MACOSX", ".DS_Store")):
                    inner_folder = os.path.join(temp_extract, item)
                    break
                    
            if inner_folder:
                for item in os.listdir(inner_folder):
                    s = os.path.join(inner_folder, item)
                    d = os.path.join(dest, item)
                    if os.path.isdir(s):
                        if os.path.exists(d): shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
                        
            shutil.rmtree(temp_extract)
            os.remove(src_zip)
            self.set_progress(40)

            # Phase 3: Dependencies
            self.set_progress(40, "Installing dependencies...")
            req_file = os.path.join(dest, "requirements.txt")
            if os.path.exists(req_file):
                self.log("Running pip install -r requirements.txt...")
                self.run_cmd_log([py_exe, "-m", "pip", "install", "-r", req_file, "--no-warn-script-location"])
            self.set_progress(65)
            
            # Phase 4: Ollama
            self.set_progress(65, "Checking Ollama setup...")
            has_ollama = shutil.which("ollama") or os.path.exists(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"))
            if not has_ollama:
                ans = messagebox.askyesno("Ollama Required", "JARVIS requires Ollama to run local LLMs. It was not detected.\nDo you want to download and install Ollama now?")
                if ans:
                    self.set_progress(65, "Downloading Ollama...")
                    ollama_exe = os.path.join(dest, "OllamaSetup.exe")
                    download_file(OLLAMA_SETUP_URL, ollama_exe, lambda p: self.set_progress(65 + p*0.1))
                    self.set_progress(75, "Running Ollama installer...")
                    self.log("Running OllamaSetup.exe. Please follow the prompts.")
                    subprocess.run([ollama_exe], shell=False)
                    os.remove(ollama_exe)
                    self.log("Ollama installation complete.")
                    time.sleep(2) # Give it time to start
            else:
                self.log("Ollama is already installed.")
                
            # Pull models
            self.set_progress(75, "Pulling required AI models (this may take a while)...")
            ollama_cmd = "ollama"
            if not shutil.which("ollama"):
                ollama_cmd = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")
                
            if os.path.exists(ollama_cmd) or shutil.which("ollama"):
                for idx, model in enumerate(MODELS_TO_PULL):
                    self.log(f"Pulling model: {model}...")
                    self.set_progress(75 + idx*5, f"Pulling model: {model}...")
                    try:
                        self.run_cmd_log([ollama_cmd, "pull", model])
                    except Exception as e:
                        self.log(f"Warning: Failed to pull {model}: {e}")
            else:
                self.log("Warning: Cannot pull models because ollama executable wasn't found in PATH.")

            self.set_progress(85)

            # Phase 5: Shortcuts & Finalization
            self.set_progress(85, "Creating shortcuts...")
            
            # launch_jarvis.bat
            bat_path = os.path.join(dest, "launch_jarvis.bat")
            with open(bat_path, "w") as f:
                f.write('@echo off\n')
                f.write('cd /d "%~dp0"\n')
                f.write('".python\\python.exe" main.py\n')
                
            # launch_jarvis.vbs
            vbs_path = os.path.join(dest, "launch_jarvis.vbs")
            with open(vbs_path, "w") as f:
                f.write('CreateObject("Wscript.Shell").Run """" & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\\launch_jarvis.bat""", 1, False\n')

            # Create Desktop Shortcut
            if self.create_shortcut.get():
                self.create_desktop_shortcut(dest, vbs_path)
                
            # Write install_info.json
            info = {
                "version": VERSION,
                "install_time": time.time(),
                "path": dest
            }
            with open(os.path.join(dest, "install_info.json"), "w") as f:
                json.dump(info, f, indent=4)

            self.set_progress(100, "Installation complete!")
            self.after(500, self.show_finish)

        except Exception as e:
            self.log(f"\nERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            self.after(0, lambda: messagebox.showerror("Installation Failed", f"An error occurred:\n{str(e)}"))
            self.after(0, lambda: self.btn_cancel_install.config(state='normal'))

    def run_cmd_log(self, cmd):
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        for line in process.stdout:
            self.log(line.strip())
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)

    def create_desktop_shortcut(self, dest, vbs_path):
        desktop = get_desktop_path()
        if not desktop:
            self.log("Warning: Could not find Desktop path.")
            return
            
        shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")
        icon_path = os.path.join(dest, "assets", "jarvis_logo.ico")
        if not os.path.exists(icon_path):
            icon_path = "" # Fallback
            
        vbs_script = os.path.join(dest, "create_shortcut.vbs")
        with open(vbs_script, "w") as f:
            f.write(f'Set oWS = WScript.CreateObject("WScript.Shell")\n')
            f.write(f'sLinkFile = "{shortcut_path}"\n')
            f.write(f'Set oLink = oWS.CreateShortcut(sLinkFile)\n')
            f.write(f'oLink.TargetPath = "{vbs_path}"\n')
            f.write(f'oLink.WorkingDirectory = "{dest}"\n')
            f.write(f'oLink.Description = "{APP_NAME}"\n')
            if icon_path:
                f.write(f'oLink.IconLocation = "{icon_path}"\n')
            f.write(f'oLink.Save\n')
            
        subprocess.run(["cscript", "//nologo", vbs_script], creationflags=subprocess.CREATE_NO_WINDOW)
        os.remove(vbs_script)

    def show_finish(self):
        self.lbl_summary.config(text=f"JARVIS Assistant was successfully installed to:\n{self.install_dir.get()}")
        self.show_frame("finish")

    def finish_install(self):
        if self.launch_now.get():
            vbs_path = os.path.join(self.install_dir.get(), "launch_jarvis.vbs")
            if os.path.exists(vbs_path):
                subprocess.Popen(["wscript", vbs_path], cwd=self.install_dir.get())
        self.destroy()

# --- Helpers ---
def download_file(url, dest, progress_cb=None):
    for attempt in range(3):
        try:
            def reporthook(blocknum, blocksize, totalsize):
                if progress_cb and totalsize > 0:
                    percent = min((blocknum * blocksize * 100) / totalsize, 100)
                    progress_cb(percent)
            urllib.request.urlretrieve(url, dest, reporthook)
            return True
        except Exception as e:
            if attempt == 2:
                raise Exception(f"Failed to download {url}: {e}")
            time.sleep(2)

def check_architecture():
    return struct.calcsize("P") * 8 == 64

def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def get_desktop_path():
    try:
        cmd = ["powershell", "-NoProfile", "-Command", "[Environment]::GetFolderPath('Desktop')"]
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        path = result.stdout.strip()
        if os.path.exists(path):
            return path
    except:
        pass
    return os.path.join(os.path.expanduser('~'), 'Desktop')

if __name__ == "__main__":
    app = InstallerGUI()
    app.mainloop()
