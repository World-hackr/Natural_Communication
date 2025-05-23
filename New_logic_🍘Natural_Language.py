import matplotlib
# Disable the Matplotlib navigation toolbar
matplotlib.rcParams['toolbar'] = 'None'

import os
import sys
import shutil
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import csv
import sounddevice as sd
from scipy import signal
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.widgets import Slider

##############################################################################
# Zero-Crossing Finder
##############################################################################
def find_zero_crossings(data):
    """
    Return a list of indices where the sign of 'data' changes.
    We'll treat an exact zero crossing as a sign change if it goes from negative
    to zero to positive or vice versa.
    """
    zero_positions = []
    prev_sign = np.sign(data[0])
    for i in range(1, len(data)):
        current_sign = np.sign(data[i])
        if current_sign != prev_sign:
            zero_positions.append(i)
            prev_sign = current_sign
    return zero_positions

##############################################################################
# 1) CUSTOM WAVE GENERATION
##############################################################################
def generate_custom_wave():
    print("\n=== Custom Frequency Waveform Generation ===")
    print("Choose a preset or go manual:")
    print("  1) Sine wave     (freq=440, spw=100, periods=10)")
    print("  2) Square wave   (freq=220, spw=80,  periods=20)")
    print("  3) Triangle wave (freq=100, spw=200, periods=5)")
    print("  4) Sawtooth wave (freq=50,  spw=120, periods=15)")
    print("  5) Manual entry")
    choice = input("Enter 1-5: ").strip()

    wave_type = "sine"
    freq = 440.0
    spw  = 100
    periods = 10

    if choice == "1":
        print("\nPreset 1: Sine wave (freq=440, spw=100, periods=10)")
    elif choice == "2":
        wave_type = "square"
        freq = 220
        spw  = 80
        periods = 20
        print("\nPreset 2: Square wave (freq=220, spw=80, periods=20)")
    elif choice == "3":
        wave_type = "triangle"
        freq = 100
        spw  = 200
        periods = 5
        print("\nPreset 3: Triangle wave (freq=100, spw=200, periods=5)")
    elif choice == "4":
        wave_type = "sawtooth"
        freq = 50
        spw  = 120
        periods = 15
        print("\nPreset 4: Sawtooth wave (freq=50, spw=120, periods=15)")
    elif choice == "5":
        print("\nManual Entry:")
        print("Wave Type (enter 1-4):")
        print("  1) sine\n  2) square\n  3) triangle\n  4) sawtooth")
        wt_choice = input("Wave type (1-4): ").strip()
        if wt_choice == "2":
            wave_type = "square"
        elif wt_choice == "3":
            wave_type = "triangle"
        elif wt_choice == "4":
            wave_type = "sawtooth"
        else:
            wave_type = "sine"
        try:
            freq = float(input("Enter frequency in Hz (e.g. 440): "))
            spw  = int(input("Enter samples per wavelength (e.g. 100): "))
            periods = int(input("Enter number of periods (e.g. 10): "))
        except ValueError:
            print("Invalid input. Using defaults: wave=sine, freq=440, spw=100, periods=10.")
            wave_type = "sine"
            freq = 440.0
            spw = 100
            periods = 10
    else:
        print("\nInvalid choice, using default sine wave with freq=440, spw=100, periods=10.")

    total_samples = spw * periods
    sample_rate = int(freq * spw)
    duration = periods / freq
    t = np.linspace(0, duration, total_samples, endpoint=False)

    if wave_type == "square":
        wave = np.sign(np.sin(2*np.pi*freq*t))
    elif wave_type == "triangle":
        wave = signal.sawtooth(2*np.pi*freq*t, 0.5)
    elif wave_type == "sawtooth":
        wave = signal.sawtooth(2*np.pi*freq*t)
    else:
        wave = np.sin(2*np.pi*freq*t)

    wave /= np.max(np.abs(wave))

    out_file = input("Enter name for custom wave file (e.g. my_custom_signal.wav): ").strip()
    if not out_file:
        out_file = "my_custom_wave.wav"
    elif not out_file.lower().endswith(".wav"):
        out_file += ".wav"

    wavfile.write(out_file, sample_rate, (wave * 32767).astype(np.int16))

    print(f"\nGenerated {wave_type} wave, freq={freq} Hz, sample_rate={sample_rate} Hz, "
          f"samples={total_samples}, duration={duration*1000:.2f} ms.")
    print(f"Custom wave saved to {out_file}")
    return out_file

