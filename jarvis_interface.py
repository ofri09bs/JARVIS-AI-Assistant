import sys
import psutil
import datetime
import threading
import queue
import os
import requests

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QProgressBar, QTextEdit, QLineEdit, QFrame,
                             QSizePolicy, QMessageBox)
from PyQt6.QtCore import QTimer, Qt, QRectF, QSize
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap, QPalette, QBrush
from PyQt6.QtWidgets import QPushButton

import jarvis_brain
import jarvis_visualizer
import jarvis_voice

# --- GLOBAL CONFIGURATION ---
COLOR_BG_TRANSPARENT = QColor(5, 10, 14, 200)
COLOR_PANEL_TRANSPARENT = QColor(13, 22, 29, 180)
COLOR_ACCENT = "#00e5ff"
COLOR_TEXT = "#ffffff"
is_voice_mode_active = False

BG_IMAGE_PATH = "ironman_bg.jpg" 

STYLESHEET = f"""
    QWidget {{
        color: {COLOR_TEXT};
        font-family: 'Segoe UI', sans-serif;
    }}
    QWidget#CentralWidget {{
        background-color: transparent;
    }}
    QFrame#Panel {{
        background-color: rgba(13, 22, 29, 180);
        border: 1px solid #1a262f;
        border-radius: 8px;
        border-top: 2px solid #005f73;
    }}
    QFrame#Panel:hover {{
        border-top: 2px solid {COLOR_ACCENT};
    }}
    QLabel#Title {{
        color: {COLOR_ACCENT};
        font-weight: bold;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        background-color: transparent;
    }}
    QLabel#Value {{
        font-size: 20px;
        font-weight: bold;
        color: white;
        background-color: transparent;
    }}
    QLabel#SubDetail {{
        font-size: 10px;
        color: #7f8c8d;
        background-color: transparent;
    }}
    QProgressBar {{
        border: 1px solid #1a262f;
        background-color: rgba(5, 10, 14, 150);
        height: 6px;
        border-radius: 3px;
    }}
    QProgressBar::chunk {{
        background-color: {COLOR_ACCENT};
    }}
    QLineEdit {{
        background-color: rgba(8, 16, 24, 200);
        border: 1px solid #2c3e50;
        color: {COLOR_ACCENT};
        padding: 8px;
        border-radius: 4px;
    }}
    QTextEdit {{
        background-color: rgba(8, 16, 24, 200);
        border: none;
        color: #cfd8dc;
        font-family: 'Consolas', monospace;
        font-size: 12px;
    }}
    QLabel#TimeLabel {{
        font-size: 38px; font-weight: bold; color: white; font-family: 'Consolas';
        background-color: transparent;
    }}
"""

ui_components = {}
rotation_angle = 0
msg_queue = queue.Queue()
bg_pixmap = None

# --- MAIN WINDOW CLASS ---
class JarvisMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S MK.42 INTERFACE")
        self.resize(1280, 720)
        self.setObjectName("CentralWidget")
        
        global bg_pixmap
        if os.path.exists(BG_IMAGE_PATH):
            bg_pixmap = QPixmap(BG_IMAGE_PATH)
        else:
             QMessageBox.critical(self, "Error", f"Image '{BG_IMAGE_PATH}' not found!")
             sys.exit(1)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(30)

    def update_animation(self):
        global rotation_angle
        rotation_angle = (rotation_angle + 3) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 1. Background Image
        if bg_pixmap:
            scaled_bg = bg_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled_bg.width()) // 2
            y = (self.height() - scaled_bg.height()) // 2
            painter.drawPixmap(x, y, scaled_bg)

        # 2. Draw the Arc Reactor
        cx = (self.width() / 2) + 8.9
        
        cy = self.height() * 0.765
        
        reactor_size = self.height() * 0.08 

        painter.translate(cx, cy)
        painter.rotate(rotation_angle)
        
        # Glow Rings
        pen = QPen(QColor(COLOR_ACCENT))
        pen.setWidth(int(reactor_size * 0.08)) 
        painter.setPen(pen)
        
        r_outer = reactor_size
        r_inner = reactor_size * 0.70
        
        rect_outer = QRectF(-r_outer, -r_outer, r_outer*2, r_outer*2)
        painter.drawArc(rect_outer, rotation_angle * 2, 100 * 16)
        painter.drawArc(rect_outer, (rotation_angle + 180) * 2, 100 * 16)
        
        rect_inner = QRectF(-r_inner, -r_inner, r_inner*2, r_inner*2)
        painter.drawArc(rect_inner, -rotation_angle * 3, 120 * 16)
        painter.drawArc(rect_inner, -(rotation_angle + 180) * 3, 120 * 16)
        
        # Core
        painter.rotate(-rotation_angle * 2.5)
        pen_core = QPen(QColor("white"), int(reactor_size * 0.1))
        painter.setPen(pen_core)
        painter.setBrush(QColor(COLOR_ACCENT))
        r_core = reactor_size * 0.3
        painter.drawEllipse(int(-r_core), int(-r_core), int(r_core*2), int(r_core*2))

        painter.end()

