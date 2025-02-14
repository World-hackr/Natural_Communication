import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import csv
from pydub import AudioSegment

class IntegratedWaveformTool:
    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.base_name = os.path.splitext(os.path.basename(audio_file))[0]  # Extract filename without extension
        self.folder_name = f"future_{self.base_name}"  # Create folder name
        os.makedirs(self.folder_name, exist_ok=True)  # Create the folder
        
        # Convert MP3 to WAV if needed
        if audio_file.lower().endswith(".mp3"):
            wav_path = os.path.join(self.folder_name, f"{self.base_name}.wav")
            AudioSegment.from_mp3(audio_file).export(wav_path, format="wav")
            self.audio_file = wav_path

        self.sample_rate, self.audio_data = wavfile.read(self.audio_file)
        self.audio_data = self.audio_data / np.max(np.abs(self.audio_data))
        self.num_samples = len(self.audio_data)
        self.max_amplitude = np.max(np.abs(self.audio_data))

        # Set up the plot
        self.fig, self.ax = plt.subplots()
        self.line_pos, = self.ax.plot([], [], color='blue')
        self.line_neg, = self.ax.plot([], [], color='red')
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.ax.set_ylim(-self.max_amplitude, self.max_amplitude)
        self.ax.set_xlim(0, self.num_samples)
        self.is_drawing = False
        self.drawing_pos = np.zeros(self.num_samples)
        self.drawing_neg = np.zeros(self.num_samples)
        self.prev_idx = None  

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        self.is_drawing = True
        self.prev_idx = int(event.xdata)
        self.update_drawing(event)

    def on_hover(self, event):
        if self.is_drawing and event.inaxes == self.ax:
            self.update_drawing(event)

    def on_release(self, event):
        self.is_drawing = False
        self.prev_idx = None

    def update_drawing(self, event):
        idx = int(event.xdata)
        if 0 <= idx < len(self.drawing_pos):
            if event.ydata > 0:
                if self.prev_idx is not None:
                    self.drawing_pos[self.prev_idx:idx + 1] = np.linspace(self.drawing_pos[self.prev_idx], event.ydata, idx - self.prev_idx + 1)
                self.drawing_pos[idx] = event.ydata
                self.line_pos.set_data(np.arange(len(self.drawing_pos)), self.drawing_pos)
            elif event.ydata < 0:
                if self.prev_idx is not None:
                    self.drawing_neg[self.prev_idx:idx + 1] = np.linspace(self.drawing_neg[self.prev_idx], event.ydata, idx - self.prev_idx + 1)
                self.drawing_neg[idx] = event.ydata
                self.line_neg.set_data(np.arange(len(self.drawing_neg)), self.drawing_neg)
            self.prev_idx = idx
            self.fig.canvas.draw()

    def save_drawing(self):
        output_png = os.path.join(self.folder_name, f"{self.base_name}.png")
        self.fig.savefig(output_png)
        print(f"Saved drawing as {output_png}")

    def save_to_csv(self):
        output_csv = os.path.join(self.folder_name, f"{self.base_name}.csv")
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Index', 'Positive Amplitude', 'Negative Amplitude'])
            for i in range(self.num_samples):
                writer.writerow([i, self.drawing_pos[i], self.drawing_neg[i]])
        print(f"Saved CSV as {output_csv}")

    def apply_drawing_to_waveform(self):
        self.save_to_csv()
        adjusted_audio_data = np.zeros_like(self.audio_data)

        for i in range(len(self.audio_data)):
            if self.audio_data[i] > 0:
                adjusted_audio_data[i] = self.drawing_pos[i]
            elif self.audio_data[i] < 0:
                adjusted_audio_data[i] = self.drawing_neg[i]
            else:
                adjusted_audio_data[i] = self.audio_data[i]

        output_wav = os.path.join(self.folder_name, f"{self.base_name}.wav")
        output_mp3 = os.path.join(self.folder_name, f"{self.base_name}.mp3")

        # Save as WAV
        wavfile.write(output_wav, self.sample_rate, (adjusted_audio_data * 32767).astype(np.int16))
        print(f"Saved adjusted audio as {output_wav}")

        # Convert back to MP3 if original was MP3
        if self.audio_file.lower().endswith(".wav") and "mp3" in audio_file.lower():
            audio = AudioSegment.from_wav(output_wav)
            audio.export(output_mp3, format="mp3")
            print(f"Saved adjusted audio as {output_mp3}")

        # Plot original vs adjusted waveform
        plt.figure(figsize=(10, 6))
        plt.subplot(2, 1, 1)
        plt.plot(self.audio_data, color='blue')
        plt.title('Original Audio Waveform')
        plt.subplot(2, 1, 2)
        plt.plot(adjusted_audio_data, color='green')
        plt.title('Adjusted Audio Waveform')
        plt.tight_layout()
        plt.show()

# Ask user for the audio file path
audio_file = input("Enter the path to your audio file: ")

# Create the waveform tool
waveform_tool = IntegratedWaveformTool(audio_file)

# Show the drawing canvas
plt.show()

# After closing the plot, save outputs
waveform_tool.save_drawing()
waveform_tool.apply_drawing_to_waveform()