##############################################################################
# 2) COLOR PICKER FUNCTIONS
##############################################################################
def show_color_options(options, title):
    print(f"\n{title}")
    print(f"{'No.':<5} {'Name':<20} {'Hex Code':<10}  Sample")
    for idx, (name, hex_code) in enumerate(options.items(), 1):
        try:
            r = int(hex_code[1:3], 16)
            g = int(hex_code[3:5], 16)
            b = int(hex_code[5:7], 16)
        except:
            r, g, b = (255, 255, 255)
        ansi_color = f"\033[38;2;{r};{g};{b}m"
        ansi_reset = "\033[0m"
        print(f"{idx:<5} {name:<20} {hex_code:<10}  {ansi_color}██{ansi_reset}")
    return list(options.values())

def choose_color(options, prompt):
    while True:
        choice_str = input(prompt).strip()
        if not choice_str.isdigit():
            print("Invalid input. Please enter a number.")
            continue
        choice = int(choice_str)
        if 1 <= choice <= len(options):
            return options[choice - 1]
        else:
            print(f"Please enter a number between 1 and {len(options)}")

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

    print("\nBackground Colors:")
    bg_vals = show_color_options(background_options, "Pick a background color:")
    bg_pick = choose_color(bg_vals, "Enter number for background: ")

    print("\nPositive Envelope Colors:")
    pos_vals = show_color_options(positive_options, "Pick a positive color:")
    pos_pick = choose_color(pos_vals, "Enter number for positive: ")

    print("\nNegative Envelope Colors:")
    neg_vals = show_color_options(negative_options, "Pick a negative color:")
    neg_pick = choose_color(neg_vals, "Enter number for negative: ")

    return bg_pick, pos_pick, neg_pick

##############################################################################
# 3) STRICT SIGN SUBDIVISION HELPERS
##############################################################################
def strict_sign_subdivision(x, y):
    new_x = []
    new_y = []
    color_val = []

    n = len(x)
    if n == 0:
        return np.array([]), np.array([]), np.array([])

    def sign_color(val):
        return 0 if val < 0 else 1

    for i in range(n - 1):
        xi, yi = x[i], y[i]
        xip1, yip1 = x[i+1], y[i+1]

        new_x.append(xi)
        new_y.append(yi)
        color_val.append(sign_color(yi))

        # Detect crossing from negative->positive or positive->negative
        if (yi < 0 and yip1 >= 0) or (yi >= 0 and yip1 < 0):
            dy = yip1 - yi
            t = (0 - yi)/dy if abs(dy) > 1e-12 else 0.5
            x_cross = xi + t*(xip1 - xi)
            crossing_color = 1 if (yi < 0 and yip1 >= 0) else 0
            new_x.append(x_cross)
            new_y.append(0.0)
            color_val.append(crossing_color)

    new_x.append(x[-1])
    new_y.append(y[-1])
    color_val.append(sign_color(y[-1]))

    return np.array(new_x), np.array(new_y), np.array(color_val)

def plot_strict_sign_colored_line(ax, xdata, ydata, neg_color, pos_color, linewidth=2, label="Modified Wave"):
    sx, sy, cvals = strict_sign_subdivision(xdata, ydata)
    points = np.array([sx, sy]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    cmap = ListedColormap([neg_color, pos_color])
    norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)
    lc = LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(cvals[:-1])
    lc.set_linewidth(linewidth)
    ax.add_collection(lc)
    ax.set_xlim(sx.min(), sx.max())
    miny, maxy = sy.min(), sy.max()
    pad = 0.05 * (maxy - miny if (maxy - miny) != 0 else 1)
    ax.set_ylim(miny - pad, maxy + pad)
    dummy_line = ax.plot([], [], color='none', label=label)[0]
    return lc, dummy_line

