import os
import sys
import shutil
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import csv
import sounddevice as sd

##############################################################################
# COLOR-PICKING FUNCTIONS
##############################################################################

def show_color_options(options, title):
    """
    Prints a table of color options with a small ANSI color swatch.
    """
    print(f"\n{title}")
    print(f"{'No.':<5} {'Name':<20} {'Hex Code':<10}  Sample")
    for idx, (name, hex_code) in enumerate(options.items(), 1):
        if hex_code.startswith('#') and len(hex_code) == 7:
            try:
                r = int(hex_code[1:3], 16)
                g = int(hex_code[3:5], 16)
                b = int(hex_code[5:7], 16)
            except ValueError:
                r, g, b = (255, 255, 255)
        else:
            r, g, b = (255, 255, 255)
        ansi_color = f"\033[38;2;{r};{g};{b}m"
        ansi_reset = "\033[0m"
        print(f"{idx:<5} {name:<20} {hex_code:<10}  {ansi_color}██{ansi_reset}")
    return list(options.values())

def choose_color(options, prompt):
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Invalid input. Please enter a number.")

def run_color_picker(default_bg, default_pos, default_neg):
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

    use_custom = input("Use custom colors? (y/n): ").lower() == 'y'
    if not use_custom:
        return default_bg, default_pos, default_neg

    bg_vals  = show_color_options(background_options, "Background Colors:")
    bg_pick  = choose_color(bg_vals,  "Select background color (enter number): ")

    pos_vals = show_color_options(positive_options,  "\nPositive Envelope Colors:")
    pos_pick = choose_color(pos_vals, "Select positive color (enter number): ")

    neg_vals = show_color_options(negative_options,  "\nNegative Envelope Colors:")
    neg_pick = choose_color(neg_vals, "Select negative color (enter number): ")

    return bg_pick, pos_pick, neg_pick

##############################################################################
# ENVELOPEPLOT + MAIN LOGIC
##############################################################################

class EnvelopePlot:
    def __init__(self, wav_file, ax, bg_color, pos_color, neg_color):
        self.wav_file = wav_file
        self.ax = ax

        self.canvas_bg_color = bg_color
        self.canvas_pos_color = pos_color
        self.canvas_neg_color = neg_color

        self.ax.set_facecolor(self.canvas_bg_color)
        self.fig = self.ax.figure
        self.fig.patch.set_facecolor(self.canvas_bg_color)

        self.sample_rate, data = wavfile.read(wav_file)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        self.audio_data = data.astype(float) / np.max(np.abs(data))
        self.num_points = len(self.audio_data)
        self.max_amp = np.max(np.abs(self.audio_data))

        self.faint_line, = self.ax.plot(
            self.audio_data,
            color=self.canvas_pos_color,
            alpha=0.15,
            lw=1
        )

        self.drawing_pos = np.zeros(self.num_points)
        self.drawing_neg = np.zeros(self.num_points)

        self.line_pos, = self.ax.plot([], [],
                                      color=self.canvas_pos_color,
                                      lw=2, label='Positive')
        self.line_neg, = self.ax.plot([], [],
                                      color=self.canvas_neg_color,
                                      lw=2, label='Negative')

        self.final_line = None
        self.comparison_line_orig = None
        self.comparison_line_mod  = None

        margin = 0.1 * self.max_amp
        self.ax.set_xlim(0, self.num_points)
        self.ax.set_ylim(-self.max_amp - margin, self.max_amp + margin)
        self.ax.tick_params(axis='both', colors='gray')
        for spine in self.ax.spines.values():
            spine.set_color('gray')

        base_name = os.path.basename(wav_file)
        self.ax.text(10, self.max_amp - margin,
                     base_name, fontsize=9, color='gray', alpha=0.8,
                     verticalalignment='top')

        self.is_drawing = False
        self.prev_idx = None
        self.last_state_pos = None
        self.last_state_neg = None
        self.background = None
        self.offset = 0.0

    def on_mouse_press(self, event):
        if event.inaxes != self.ax:
            return
        self.is_drawing = True
        if event.xdata is not None:
            self.prev_idx = int(event.xdata)
        self.last_state_pos = self.drawing_pos.copy()
        self.last_state_neg = self.drawing_neg.copy()
        self.update_drawing(event)

    def on_mouse_move(self, event):
        if self.is_drawing and event.inaxes == self.ax:
            self.update_drawing(event)

    def on_mouse_release(self, event):
        self.is_drawing = False

    def update_drawing(self, event):
        if event.xdata is None or event.ydata is None:
            return
        idx = int(event.xdata)
        if idx < 0 or idx >= self.num_points:
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
            envelope[start_idx:end_idx+1] = np.linspace(
                start_val, end_val,
                end_idx - start_idx + 1
            )
        else:
            envelope[idx] = amp
        self.prev_idx = idx

        self.line_pos.set_data(np.arange(self.num_points),
                               self.drawing_pos + self.offset)
        self.line_neg.set_data(np.arange(self.num_points),
                               self.drawing_neg + self.offset)

        if self.background is None:
            self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)
        else:
            self.ax.figure.canvas.restore_region(self.background)
        self.ax.draw_artist(self.line_pos)
        self.ax.draw_artist(self.line_neg)
        self.ax.figure.canvas.blit(self.ax.bbox)

    def undo_envelope(self):
        if self.last_state_pos is not None and self.last_state_neg is not None:
            self.drawing_pos = self.last_state_pos.copy()
            self.drawing_neg = self.last_state_neg.copy()
            self.redraw_lines()

    def reset_envelope(self):
        self.drawing_pos[:] = 0
        self.drawing_neg[:] = 0
        self.redraw_lines()

    def redraw_lines(self):
        self.line_pos.set_data(np.arange(self.num_points),
                               self.drawing_pos + self.offset)
        self.line_neg.set_data(np.arange(self.num_points),
                               self.drawing_neg + self.offset)
        self.ax.figure.canvas.draw_idle()

    def preview_envelope(self):
        adjusted = np.copy(self.audio_data)
        for i in range(len(adjusted)):
            if adjusted[i] > 0:
                adjusted[i] = self.drawing_pos[i] + self.offset
            elif adjusted[i] < 0:
                adjusted[i] = self.drawing_neg[i] + self.offset
        audio_int16 = (adjusted * 32767).astype(np.int16)
        sd.play(audio_int16, self.sample_rate)
        sd.wait()

    def reapply_colors(self, bg_color, pos_color, neg_color,
                       faint_alpha=0.15, final_wave_color="#00FF00",
                       final_wave_alpha=0.4, orig_alpha=0.6, mod_alpha=0.8):
        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)

        if self.faint_line is not None:
            self.faint_line.set_color(pos_color)
            self.faint_line.set_alpha(faint_alpha)

        self.line_pos.set_color(pos_color)
        self.line_neg.set_color(neg_color)

        if self.final_line is not None:
            self.final_line.set_color(final_wave_color)
            self.final_line.set_alpha(final_wave_alpha)

        if self.comparison_line_orig is not None:
            self.comparison_line_orig.set_color(neg_color)
            self.comparison_line_orig.set_alpha(orig_alpha)

        if self.comparison_line_mod is not None:
            self.comparison_line_mod.set_color(pos_color)
            self.comparison_line_mod.set_alpha(mod_alpha)

        self.ax.figure.canvas.draw_idle()