# --- LOGIC ---

def run_brain_task(user_text):
    response = jarvis_brain.process_user_input(user_text)
    msg_queue.put(("JARVIS", response))
    threading.Thread(target=jarvis_voice.speak, args=(response,), daemon=True).start()

def check_message_queue():
    try:
        message_data = msg_queue.get_nowait()
        
        if isinstance(message_data, str):
            sender, text = "JARVIS", message_data
        else:
            sender, text = message_data 

        chat_box = ui_components['chat']
        
        if sender == "USER":
            timestamp = datetime.datetime.now().strftime("[%H:%M]")
            chat_box.append(f"<span style='color: #7f8c8d;'>{timestamp} USER:</span> {text}")
        else:
            chat_box.append(f"<span style='color: {COLOR_ACCENT};'>➜ JARVIS:</span> {text}\n")
            
        sb = chat_box.verticalScrollBar()
        sb.setValue(sb.maximum())
        
    except queue.Empty:
        pass

def toggle_voice_mode():
    global is_voice_mode_active
    
    # Toggle the state
    is_voice_mode_active = not is_voice_mode_active
    
    # Update UI Button visual state
    btn = ui_components['mic_btn']
    if is_voice_mode_active:
        btn.setStyleSheet(f"background-color: {COLOR_ACCENT}; color: black; border-radius: 20px; font-weight: bold;")
        # Start the loop in a thread
        threading.Thread(target=voice_loop_task, daemon=True).start()
    else:
        btn.setStyleSheet(f"background-color: {COLOR_PANEL_TRANSPARENT.name()}; color: {COLOR_ACCENT}; border: 1px solid {COLOR_ACCENT}; border-radius: 20px;")

def voice_loop_task():
    global is_voice_mode_active
    
    while is_voice_mode_active:
        user_text = jarvis_voice.listen_dynamic()
        
        if user_text:
            ui_components['input'].setText(user_text)
            
            # 1.send user text to chat display
            msg_queue.put(("USER", user_text)) 
            
            # 2. Process in brain
            response = jarvis_brain.process_user_input(user_text)
            
            # 3. Send JARVIS response to chat display
            msg_queue.put(("JARVIS", response))
            
            # 4. Speak response
            jarvis_voice.speak(response)
            
            # Clear input field
            ui_components['input'].clear()
            
        if not is_voice_mode_active:
            break


def get_current_temperature(lat=32.72, lon=35.29, callback=None):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=5).json()
        temp = response.get("current_weather", {}).get("temperature", "N/A")
        if callback:
            callback(temp)
    except Exception as e:
        print(f"[Weather Error]: {e}")
        if callback:
            callback("N/A")

def weather_callback(data):
    if data != "N/A":
        ui_components['weather_val'].setText(f"{data}°C")
    else:
        ui_components['weather_val'].setText("N/A")

threading.Thread(target=get_current_temperature, args=(32.72, 35.29, weather_callback), daemon=True).start()

def update_system_stats():
    cpu = psutil.cpu_percent()
    ui_components['cpu_val'].setText(f"{cpu}%")
    ui_components['cpu_bar'].setValue(int(cpu))
    ram = psutil.virtual_memory().percent
    ui_components['ram_val'].setText(f"{ram}%")
    ui_components['ram_bar'].setValue(int(ram))
    hdd = psutil.disk_usage('/')
    free_gb = hdd.free / (1024**3)
    percent = hdd.percent
    ui_components['disk_val'].setText(f"{int(free_gb)} GB Free")
    ui_components['disk_bar'].setValue(int(percent))
    now = datetime.datetime.now()
    ui_components['time_lbl'].setText(now.strftime("%H:%M:%S"))

def handle_user_input():
    input_field = ui_components['input']
    chat_box = ui_components['chat']
    text = input_field.text()
    if not text: return
    timestamp = datetime.datetime.now().strftime("[%H:%M]")
    chat_box.append(f"<span style='color: #7f8c8d;'>{timestamp} USER:</span> {text}")
    input_field.clear()
    threading.Thread(target=run_brain_task, args=(text,), daemon=True).start()