##############################################################################
# 4) EnvelopePlot Class (clamp user drawing to [-1,1])
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
        # Normalize to [-1,1]
        self.audio_data = data.astype(float) / np.max(np.abs(data))
        self.num_points = len(self.audio_data)
        self.max_amp = np.max(np.abs(self.audio_data))

        time_axis = np.arange(self.num_points)/self.sample_rate
        # faint_line => original wave (light)
        self.faint_line, = self.ax.plot(
            time_axis,
            self.audio_data,
            color=self.canvas_pos_color,
            alpha=0.15, lw=1
        )

        self.drawing_pos = np.zeros(self.num_points)
        self.drawing_neg = np.zeros(self.num_points)

        self.line_pos, = self.ax.plot([], [], color=self.canvas_pos_color, lw=2, label='Positive')
        self.line_neg, = self.ax.plot([], [], color=self.canvas_neg_color, lw=2, label='Negative')

        self.final_line = None
        self.comparison_line_orig = None
        self.comparison_line_mod  = None

        margin = 0.1 * self.max_amp
        self.ax.set_xlim(0, self.num_points/self.sample_rate)
        self.ax.set_ylim(-self.max_amp - margin, self.max_amp + margin)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.tick_params(axis='both', colors='gray')
        for spine in self.ax.spines.values():
            spine.set_color('gray')

        base_name = os.path.basename(wav_file)
        self.ax.text(0.01, 0.95, base_name,
                     fontsize=9, color='gray', alpha=0.8,
                     transform=self.ax.transAxes,
                     verticalalignment='top')

        self.ax.set_aspect('auto')

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
            self.prev_idx = int(event.xdata * self.sample_rate)
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
        idx = int(event.xdata * self.sample_rate)
        if idx < 0 or idx >= self.num_points:
            return

        # 1) Clamp amplitude to [-1,1]
        amp = max(min(event.ydata, 1.0), -1.0)

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

        time_axis = np.arange(self.num_points)/self.sample_rate
        self.line_pos.set_data(time_axis, self.drawing_pos + self.offset)
        self.line_neg.set_data(time_axis, self.drawing_neg + self.offset)

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
        time_axis = np.arange(self.num_points)/self.sample_rate
        self.line_pos.set_data(time_axis, self.drawing_pos + self.offset)
        self.line_neg.set_data(time_axis, self.drawing_neg + self.offset)
        self.ax.figure.canvas.draw_idle()

    def preview_envelope(self):
        adjusted = self.get_drawn_wave()
        audio_int16 = (adjusted * 32767).astype(np.int16)
        sd.play(audio_int16, self.sample_rate)
        sd.wait()

    def get_drawn_wave(self):
        """
        Return the raw 'drawn' wave, i.e. if sample>0 => use drawing_pos,
        if sample<0 => use drawing_neg. Then clamp again just in case.
        """
        adjusted = np.copy(self.audio_data)
        for i in range(len(adjusted)):
            if adjusted[i] > 0:
                val = self.drawing_pos[i] + self.offset
            elif adjusted[i] < 0:
                val = self.drawing_neg[i] + self.offset
            else:
                val = self.drawing_pos[i] + self.offset
            # clamp to [-1,1]
            adjusted[i] = max(min(val, 1.0), -1.0)
        return adjusted

    def reapply_colors(self, bg_color, pos_color, neg_color,
                       faint_alpha=0.15, final_wave_color="#00FF00",
                       final_wave_alpha=0.4, orig_alpha=0.6, mod_alpha=0.8):
        self.ax.set_facecolor(bg_color)
        self.fig.patch.set_facecolor(bg_color)
        if self.faint_line is not None:
            self.faint_line.set_color(pos_color)
            self.faint_line.set_alpha(faint_alpha)
        if self.line_pos is not None:
            self.line_pos.set_color(pos_color)
        if self.line_neg is not None:
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

##############################################################################
# Additional Helper: Write CSV
##############################################################################
def write_csv(filename, headers, data_rows):
    """
    Generic CSV writer.
    headers: list of column names
    data_rows: list of lists, each sublist is one row
    """
    with open(filename, "w", newline="") as f_:
        writer = csv.writer(f_)
        writer.writerow(headers)
        for row in data_rows:
            writer.writerow(row)

