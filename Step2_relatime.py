import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

class InteractiveWaveform:
    def __init__(self, audio_file):
        # Read the audio file
        self.sample_rate, self.audio_data = wavfile.read(audio_file)
        self.audio_data = self.audio_data / np.max(np.abs(self.audio_data))
        
        # Set up the plot
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(self.audio_data, color='blue')
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, len(self.audio_data))
        self.is_clicked = False
        plt.show()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        self.is_clicked = not self.is_clicked
        self.update_waveform(event)

    def on_hover(self, event):
        if self.is_clicked and event.inaxes == self.ax:
            self.update_waveform(event)

    def update_waveform(self, event):
        idx = int(event.xdata)
        range_width = 10  # Number of points to adjust around the cursor
        if 0 <= idx < len(self.audio_data):
            for i in range(max(0, idx - range_width), min(len(self.audio_data), idx + range_width)):
                if (self.audio_data[i] > 0 and event.ydata > 0) or (self.audio_data[i] < 0 and event.ydata < 0):
                    self.audio_data[i] = event.ydata
            self.line.set_ydata(self.audio_data)
            self.fig.canvas.draw()

    def save_audio(self, output_file):
        wavfile.write(output_file, self.sample_rate, (self.audio_data * 32767).astype(np.int16))

# Example usage
interactive_waveform = InteractiveWaveform('elephant-225994.wav')
# After adjusting the waveform, call the save_audio method to save the modified audio
# interactive_waveform.save_audio('output_audio.wav')
