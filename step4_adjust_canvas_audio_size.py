import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

class SimpleDrawTool:
    def __init__(self, audio_file):
        # Read the audio file
        self.sample_rate, self.audio_data = wavfile.read(audio_file)
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
        self.ax.set_xlim(0, self.num_samples)  # x-axis range based on number of samples
        self.is_drawing = False
        self.drawing_pos = np.zeros(self.num_samples)  # Blank canvas for positive area
        self.drawing_neg = np.zeros(self.num_samples)  # Blank canvas for negative area
        self.prev_idx = None  # To store the previous index for continuous line
        plt.show()

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
                    # Create a continuous line between the previous point and the current point
                    self.drawing_pos[self.prev_idx:idx + 1] = np.linspace(self.drawing_pos[self.prev_idx], event.ydata, idx - self.prev_idx + 1)
                self.drawing_pos[idx] = event.ydata
                self.line_pos.set_data(np.arange(len(self.drawing_pos)), self.drawing_pos)
            elif event.ydata < 0:
                if self.prev_idx is not None:
                    # Create a continuous line between the previous point and the current point
                    self.drawing_neg[self.prev_idx:idx + 1] = np.linspace(self.drawing_neg[self.prev_idx], event.ydata, idx - self.prev_idx + 1)
                self.drawing_neg[idx] = event.ydata
                self.line_neg.set_data(np.arange(len(self.drawing_neg)), self.drawing_neg)
            self.prev_idx = idx
            self.fig.canvas.draw()

# Example usage
SimpleDrawTool('elephant-225994.wav')
