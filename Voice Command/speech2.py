import sys
import os
import sounddevice as sd
from scipy.io.wavfile import write
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
)
from datetime import datetime
import numpy as np

class VoiceCommandApp(QWidget):
    def __init__(self):
        super().__init__()
        self.language = None
        self.user_name = None
        self.command_name = None
        self.recording = False
        self.recorded_data = []
        self.samplerate = 44100  # Sample rate
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Voice Command Data Collector")
        self.setGeometry(100, 100, 400, 300)

        # Layouts
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Language Selection
        self.language_label = QLabel("Türkçe mi İngilizce mi?")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Türkçe", "English"])
        self.language_button = QPushButton("Seç")
        self.language_button.clicked.connect(self.select_language)

        # User Input for Command Name and Username
        self.user_label = QLabel("Adınızı girin:")
        self.user_input = QLineEdit()
        self.command_label = QLabel("Komut adını girin:")
        self.command_input = QLineEdit()

        # Record Button
        self.record_button = QPushButton("Kaydı Başlat")
        self.record_button.setEnabled(False)
        self.record_button.clicked.connect(self.toggle_recording)

        # Status Label
        self.status_label = QLabel("")  # Boş başlayacak, durum değiştikçe güncellenecek

        # Add Widgets to Layout
        self.layout.addWidget(self.language_label)
        self.layout.addWidget(self.language_combo)
        self.layout.addWidget(self.language_button)
        self.layout.addWidget(self.user_label)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(self.command_label)
        self.layout.addWidget(self.command_input)
        self.layout.addWidget(self.record_button)
        self.layout.addWidget(self.status_label)

    def select_language(self):
        self.language = self.language_combo.currentText()
        self.status_label.setText(f"Dil seçildi: {self.language}")
        self.record_button.setEnabled(True)

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.user_name = self.user_input.text().strip()
        self.command_name = self.command_input.text().strip()

        if not self.user_name or not self.command_name:
            self.status_label.setText("Lütfen adınızı ve komut adını giriniz.")
            return

        self.recording = True
        self.recorded_data = []  # Clear previous recordings
        self.record_button.setText("Kaydı Durdur")
        self.status_label.setText("Kayıt başladı, konuşabilirsiniz.")
        # Start streaming audio
        self.stream = sd.InputStream(
            samplerate=self.samplerate, channels=1, callback=self.audio_callback
        )
        self.stream.start()

    def stop_recording(self):
        self.recording = False
        self.stream.stop()
        self.stream.close()
        self.record_button.setText("Kaydı Başlat")
        self.status_label.setText("Kayıt durduruldu ve kaydediliyor.")

        # Create Folder Structure
        base_folder = "VoiceCommands"
        os.makedirs(base_folder, exist_ok=True)
        language_folder = os.path.join(base_folder, self.language)
        os.makedirs(language_folder, exist_ok=True)
        command_folder = os.path.join(language_folder, self.command_name)
        os.makedirs(command_folder, exist_ok=True)

        # File Path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{self.user_name}_{timestamp}.wav"
        file_path = os.path.join(command_folder, file_name)

        # Save the recording to a WAV file
        recorded_array = np.concatenate(self.recorded_data, axis=0)
        write(file_path, self.samplerate, recorded_array)
        self.status_label.setText(f"Kayıt tamamlandı: {file_path}")

    def audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.recorded_data.append(indata.copy())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceCommandApp()
    window.show()
    sys.exit(app.exec_())
