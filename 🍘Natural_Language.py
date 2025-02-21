import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import csv

class IntegratedWaveformTool:
    """
    A tool that loads a WAV file, lets the user draw custom envelopes for positive and negative
    parts of the waveform, and then applies the drawing to modify the waveform's peaks.
    """
    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.sample_rate, self.audio_data = wavfile.read(audio_file)

        # Convert stereo to mono if needed.
        if len(self.audio_data.shape) == 2:  # If stereo (2D array)
            self.audio_data = np.mean(self.audio_data, axis=1)
        
        # Normalize waveform.
        self.audio_data = self.audio_data / np.max(np.abs(self.audio_data))
        self.num_samples = len(self.audio_data)
        self.max_amplitude = np.max(np.abs(self.audio_data))

        # Extract filename without extension.
        self.base_name = os.path.splitext(os.path.basename(audio_file))[0]

        # Create a new folder to store outputs.
        self.output_folder = f"future_{self.base_name}"
        os.makedirs(self.output_folder, exist_ok=True)

        # Move the original audio file to the new folder.
        shutil.move(self.audio_file, os.path.join(self.output_folder, os.path.basename(self.audio_file)))
        
        # Set up the plot.
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Draw Your Custom Envelope")
        self.ax.set_xlabel("Sample Index")
        self.ax.set_ylabel("Amplitude")
        # Set fixed limits to avoid distortion when resizing.
        self.expected_xlim = (0, self.num_samples)
        self.expected_ylim = (-self.max_amplitude, self.max_amplitude)
        self.ax.set_xlim(*self.expected_xlim)
        self.ax.set_ylim(*self.expected_ylim)
        self.ax.set_aspect('auto')

        # Create empty line objects for positive (blue) and negative (red) drawings.
        self.line_pos, = self.ax.plot([], [], color='blue', lw=2, label='Positive Envelope')
        self.line_neg, = self.ax.plot([], [], color='red', lw=2, label='Negative Envelope')
        self.ax.legend()

        # Connect mouse event handlers.
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        # Connect a resize event to reset axis limits and background.
        self.cid_resize = self.fig.canvas.mpl_connect('resize_event', self.on_resize)

        # Drawing state variables.
        self.is_drawing = False
        self.drawing_pos = np.zeros(self.num_samples)
        self.drawing_neg = np.zeros(self.num_samples)
        self.prev_idx = None  

        # Variable to store the canvas background for blitting.
        self.background = None

    def on_resize(self, event):
        """Reset the axis limits and clear the cached background on resize."""
        self.ax.set_xlim(*self.expected_xlim)
        self.ax.set_ylim(*self.expected_ylim)
        self.background = None  # Invalidate cached background.

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
        """Update the drawn envelope based on mouse position using linear interpolation and blitting."""
        idx = int(event.xdata)
        if 0 <= idx < self.num_samples:
            if event.ydata > 0:
                if self.prev_idx is not None and idx > self.prev_idx:
                    self.drawing_pos[self.prev_idx:idx + 1] = np.linspace(
                        self.drawing_pos[self.prev_idx], event.ydata, idx - self.prev_idx + 1)
                else:
                    self.drawing_pos[idx] = event.ydata
                self.line_pos.set_data(np.arange(self.num_samples), self.drawing_pos)
            elif event.ydata < 0:
                if self.prev_idx is not None and idx > self.prev_idx:
                    self.drawing_neg[self.prev_idx:idx + 1] = np.linspace(
                        self.drawing_neg[self.prev_idx], event.ydata, idx - self.prev_idx + 1)
                else:
                    self.drawing_neg[idx] = event.ydata
                self.line_neg.set_data(np.arange(self.num_samples), self.drawing_neg)
            self.prev_idx = idx

            # --- Blitting update ---
            if self.background is None:
                # Cache the current background (everything except animated artists).
                self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
            else:
                self.fig.canvas.restore_region(self.background)
            # Draw only the updated artists.
            self.ax.draw_artist(self.line_pos)
            self.ax.draw_artist(self.line_neg)
            self.fig.canvas.blit(self.ax.bbox)
            # --------------------------------

    def save_drawing(self):
        """Reset axes to original limits and save the current drawing as a PNG."""
        self.ax.set_xlim(*self.expected_xlim)
        self.ax.set_ylim(*self.expected_ylim)
        output_png = os.path.join(self.output_folder, f"future_{self.base_name}.png")
        self.fig.savefig(output_png)
        print(f"Saved drawing as {output_png}")

    def save_to_csv(self):
        """Save the drawn envelope data (both positive and negative) to a CSV file."""
        output_csv = os.path.join(self.output_folder, f"future_{self.base_name}.csv")
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Index', 'Positive Amplitude', 'Negative Amplitude'])
            for i in range(self.num_samples):
                writer.writerow([i, self.drawing_pos[i], self.drawing_neg[i]])
        print(f"Saved CSV as {output_csv}")

    def apply_drawing_to_waveform(self):
        """Apply the drawn envelopes to the original waveform and save the adjusted audio."""
        self.save_to_csv()
        adjusted_audio_data = np.zeros_like(self.audio_data)

        # Apply drawn envelope to positive and negative parts.
        for i in range(len(self.audio_data)):
            if self.audio_data[i] > 0:
                adjusted_audio_data[i] = self.drawing_pos[i]
            elif self.audio_data[i] < 0:
                adjusted_audio_data[i] = self.drawing_neg[i]
            else:
                adjusted_audio_data[i] = self.audio_data[i]

        output_wav = os.path.join(self.output_folder, f"future_{self.base_name}.wav")
        # Scale back to int16 range.
        wavfile.write(output_wav, self.sample_rate, (adjusted_audio_data * 32767).astype(np.int16))
        print(f"Saved adjusted audio as {output_wav}")

        # Plot original vs. adjusted waveform for comparison.
        plt.figure(figsize=(10, 6))
        plt.subplot(2, 1, 1)
        plt.plot(self.audio_data, color='blue')
        plt.title('Original Audio Waveform')
        plt.subplot(2, 1, 2)
        plt.plot(adjusted_audio_data, color='green')
        plt.title('Adjusted Audio Waveform')
        plt.tight_layout()
        plt.show()

def process_file():
    audio_file = input("Enter the path to your audio file: ")
    if not os.path.exists(audio_file):
        print("File not found!")
        return
    waveform_tool = IntegratedWaveformTool(audio_file)
    # Display the drawing canvas (the user can draw on the pop-up window).
    plt.show()
    # After closing the plot window, save outputs.
    waveform_tool.save_drawing()
    waveform_tool.apply_drawing_to_waveform()

def main():
    while True:
        process_file()
        cont = input("Process another file? (y/n): ")
        if cont.lower() != 'y':
            break

if __name__ == '__main__':
    main()
