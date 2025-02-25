import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import csv
import sounddevice as sd  # For real-time audio preview

# Updated Color Palettes
background_options = {
    "Black": "#000000",
    "Electric Blue": "#0000FF",
    "Neon Purple": "#BF00FF",
    "Bright Cyan": "#00FFFF",
    "Vibrant Magenta": "#FF00FF",
    "Neon Green": "#39FF14",
    "Hot Pink": "#FF69B4",
    "Neon Orange": "#FF4500",
    "Bright Yellow": "#FFFF00",
    "Electric Lime": "#CCFF00",
    "Vivid Red": "#FF0000",
    "Deep Sky Blue": "#00BFFF",
    "Vivid Violet": "#9F00FF",
    "Fluorescent Pink": "#FF1493",
    "Laser Lemon": "#FFFF66",
    "Screamin' Green": "#66FF66",
    "Ultra Red": "#FF2400",
    "Radical Red": "#FF355E",
    "Vivid Orange": "#FFA500",
    "Electric Indigo": "#6F00FF"
}

positive_options = {
    "Vibrant Green": "#00FF00",
    "Neon Green": "#39FF14",
    "Electric Lime": "#CCFF00",
    "Bright Yellow": "#FFFF00",
    "Vivid Cyan": "#00FFFF",
    "Electric Blue": "#0000FF",
    "Neon Purple": "#BF00FF",
    "Hot Pink": "#FF69B4",
    "Neon Orange": "#FF4500",
    "Vivid Red": "#FF0000",
    "Screamin' Green": "#66FF66",
    "Laser Lemon": "#FFFF66",
    "Fluorescent Magenta": "#FF00FF",
    "Hyper Blue": "#1F51FF",
    "Electric Teal": "#00FFEF",
    "Vivid Turquoise": "#00CED1",
    "Radical Red": "#FF355E",
    "Ultra Violet": "#7F00FF",
    "Neon Coral": "#FF6EC7",
    "Luminous Lime": "#BFFF00"
}

negative_options = {
    "Vibrant Green": "#00FF00",
    "Neon Orange": "#FF4500",
    "Hot Pink": "#FF69B4",
    "Vivid Cyan": "#00FFFF",
    "Electric Blue": "#0000FF",
    "Neon Purple": "#BF00FF",
    "Bright Yellow": "#FFFF00",
    "Electric Lime": "#CCFF00",
    "Vivid Red": "#FF0000",
    "Deep Pink": "#FF1493",
    "Screamin' Green": "#66FF66",
    "Laser Lemon": "#FFFF66",
    "Fluorescent Magenta": "#FF00FF",
    "Hyper Blue": "#1F51FF",
    "Electric Teal": "#00FFEF",
    "Vivid Turquoise": "#00CED1",
    "Radical Red": "#FF355E",
    "Ultra Violet": "#7F00FF",
    "Neon Coral": "#FF6EC7",
    "Luminous Lime": "#BFFF00"
}

def select_color(prompt, options, default):
    """
    Presents a list of colors from which the user can choose.
    If the user presses Enter without a choice, returns the default.
    """
    print(prompt)
    options_list = list(options.items())
    for i, (name, hexcode) in enumerate(options_list, start=1):
        print(f"  {i}. {name} ({hexcode})")
    choice = input(f"Select a number [default: {default}]: ")
    if not choice.strip():
        return default
    try:
        idx = int(choice)
        if 1 <= idx <= len(options_list):
            return options_list[idx-1][1]
        else:
            print("Invalid number. Using default.")
            return default
    except ValueError:
        print("Invalid input. Using default.")
        return default

