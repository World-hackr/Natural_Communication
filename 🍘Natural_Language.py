import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import csv
import sounddevice as sd  # For real-time audio preview

class IntegratedWaveformTool:
    """
    A tool that:
      - Loads a WAV file (stereo -> mono, normalized).
      - Lets you draw envelopes for positive and negative parts of the waveform separately.
      - Uses your original per-sample logic (no smoothing).
      - Offers real-time audio preview, undo/reset, partial redraw, and background waveform.
      - Optionally clamps drawn amplitudes to [-1,1].
      - Now saves two PNG files:
          1) The drawn envelope.
          2) A comparison of original vs. adjusted waveforms.
    """
    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.sample_rate, self.audio_data = wavfile.read(audio_file)

        # Convert stereo to mono if needed.
        if len(self.audio_data.shape) == 2:
            self.audio_data = np.mean(self.audio_data, axis=1)

        # Normalize waveform to [-1, 1].
        self.audio_data = self.audio_data / np.max(np.abs(self.audio_data))
        self.num_samples = len(self.audio_data)
        self.max_amplitude = np.max(np.abs(self.audio_data))

        # Prepare output folder.
        self.base_name = os.path.splitext(os.path.basename(audio_file))[0]
        self.output_folder = f"future_{self.base_name}"
        os.makedirs(self.output_folder, exist_ok=True)

        # Copy (not move) the original file for safety.
        shutil.copy(self.audio_file, os.path.join(self.output_folder, os.path.basename(self.audio_file)))

        # Set up figure and axes for drawing.
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Draw Envelope (Keys: 'r' Reset, 'u' Undo, 'p' Preview)")
        self.ax.set_xlabel("Sample Index")
        self.ax.set_ylabel("Amplitude")
        self.expected_xlim = (0, self.num_samples)
        self.expected_ylim = (-self.max_amplitude, self.max_amplitude)
        self.ax.set_xlim(*self.expected_xlim)
        self.ax.set_ylim(*self.expected_ylim)
        self.ax.set_aspect('auto')

        # Plot original waveform in gray (background reference).
        self.ax.plot(np.arange(self.num_samples), self.audio_data, color='gray', alpha=0.3, lw=1)

        # Initialize empty envelopes for positive (blue) and negative (red).
        self.drawing_pos = np.zeros(self.num_samples)
        self.drawing_neg = np.zeros(self.num_samples)
        self.line_pos, = self.ax.plot([], [], color='blue', lw=2, label='Positive Envelope')
        self.line_neg, = self.ax.plot([], [], color='red',  lw=2, label='Negative Envelope')
        self.ax.legend()

        # Event connections.
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_resize = self.fig.canvas.mpl_connect('resize_event', self.on_resize)
        self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        # State variables for drawing and undo.
        self.is_drawing = False
        self.prev_idx = None
        self.last_state_pos = None
        self.last_state_neg = None

        # For partial redraw (blitting).
        self.background = None

    def on_resize(self, event):
        """When the figure is resized, reset axis limits and clear the cached background."""
        self.ax.set_xlim(*self.expected_xlim)
        self.ax.set_ylim(*self.expected_ylim)
        self.background = None

    def on_click(self, event):
        """Start drawing; save state for undo."""
        if event.inaxes != self.ax:
            return
        self.is_drawing = True
        self.prev_idx = int(event.xdata)
        # Save the current envelopes in case we need to undo.
        self.last_state_pos = self.drawing_pos.copy()
        self.last_state_neg = self.drawing_neg.copy()
        self.update_drawing(event)

    def on_hover(self, event):
        """Draw while mouse moves, if is_drawing is True."""
        if self.is_drawing and event.inaxes == self.ax:
            self.update_drawing(event)

    def on_release(self, event):
        """Stop drawing."""
        self.is_drawing = False
        self.prev_idx = None

    def on_key_press(self, event):
        """
        Handle key events:
          - 'r' -> Reset envelope
          - 'u' -> Undo last drawing
          - 'p' -> Preview the adjusted audio
        """
        if event.key == 'r':
            # Reset envelopes to zero.
            self.drawing_pos[:] = 0
            self.drawing_neg[:] = 0
            self.line_pos.set_data(np.arange(self.num_samples), self.drawing_pos)
            self.line_neg.set_data(np.arange(self.num_samples), self.drawing_neg)
            self.fig.canvas.draw()
            print("Envelope reset.")

        elif event.key == 'u':
            # Undo: restore the last saved state.
            if self.last_state_pos is not None and self.last_state_neg is not None:
                self.drawing_pos = self.last_state_pos.copy()
                self.drawing_neg = self.last_state_neg.copy()
                self.line_pos.set_data(np.arange(self.num_samples), self.drawing_pos)
                self.line_neg.set_data(np.arange(self.num_samples), self.drawing_neg)
                self.fig.canvas.draw()
                print("Undo last drawing.")
            else:
                print("Nothing to undo.")

        elif event.key == 'p':
            # Preview: apply the envelope, generate an audio array, and play it.
            print("Playing preview audio...")
            preview_audio = self.apply_drawing_to_waveform(play_only=True)
            sd.play(preview_audio, self.sample_rate)
            if hasattr(self.fig.canvas, "toolbar"):
                self.fig.canvas.toolbar.mode = ""
            self.fig.canvas.set_cursor(0)
            print("Preview finished. Continue drawing if you like.")

    def update_drawing(self, event):
        """Update the drawn envelope based on the current mouse position."""
        idx = int(event.xdata)
        if idx < 0 or idx >= self.num_samples:
            return
        if event.ydata is None:
            return

        # Optionally clamp to [-1,1] to prevent amplitude blow-ups. (Uncomment if needed)
        # amp = max(-1, min(1, event.ydata))
        amp = event.ydata

        # Choose which envelope to update: above 0 -> drawing_pos, below 0 -> drawing_neg
        if amp >= 0:
            envelope = self.drawing_pos
        else:
            envelope = self.drawing_neg

        # Linear interpolation between the previous index and the current one.
        if self.prev_idx is not None and idx != self.prev_idx:
            start_idx = self.prev_idx
            end_idx = idx
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx
                start_val = amp
                end_val = envelope[self.prev_idx]
            else:
                start_val = envelope[self.prev_idx]
                end_val = amp
            envelope[start_idx:end_idx+1] = np.linspace(start_val, end_val, end_idx - start_idx + 1)
        else:
            envelope[idx] = amp

        self.prev_idx = idx

        # Update the lines for partial redraw (blitting).
        self.line_pos.set_data(np.arange(self.num_samples), self.drawing_pos)
        self.line_neg.set_data(np.arange(self.num_samples), self.drawing_neg)

        # Blitting logic: redraw only the changed parts.
        if self.background is None:
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        else:
            self.fig.canvas.restore_region(self.background)
        self.ax.draw_artist(self.line_pos)
        self.ax.draw_artist(self.line_neg)
        self.fig.canvas.blit(self.ax.bbox)

    def save_drawing(self):
        """Save the final envelope drawing as a PNG."""
        self.ax.set_xlim(*self.expected_xlim)
        self.ax.set_ylim(*self.expected_ylim)
        output_png = os.path.join(self.output_folder, f"future_{self.base_name}.png")
        self.fig.savefig(output_png)
        print(f"Saved drawing as {output_png}")

    def save_envelope_data(self):
        """Save the drawn envelope data to CSV and NumPy files."""
        output_csv = os.path.join(self.output_folder, f"future_{self.base_name}.csv")
        with open(output_csv, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Index', 'Positive Amplitude', 'Negative Amplitude'])
            for i in range(self.num_samples):
                writer.writerow([i, self.drawing_pos[i], self.drawing_neg[i]])
        print(f"Saved envelope CSV as {output_csv}")

        np.save(os.path.join(self.output_folder, f"{self.base_name}_pos.npy"), self.drawing_pos)
        np.save(os.path.join(self.output_folder, f"{self.base_name}_neg.npy"), self.drawing_neg)
        print("Saved envelope data as .npy files.")

    def apply_drawing_to_waveform(self, play_only=False):
        """
        Apply the drawn envelope using your original per-sample logic:
          - If original sample > 0, use drawing_pos
          - If original sample < 0, use drawing_neg
          - If original sample == 0, keep it as is
        """
        adjusted_audio_data = np.copy(self.audio_data)
        for i in range(len(adjusted_audio_data)):
            if adjusted_audio_data[i] > 0:
                adjusted_audio_data[i] = self.drawing_pos[i]
            elif adjusted_audio_data[i] < 0:
                adjusted_audio_data[i] = self.drawing_neg[i]
            # else: zero remains zero

        if play_only:
            # Return int16 array for playback preview.
            return (adjusted_audio_data * 32767).astype(np.int16)

        # Otherwise, save the data.
        self.save_envelope_data()

        # Write out the adjusted WAV file.
        output_wav = os.path.join(self.output_folder, f"future_{self.base_name}.wav")
        wavfile.write(output_wav, self.sample_rate, (adjusted_audio_data * 32767).astype(np.int16))
        print(f"Saved adjusted audio as {output_wav}")

        # --- CHANGED: Save a second PNG for comparison of original vs. adjusted. ---
        fig2, ax2 = plt.subplots(2, 1, figsize=(10, 6))
        ax2[0].plot(self.audio_data, color='blue')
        ax2[0].set_title('Original Audio Waveform')
        ax2[1].plot(adjusted_audio_data, color='green')
        ax2[1].set_title('Adjusted Audio Waveform')
        plt.tight_layout()

        comparison_png = os.path.join(self.output_folder, f"comparison_{self.base_name}.png")
        fig2.savefig(comparison_png)  # Save the comparison plot
        print(f"Saved comparison as {comparison_png}")
        plt.show()
        # --------------------------------------------------------------------------

    def process_file(self):
        """Run the interactive drawing session and finalize the audio after user closes the plot."""
        plt.show()
        self.save_drawing()          # Save the envelope drawing
        self.apply_drawing_to_waveform()  # Save the comparison plot & adjusted WAV

def process_file():
    """Prompt for an audio file path, create the tool, run the drawing session."""
    audio_file = input("Enter the path to your audio file: ")
    if not os.path.exists(audio_file):
        print("File not found!")
        return
    tool = IntegratedWaveformTool(audio_file)
    tool.process_file()

def main():
    """Main loop to process multiple files if desired."""
    while True:
        process_file()
        cont = input("Process another file? (y/n): ")
        if cont.lower() != 'y':
            break

if __name__ == '__main__':
    main()