##############################################################################
# Modified Wave Creation (Using a SCALING approach)
##############################################################################
def create_modified_wave(original_data, drawn_data, zero_positions):
    """
    1) Chunk original_data from zero_positions[i] to zero_positions[i+1].
    2) For each chunk, find largest absolute peak => original_peak[i].
    3) For the same chunk in drawn_data, find the maximum absolute amplitude => drawn_peak[i].
    4) scale_factor = original_peak[i] / drawn_peak[i], or 0 if drawn_peak[i] is near zero.
    5) Multiply the chunk of original_data by scale_factor, clip to [-1, 1].
    """
    # For safety, clamp drawn_data to [-1,1] in case user drew huge values
    drawn_data = np.clip(drawn_data, -1.0, 1.0)

    all_positions = [0] + zero_positions + [len(original_data)]
    new_data = np.copy(original_data)

    for i in range(len(all_positions) - 1):
        start_idx = all_positions[i]
        end_idx   = all_positions[i+1]  # non-inclusive boundary

        chunk_orig = original_data[start_idx:end_idx]
        chunk_drawn = drawn_data[start_idx:end_idx]

        if len(chunk_orig) == 0:
            continue
        # Step 2: largest absolute peak in the original chunk
        peak_val = np.max(np.abs(chunk_orig))

        # Step 3: maximum absolute amplitude in the drawn chunk
        drawn_peak = np.max(np.abs(chunk_drawn)) if len(chunk_drawn) else 0.0

        # Step 4: scale factor
        if drawn_peak < 1e-12:
            # If user drew near 0, we can set the entire chunk to 0
            # or keep it unchanged. Let's assume we set it to 0:
            shifted_chunk = np.zeros_like(chunk_orig)
        else:
            scale_factor = peak_val / drawn_peak
            shifted_chunk = chunk_orig * scale_factor

        # Step 5: clip
        shifted_chunk = np.clip(shifted_chunk, -1.0, 1.0)
        new_data[start_idx:end_idx] = shifted_chunk

    return new_data