class IntegratedWaveformTool:
    """
    A tool that:
      - Loads a WAV file (stereo -> mono, normalized).
      - Lets you draw envelopes for positive and negative parts of the waveform separately.
      - Uses per-sample logic to adjust the waveform.
      - Offers real-time audio preview, undo/reset, and partial redraw.
      - Saves three files:
          1) The drawn envelope as a PNG (future_original.png).
          2) A comparison PNG of original vs. adjusted waveforms.
          3) The modified waveform PNG.
    """
    def __init__(self, audio_file, pos_color="#39FF14", neg_color="#39FF14", bg_color="black"):
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

        # Save chosen colors.
        self.pos_color = pos_color
        self.neg_color = neg_color
        self.bg_color = bg_color

        # Set up figure and axes for drawing.
        self.fig, self.ax = plt.subplots()  # Using default figsize/dpi
        self.fig.patch.set_facecolor(self.bg_color)
        self.ax.set_facecolor(self.bg_color)
        self.ax.set_title("Draw Envelope (Keys: 'r' Reset, 'u' Undo, 'p' Preview)", color="white")
        self.ax.set_xlabel("Sample Index", color="white")
        self.ax.set_ylabel("Amplitude", color="white")
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.expected_xlim = (0, self.num_samples)
        self.expected_ylim = (-self.max_amplitude, self.max_amplitude)
        self.ax.set_xlim(*self.expected_xlim)
        self.ax.set_ylim(*self.expected_ylim)
        self.ax.set_aspect('auto')

        # Plot original waveform in gray (background reference).
        self.ax.plot(np.arange(self.num_samples), self.audio_data, color='gray', alpha=0.3, lw=1)

        # Initialize empty envelopes for positive and negative.
        self.drawing_pos = np.zeros(self.num_samples)
        self.drawing_neg = np.zeros(self.num_samples)
        self.line_pos, = self.ax.plot([], [], color=self.pos_color, lw=2, label='Positive Envelope')
        self.line_neg, = self.ax.plot([], [], color=self.neg_color, lw=2, label='Negative Envelope')
        
        legend = self.ax.legend()
        for text in legend.get_texts():
            text.set_color("white")
        legend.get_frame().set_facecolor(self.bg_color)

        # Event connections.
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_resize = self.fig.canvas.mpl_connect('resize_event', self.on_resize)
        self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        # State variables.
        self.is_drawing = False
        self.prev_idx = None
        self.last_state_pos = None
        self.last_state_neg = None

        # For partial redraw.
        self.background = None

    def on_resize(self, event):
        self.ax.set_xlim(*self.expected_xlim)
        self.ax.set_ylim(*self.expected_ylim)
        self.background = None

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        self.is_drawing = True
        self.prev_idx = int(event.xdata)
        self.last_state_pos = self.drawing_pos.copy()
        self.last_state_neg = self.drawing_neg.copy()
        self.update_drawing(event)

    def on_hover(self, event):
        if self.is_drawing and event.inaxes == self.ax:
            self.update_drawing(event)

    def on_release(self, event):
        self.is_drawing = False
        self.prev_idx = None

    def on_key_press(self, event):
        if event.key == 'r':
            self.drawing_pos[:] = 0
            self.drawing_neg[:] = 0
            self.line_pos.set_data(np.arange(self.num_samples), self.drawing_pos)
            self.line_neg.set_data(np.arange(self.num_samples), self.drawing_neg)
            self.fig.canvas.draw()
            print("Envelope reset.")
        elif event.key == 'u':
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
            print("Playing preview audio...")
            preview_audio = self.apply_drawing_to_waveform(play_only=True)
            sd.play(preview_audio, self.sample_rate)
            if hasattr(self.fig.canvas, "toolbar"):
                self.fig.canvas.toolbar.mode = ""
            self.fig.canvas.set_cursor(0)
            print("Preview finished. Continue drawing if you like.")

    def update_drawing(self, event):
        idx = int(event.xdata)
        if idx < 0 or idx >= self.num_samples or event.ydata is None:
            return
        amp = event.ydata
        envelope = self.drawing_pos if amp >= 0 else self.drawing_neg
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
        self.line_pos.set_data(np.arange(self.num_samples), self.drawing_pos)
        self.line_neg.set_data(np.arange(self.num_samples), self.drawing_neg)
        if self.background is None:
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        else:
            self.fig.canvas.restore_region(self.background)
        self.ax.draw_artist(self.line_pos)
        self.ax.draw_artist(self.line_neg)
        self.fig.canvas.blit(self.ax.bbox)

    def save_drawing(self):
        self.ax.set_xlim(*self.expected_xlim)
        self.ax.set_ylim(*self.expected_ylim)
        output_png = os.path.join(self.output_folder, f"future_{self.base_name}.png")
        self.fig.savefig(output_png)
        print(f"Saved drawing as {output_png}")

    def save_envelope_data(self):
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
        adjusted_audio_data = np.copy(self.audio_data)
        for i in range(len(adjusted_audio_data)):
            if adjusted_audio_data[i] > 0:
                adjusted_audio_data[i] = self.drawing_pos[i]
            elif adjusted_audio_data[i] < 0:
                adjusted_audio_data[i] = self.drawing_neg[i]
        if play_only:
            return (adjusted_audio_data * 32767).astype(np.int16)
        self.save_envelope_data()
        output_wav = os.path.join(self.output_folder, f"future_{self.base_name}.wav")
        wavfile.write(output_wav, self.sample_rate, (adjusted_audio_data * 32767).astype(np.int16))
        print(f"Saved adjusted audio as {output_wav}")
        
        # Get the original drawing's figsize and dpi
        orig_figsize = self.fig.get_size_inches()
        orig_dpi = self.fig.dpi

        # For comparison.png, we want two subplots where each subplot has the same dimensions as the original drawing.
        # Double the height so each subplot matches the original.
        comp_figsize = (orig_figsize[0], orig_figsize[1] * 2)
        fig2, ax2 = plt.subplots(2, 1, figsize=comp_figsize, dpi=orig_dpi)
        fig2.patch.set_facecolor(self.bg_color)
        for a in ax2:
            a.set_facecolor(self.bg_color)
            a.set_xlim(*self.expected_xlim)
            a.set_ylim(*self.expected_ylim)
            a.set_aspect('auto')
            a.title.set_color("white")
            a.xaxis.label.set_color("white")
            a.yaxis.label.set_color("white")
            a.tick_params(axis='x', colors='white')
            a.tick_params(axis='y', colors='white')
        ax2[0].plot(self.audio_data, color=self.pos_color)
        ax2[0].set_title('Original Audio Waveform')
        ax2[1].plot(adjusted_audio_data, color=self.pos_color)
        ax2[1].set_title('Adjusted Audio Waveform')
        comparison_png = os.path.join(self.output_folder, f"comparison_{self.base_name}.png")
        fig2.savefig(comparison_png)
        print(f"Saved comparison as {comparison_png}")
        plt.close(fig2)
        
        # Create a new PNG with only the modified waveform.
        fig3, ax3 = plt.subplots(figsize=orig_figsize, dpi=orig_dpi)
        fig3.patch.set_facecolor(self.bg_color)
        ax3.set_facecolor(self.bg_color)
        ax3.plot(adjusted_audio_data, color=self.pos_color)
        ax3.set_title('Modified Audio Waveform', color="white")
        ax3.set_xlabel('Sample Index', color="white")
        ax3.set_ylabel('Amplitude', color="white")
        ax3.tick_params(axis='x', colors='white')
        ax3.tick_params(axis='y', colors='white')
        ax3.set_xlim(*self.expected_xlim)
        ax3.set_ylim(*self.expected_ylim)
        ax3.set_aspect('auto')
        modified_wave_png = os.path.join(self.output_folder, f"modified_wave_{self.base_name}.png")
        fig3.savefig(modified_wave_png)
        print(f"Saved modified waveform as {modified_wave_png}")
        plt.close(fig3)
        plt.show()
        return adjusted_audio_data

    def process_file(self):
        plt.show()
        self.save_drawing()
        self.apply_drawing_to_waveform()

def process_file():
    audio_file = input("Enter the path to your audio file: ")
    if not os.path.exists(audio_file):
        print("File not found!")
        return
    custom = input("Do you want to choose colors from a preset list? (y/n): ")
    if custom.lower() == 'y':
        bg_color = select_color("Select a background color:", background_options, "#000000")
        pos_color = select_color("Select a positive envelope color:", positive_options, "#00FF00")
        neg_color = select_color("Select a negative envelope color:", negative_options, "#00FF00")
    else:
        bg_color = "black"
        pos_color = "#39FF14"
        neg_color = "#39FF14"
    tool = IntegratedWaveformTool(audio_file, pos_color=pos_color, neg_color=neg_color, bg_color=bg_color)
    tool.process_file()

def main():
    while True:
        process_file()
        cont = input("Process another file? (y/n): ")
        if cont.lower() != 'y':
            break

if __name__ == '__main__':
    main()