def get_modified_wave(ep):
    adjusted = np.copy(ep.audio_data)
    for i in range(len(adjusted)):
        if adjusted[i] > 0:
            adjusted[i] = ep.drawing_pos[i] + ep.offset
        elif adjusted[i] < 0:
            adjusted[i] = ep.drawing_neg[i] + ep.offset
    return adjusted

##############################################################################
# SINGLE FILE PROCESSING (MAIN)
##############################################################################

def process_single_file():
    # 1) Ask for a single .wav file
    print("\n=== Insert your .wav file ===")
    wf = input("Enter path to .wav file: ")
    if not os.path.exists(wf):
        print(f"File not found: {wf}")
        sys.exit(1)

    # Create a folder based on the file name
    first_base = os.path.splitext(os.path.basename(wf))[0]
    new_folder = os.path.join(os.getcwd(), first_base)
    os.makedirs(new_folder, exist_ok=True)
    print(f"Created folder: {new_folder}")

    # Copy the .wav file to the new folder
    shutil.copy(wf, new_folder)
    print(f"Copied {wf} to {new_folder}")

    # 2) Drawing canvas color picker
    print("\n=== Drawing Canvas Color Picker ===")
    default_bg  = "#000000"
    default_pos = "#00FF00"
    default_neg = "#00FF00"
    draw_bg, draw_pos, draw_neg = run_color_picker(default_bg, default_pos, default_neg)

    # 3) Create figure and single subplot for interactive drawing
    fig, ax = plt.subplots(1, 1, figsize=(16, 3), facecolor=draw_bg)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.05)

    # Disconnect default key press handler if present
    if hasattr(fig.canvas.manager, 'key_press_handler_id'):
        fig.canvas.mpl_disconnect(fig.canvas.manager.key_press_handler_id)

    # 4) Create EnvelopePlot object
    ep = EnvelopePlot(wf, ax, bg_color=draw_bg, pos_color=draw_pos, neg_color=draw_neg)
    ax.set_aspect('auto')
    leg = ax.legend(loc='upper right')
    leg.get_frame().set_alpha(0.5)
    ax.text(
        0.65, 0.90,
        "p=preview\nr=reset\nu=undo",
        transform=ax.transAxes,
        fontsize=8,
        color='white',
        ha='left',
        va='top',
        bbox=dict(boxstyle="round", fc="black", ec="none", alpha=0.5)
    )

    print("\nIn the drawing canvas:\n"
          " - Press 'p' to preview.\n"
          " - Press 'r' to reset.\n"
          " - Press 'u' to undo.\n")

    # 5) Interactive drawing callbacks
    def on_press(event):
        if event.inaxes == ep.ax:
            ep.on_mouse_press(event)

    def on_move(event):
        if event.inaxes == ep.ax:
            ep.on_mouse_move(event)

    def on_release(event):
        if event.inaxes == ep.ax:
            ep.on_mouse_release(event)

    def on_key(event):
        if not event.key:
            return
        k = event.key.lower()
        if event.inaxes != ep.ax:
            return
        if k == 'p':
            print("Previewing envelope...")
            ep.preview_envelope()
        elif k == 'r':
            ep.reset_envelope()
            print("Envelope reset.")
        elif k == 'u':
            ep.undo_envelope()
            print("Undo last stroke.")

    cid_press   = fig.canvas.mpl_connect('button_press_event', on_press)
    cid_move    = fig.canvas.mpl_connect('motion_notify_event', on_move)
    cid_release = fig.canvas.mpl_connect('button_release_event', on_release)
    cid_key     = fig.canvas.mpl_connect('key_press_event', on_key)

    plt.show(block=False)
    print("Drawing phase active. Press Enter when done.")
    input()

    # Disconnect interactive callbacks
    fig.canvas.mpl_disconnect(cid_press)
    fig.canvas.mpl_disconnect(cid_move)
    fig.canvas.mpl_disconnect(cid_release)
    fig.canvas.mpl_disconnect(cid_key)

    # 6) final_drawing color picker and save final drawing
    print("\n=== final_drawing Color Picker ===")
    f_bg, f_pos, f_neg = run_color_picker(draw_bg, draw_pos, draw_neg)
    ep.reapply_colors(f_bg, f_pos, f_neg)

    final_path = os.path.join(new_folder, "final_drawing.png")
    fig.savefig(final_path)
    print(f"final_drawing.png saved to {final_path}")

    # 7) Save envelope CSV data and modified audio WAV
    csv_path = os.path.join(new_folder, "envelope.csv")
    with open(csv_path, "w", newline="") as f_:
        writer = csv.writer(f_)
        writer.writerow(["Index", "Positive", "Negative"])
        for i in range(ep.num_points):
            writer.writerow([i, ep.drawing_pos[i], ep.drawing_neg[i]])
    print(f"Envelope data saved to {csv_path}")

    mod_wave = get_modified_wave(ep)
    wav_path = os.path.join(new_folder, f"future_{os.path.basename(ep.wav_file)}")
    wavfile.write(wav_path, ep.sample_rate, (mod_wave * 32767).astype(np.int16))
    print(f"Modified audio saved to {wav_path}")

    # 8) natural_lang: remove faint wave, add final wave line, and save image
    if ep.faint_line is not None:
        ep.faint_line.remove()
        ep.faint_line = None
    ep.final_line, = ep.ax.plot(mod_wave, color='lime', alpha=0.4, lw=2, label='Modified Wave')

    print("\n=== natural_lang Color Picker ===")
    n_bg, n_pos, n_neg = run_color_picker(f_bg, f_pos, f_neg)
    ep.reapply_colors(n_bg, n_pos, n_neg)
    ax.legend(loc='upper right').get_frame().set_alpha(0.5)

    nat_path = os.path.join(new_folder, "natural_lang.png")
    fig.savefig(nat_path)
    print(f"natural_lang.png saved to {nat_path}")

    # 9) wave_comparison: remove final_line, add comparison lines, and save image
    if ep.final_line is not None:
        ep.final_line.remove()
        ep.final_line = None

    ep.comparison_line_orig, = ep.ax.plot(
        ep.audio_data,
        color=n_neg,
        alpha=0.6,
        lw=2,
        label='Original Wave'
    )
    mod_data = get_modified_wave(ep)
    ep.comparison_line_mod, = ep.ax.plot(
        mod_data,
        color=n_pos,
        alpha=0.8,
        lw=2,
        label='Modified Wave'
    )

    print("\n=== wave_comparison Color Picker ===")
    c_bg, c_pos, c_neg = run_color_picker(n_bg, n_pos, n_neg)
    ep.reapply_colors(c_bg, c_pos, c_neg)
    ax.legend(loc='upper right').get_frame().set_alpha(0.5)

    cmp_path = os.path.join(new_folder, "wave_comparison.png")
    fig.savefig(cmp_path)
    print(f"wave_comparison.png saved to {cmp_path}")

    plt.close()

if __name__ == '__main__':
    while True:
        process_single_file()
        cont = input("\nDo you want to process another file? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting program.")
            break
