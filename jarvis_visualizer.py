import sys
import time
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QRectF, Qt
from PyQt6.QtGui import QPainter, QColor, QBrush

class AudioVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        
        # --- Configuration ---
        self.BAR_COUNT = 40       # Total bars (Keep it even for symmetry)
        self.BAR_WIDTH = 6        
        self.BAR_SPACING = 2      
        self.COLOR_ACCENT = "#00e5ff" 
        
        # Settings
        self.DECAY = 0.5          
        self.GAIN = 20.0          # Sensitivity
        self.NOISE_FLOOR = 0.05   
        self.IDLE_TIMEOUT = 10    # Wait time before idle animation
        
        # Data containers
        self.amplitudes = np.zeros(self.BAR_COUNT) 
        self.phase = 0 
        self.last_sound_time = time.time()
        
        # Audio Stream
        self.stream = None
        self.is_listening = False
        
        # Start
        self.init_audio_stream()

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui) 
        self.timer.start(16) 

    def init_audio_stream(self):
        try:
            self.stream = sd.InputStream(
                channels=1,
                samplerate=44100,
                blocksize=1024,
                callback=self.audio_callback
            )
            self.stream.start()
            self.is_listening = True
            self.last_sound_time = time.time()
        except Exception as e:
            print(f"⚠️ AUDIO ERROR: {e}")
            self.is_listening = False

    def audio_callback(self, indata, frames, t, status):
        if not self.is_listening: return

        try:
            audio_data = indata[:, 0]
            
            # Check volume for idle timer
            if np.linalg.norm(audio_data) * 10 > self.NOISE_FLOOR:
                self.last_sound_time = time.time()

            fft_data = np.abs(np.fft.rfft(audio_data))
            
            # --- MIRROR LOGIC START ---
            # We only calculate HALF the bars
            half_count = self.BAR_COUNT // 2
            chunk_size = len(fft_data) // half_count
            
            half_amplitudes = []
            
            for i in range(half_count):
                start = i * chunk_size
                end = start + chunk_size
                if end > len(fft_data): end = len(fft_data)
                
                avg_val = np.mean(fft_data[start:end])
                half_amplitudes.append(avg_val)
            
            # Prepare the mirrored array
            half_array = np.array(half_amplitudes) * self.GAIN
            half_array = np.clip(half_array, 0, 1)
            
            # Construct full array: [Reversed Left] + [Normal Right]
            # FFT is [Low -> High]. 
            # We want Center to be Low.
            # So Left side = High->Low (Reversed FFT)
            # Right side = Low->High (Normal FFT)
            
            full_array = np.concatenate((half_array[::-1], half_array))
            
            # Apply Decay
            self.amplitudes = self.amplitudes * self.DECAY + full_array * (1 - self.DECAY)
            # --- MIRROR LOGIC END ---
            
        except Exception as e:
            print(f"Stream Error: {e}")

    def update_gui(self):
        self.phase += 0.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        total_width = self.BAR_COUNT * (self.BAR_WIDTH + self.BAR_SPACING)
        start_x = (w - total_width) / 2
        
        brush = QBrush(QColor(self.COLOR_ACCENT))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)

        # Check Idle Mode
        is_idle_mode = (time.time() - self.last_sound_time) > self.IDLE_TIMEOUT

        for i, val in enumerate(self.amplitudes):
            
            if is_idle_mode or not self.is_listening:
                # Mirrored Sine Wave for Idle
                # We calculate sine based on distance from center
                center = self.BAR_COUNT / 2
                dist = abs(i - center)
                val = 0.05 + (np.sin(dist * 0.2 - self.phase) * 0.04)
                # Keep it positive
                if val < 0: val = 0.01

            else:
                # Active Mode cleanup
                if val < 0.02: val = 0.01 
            
            # Draw
            bar_height = val * h
            x = start_x + i * (self.BAR_WIDTH + self.BAR_SPACING)
            y = (h - bar_height) / 2 
            
            rect = QRectF(x, y, self.BAR_WIDTH, bar_height)
            painter.drawRoundedRect(rect, 2, 2)
            
        painter.end()

    def closeEvent(self, event):
        if self.stream:
            self.stream.stop()
            self.stream.close()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = AudioVisualizer()
    window.resize(800, 300)
    window.show()
    sys.exit(app.exec())