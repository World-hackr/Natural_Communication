## Main File
The main code of this project is in **🍘Natural_language.py**.
Do not mind the Steps, 🍘unless you want to know how i came up with the idea for final code🍘

# Integrated Waveform Tool

An interactive Python tool for custom audio envelope manipulation. This version applies your original per-sample envelope logic (no smoothing) and includes advanced features such as partial redraw, real-time audio preview, undo/reset, a background waveform reference, **and two PNG outputs**:

1. **`future_[filename].png`:** The drawn envelope itself.  
2. **`comparison_[filename].png`:** A side-by-side plot of the original vs. adjusted waveforms.

## Key Features

1. **Original Envelope Application (No Smoothing)**  
   - Each audio sample is modified based on the sign of its **original** amplitude:
     - **Positive** samples → Use the *blue* (positive) envelope.
     - **Negative** samples → Use the *red* (negative) envelope.
     - **Zero** samples remain unchanged.
   - Ensures an exact, predictable transformation without interpolation or smoothing.

2. **Undo & Reset**  
   - **`u`**: Reverts the envelope to its state before your last mouse click.  
   - **`r`**: Resets both the positive and negative envelopes to zero.

3. **Real-Time Audio Preview**  
   - **`p`**: Applies the envelope to a temporary array and plays it in real time using [sounddevice](https://pypi.org/project/sounddevice/).  
   - Allows you to hear changes without leaving the drawing interface.

4. **Partial Redraw (Blitting)**  
   - Improves performance by only redrawing the changed envelope lines as you move the mouse.

5. **Background Waveform Reference**  
   - The original audio waveform is plotted in **light gray**, helping you align your envelope drawing to the natural dynamics of the sound.

6. **Stereo→Mono & Normalization**  
   - Automatically converts stereo files to mono.  
   - Normalizes the waveform to **[-1, 1]**.

7. **Optional Amplitude Clamping**  
   - If you find the final audio is “blowing up,” you can uncomment the clamping line in `update_drawing`:
     ```python
     # amp = max(-1, min(1, event.ydata))
     ```
   - This prevents drawn amplitudes from exceeding **[-1, 1]**.

8. **Two PNG Outputs**  
   - **`future_[filename].png`:** Saves the final state of the drawing canvas (the envelope lines on top of the background waveform).  
   - **`comparison_[filename].png`:** Plots the original waveform (blue) and the adjusted waveform (green) in separate subplots for easy visual comparison.

9. **Data & Audio Output**  
   - **CSV & .npy:** Envelope data is saved as a CSV file and two .npy files (`_pos.npy` & `_neg.npy`) for positive/negative envelopes.  
   - **WAV File:** The adjusted audio is written to `future_[filename].wav` in the same folder, using 16-bit PCM format.  
   - **Comparison Plot:** Displayed on-screen and saved as `comparison_[filename].png`.

## Installation

1. **Python 3.x**  
2. [NumPy](https://numpy.org/)  
3. [Matplotlib](https://matplotlib.org/)  
4. [SciPy](https://www.scipy.org/)  
5. [sounddevice](https://pypi.org/project/sounddevice/)

Install dependencies via pip:
```bash
pip install numpy matplotlib scipy sounddevice