##############################################################################
# process_single_file (Main Flow for One File)
##############################################################################
def process_single_file():
    print("\nDo you want to:")
    print("  1) Use an existing .wav file")
    print("  2) Generate a custom wave (presets/manual)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "2":
        wf = generate_custom_wave()
    else:
        print("\n=== Insert your .wav file ===")
        wf = input("Enter path to .wav file: ")
        if not os.path.exists(wf):
            print(f"File not found: {wf}")
            sys.exit(1)

    # Create folder
    first_base = os.path.splitext(os.path.basename(wf))[0]
    new_folder = os.path.join(os.getcwd(), first_base)
    os.makedirs(new_folder, exist_ok=True)
    print(f"Created folder: {new_folder}")

    shutil.copy(wf, new_folder)
    print(f"Copied {wf} to {new_folder}")

    # ================== Step 1: Save original.csv ====================
    sr, raw_data = wavfile.read(wf)
    if raw_data.ndim > 1:
        raw_data = np.mean(raw_data, axis=1)
    raw_data = raw_data.astype(float)
    max_val = np.max(np.abs(raw_data))
    if max_val < 1e-12:
        max_val = 1.0
    # Normalize
    raw_data_norm = raw_data / max_val

    original_csv_path = os.path.join(new_folder, "original.csv")
    orig_rows = [[i, sample] for i, sample in enumerate(raw_data_norm)]
    write_csv(original_csv_path, ["Index", "Amplitude"], orig_rows)
    print(f"original.csv saved to {original_csv_path}")

    # ================== Step 2: wave_position.csv ====================
    zc_indices = find_zero_crossings(raw_data_norm)
    wavepos_csv_path = os.path.join(new_folder, "wave_position.csv")
    wp_rows = [[idx] for idx in zc_indices]
    write_csv(wavepos_csv_path, ["ZeroCrossIndex"], wp_rows)
    print(f"wave_position.csv saved to {wavepos_csv_path}")

    # =========== Drawing Canvas =============
    print("\n=== Drawing Canvas Color Picker ===")
    draw_bg, draw_pos, draw_neg = run_color_picker("#000000", "#00FF00", "#00FF00")

    fig, ax = plt.subplots(1, 1, figsize=(16, 3), facecolor=draw_bg)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.1)

    ep = EnvelopePlot(wf, ax, bg_color=draw_bg, pos_color=draw_pos, neg_color=draw_neg)
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

    fig.canvas.mpl_disconnect(cid_press)
    fig.canvas.mpl_disconnect(cid_move)
    fig.canvas.mpl_disconnect(cid_release)
    fig.canvas.mpl_disconnect(cid_key)

    # ================== Step 3: Save drawn.csv ====================
    drawn_wave = ep.get_drawn_wave()  # direct envelope approach (already clamped)
    drawn_csv_path = os.path.join(new_folder, "drawn.csv")
    drows = [[i, amp] for i, amp in enumerate(drawn_wave)]
    write_csv(drawn_csv_path, ["Index", "DrawnAmplitude"], drows)
    print(f"drawn.csv saved to {drawn_csv_path}")

    # =========== final_drawing =============
    print("\n=== final_drawing Color Picker ===")
    f_bg, f_pos, f_neg = run_color_picker("#000000", "#00FF00", "#00FF00")
    ep.reapply_colors(f_bg, f_pos, f_neg)

    final_path = os.path.join(new_folder, "final_drawing.png")
    fig.savefig(final_path)
    print(f"final_drawing.png saved to {final_path}")

    # ======== Create the modified wave with the new SCALING logic ========
    mod_wave = create_modified_wave(raw_data_norm, drawn_wave, zc_indices)
    # Print debug info
    print(f"DEBUG: mod_wave min={mod_wave.min():.3f}, max={mod_wave.max():.3f}")

    # Convert back to int16
    mod_wave_int16 = (mod_wave * 32767).astype(np.int16)
    wav_path = os.path.join(new_folder, f"future_{os.path.basename(ep.wav_file)}")
    wavfile.write(wav_path, ep.sample_rate, mod_wave_int16)
    print(f"Modified audio saved to {wav_path}")

    # =========== natural_lang => strict sign-based coloring =============
    if ep.faint_line is not None:
        ep.faint_line.remove()
        ep.faint_line = None
    if ep.line_pos is not None:
        ep.line_pos.remove()
        ep.line_pos = None
    if ep.line_neg is not None:
        ep.line_neg.remove()
        ep.line_neg = None
    if ep.final_line is not None:
        ep.final_line.remove()
        ep.final_line = None

    print("\n=== natural_lang Color Picker ===")
    n_bg, n_pos, n_neg = run_color_picker("#000000", "#00FF00", "#00FFFF")
    ep.reapply_colors(n_bg, n_pos, n_neg)

    ax.cla()
    ax.set_facecolor(n_bg)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")

    time_axis = np.arange(len(mod_wave)) / sr
    # We'll fix the y-limits to [-1.1, 1.1] so it won't auto-scale:
    ax.set_xlim(0, len(mod_wave)/sr)
    ax.set_ylim(-1.1, 1.1)

    lc, dummy_line = plot_strict_sign_colored_line(
        ax, time_axis, mod_wave,
        neg_color=n_neg,
        pos_color=n_pos,
        linewidth=2,
        label="Modified Wave"
    )

    ax.legend(loc='upper right').get_frame().set_alpha(0.5)
    ax.set_aspect('auto')
    nat_path = os.path.join(new_folder, "natural_lang.png")
    fig.savefig(nat_path)
    print(f"natural_lang.png saved to {nat_path}")

    # =========== wave_comparison => original vs modified =============
    ax.cla()
    print("\n=== wave_comparison Color Picker ===")
    c_bg, c_pos, c_neg = run_color_picker("#000000", "#00FF00", "#FF0000")
    ep.reapply_colors(c_bg, c_pos, c_neg)

    ax.set_facecolor(c_bg)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")

    ax.plot(time_axis, raw_data_norm, lw=2, color=c_neg, label='Original Wave')
    ax.plot(time_axis, mod_wave, lw=2, color=c_pos, label='Modified Wave')
    ax.legend(loc='upper right').get_frame().set_alpha(0.5)

    ax.set_xlim(0, len(mod_wave)/sr)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect('auto')

    cmp_path = os.path.join(new_folder, "wave_comparison.png")
    fig.savefig(cmp_path)
    print(f"wave_comparison.png saved to {cmp_path}")

    plt.close()

def main():
    while True:
        process_single_file()
        cont = input("\nDo you want to process another file? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting program.")
            break

if __name__ == '__main__':
    main()