def create_stat_panel(title, initial_value, sub_text=""):
    panel = QFrame()
    panel.setObjectName("Panel")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(15, 12, 15, 12)
    layout.setSpacing(5)
    lbl_title = QLabel(title); lbl_title.setObjectName("Title"); layout.addWidget(lbl_title)
    lbl_value = QLabel(initial_value); lbl_value.setObjectName("Value"); layout.addWidget(lbl_value)
    if sub_text:
        lbl_sub = QLabel(sub_text); lbl_sub.setObjectName("SubDetail"); layout.addWidget(lbl_sub)
        return panel, lbl_value, None
    pbar = QProgressBar(); pbar.setTextVisible(False); pbar.setValue(0); layout.addWidget(pbar)
    return panel, lbl_value, pbar

# --- MAIN ---

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    
    window = JarvisMainWindow()
    
    # --- Main Layout (3 Columns) ---
    main_layout = QHBoxLayout(window)
    main_layout.setSpacing(10)
    main_layout.setContentsMargins(25, 25, 25, 25)
    
    # === LEFT COLUMN (Stats) ===
    col_left = QVBoxLayout()
    lbl_time = QLabel("00:00:00"); lbl_time.setObjectName("TimeLabel")
    col_left.addWidget(lbl_time); ui_components['time_lbl'] = lbl_time
    col_left.addSpacing(20)
    
    panel_cpu, lbl_cpu, bar_cpu = create_stat_panel("CPU LOAD", "0%")
    panel_ram, lbl_ram, bar_ram = create_stat_panel("RAM", "0%")
    panel_disk, lbl_disk, bar_disk = create_stat_panel("STORAGE SPACE", "Calculating...")
    panel_weather, lbl_weather, _ = create_stat_panel("LOCAL WEATHER", "Loading...", "Humidity: 65% | Wind: 12km/h")
    ui_components['weather_val'] = lbl_weather
    
    col_left.addWidget(panel_cpu); col_left.addWidget(panel_ram); col_left.addWidget(panel_disk); col_left.addWidget(panel_weather)
    col_left.addStretch()
    
    ui_components['cpu_val'] = lbl_cpu; ui_components['cpu_bar'] = bar_cpu
    ui_components['ram_val'] = lbl_ram; ui_components['ram_bar'] = bar_ram
    ui_components['disk_val'] = lbl_disk; ui_components['disk_bar'] = bar_disk

    # === CENTER COLUMN (Arc Reactor + Visualizer) ===
    col_center = QVBoxLayout()
    col_center.addStretch(5)
    
    visualizer = jarvis_visualizer.AudioVisualizer()
    col_center.addWidget(visualizer) 
    col_center.addSpacing(10) 
   # === RIGHT COLUMN (Chat and mic) ===
    col_right = QVBoxLayout()
    panel_chat = QFrame(); panel_chat.setObjectName("Panel")
    chat_layout = QVBoxLayout(panel_chat)
    
    # 1. Title
    lbl_chat = QLabel("SECURE LINK"); lbl_chat.setObjectName("Title"); chat_layout.addWidget(lbl_chat)
    
    chat_box = QTextEdit(); chat_box.setReadOnly(True); 
    chat_layout.addWidget(chat_box, 1) 
    
    # --- Input Area Layout (Row) ---
    input_layout = QHBoxLayout()
    
    # 3. Input field
    input_field = QLineEdit()
    input_field.setPlaceholderText("Execute command protocol...")
    input_field.setMinimumHeight(40) 
    input_field.returnPressed.connect(handle_user_input)
    
    # 4. Microphone button
    from PyQt6.QtWidgets import QPushButton
    btn_mic = QPushButton("🎤")
    btn_mic.setFixedSize(40, 40)
    btn_mic.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_mic.setStyleSheet(f"""
        QPushButton {{
            background-color: {COLOR_PANEL_TRANSPARENT.name()};
            color: {COLOR_ACCENT};
            border: 1px solid {COLOR_ACCENT};
            border-radius: 20px;
            font-size: 16px;
        }}
    """)
    # Connecting to the toggle function
    btn_mic.clicked.connect(toggle_voice_mode) 
    
    input_layout.addWidget(input_field) 
    input_layout.addWidget(btn_mic)
    
    # Adding the input row to the bottom of the panel
    chat_layout.addLayout(input_layout) 
    
    # Finishing and adding to the main panel
    col_right.addWidget(panel_chat)
    
    # saving UI components for later use
    ui_components['chat'] = chat_box
    ui_components['input'] = input_field
    ui_components['mic_btn'] = btn_mic

    # --- Add Columns to Main Layout ---
    main_layout.addLayout(col_left, 1)   # Left (25%)
    main_layout.addLayout(col_center, 2) # Center (50%) - Invisible layout for visualizer
    main_layout.addLayout(col_right, 1)  # Right (25%)

    # --- Timers ---
    t_stats = QTimer(window)
    t_stats.timeout.connect(update_system_stats)
    t_stats.start(1000)
    
    t_brain = QTimer(window)
    t_brain.timeout.connect(check_message_queue)
    t_brain.start(100)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()