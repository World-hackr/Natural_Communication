This repository provides a Python-based tool for:

- **Generating** or **loading** a wave (custom or existing `.wav`).
- **Drawing** an envelope on that wave (positive/negative) **without** accidental panning/zooming.
- **Applying** color logic to produce three distinct output images:
  - **final_drawing**  
  - **natural_lang** (strict sign-based coloring, no color leaking)
  - **wave_comparison** (original vs. modified wave)

## Table of Contents

- [Features](#features)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [Space-Signal Context](#space-signal-context)
- [License](#license)

---

## Features

1. **Custom Wave Generation**  
   - Numeric presets (sine, square, triangle, sawtooth) or manual entry (frequency, samples-per-wavelength, periods).
   - **User-defined filename** for the generated `.wav` (no more fixed `"my_custom_wave.wav"`).

2. **No Panning**  
   - We disable the default Matplotlib toolbar so you **only** draw your envelope.  
   - Click-and-drag in the waveform window to modify positive or negative amplitude.

3. **Sign-Based Coloring**  
   - **natural_lang** subdivides each segment at zero crossings to ensure **strict** sign coloring:
     - Values `< 0` → negative color
     - Values `>= 0` → positive color
     - Zero is considered part of the **positive** side
   - No partial overlap or “leak” from negative to positive.

4. **Independent Color Pickers**  
   - Each output (`final_drawing.png`, `natural_lang.png`, `wave_comparison.png`) has **its own** color picker step.  
   - Default negative color in **natural_lang** is set to **cyan** (`#00FFFF`) if you don’t pick custom.

5. **Preview Audio**  
   - Press **p** during drawing to hear how the modified envelope sounds.

6. **Outputs**  
   - A folder named after your wave file (e.g., `my_wave`) is created, containing:
     - **final_drawing.png**  
       Shows the user-drawn envelope on the original wave.
     - **envelope.csv**  
       Numeric data for positive and negative envelopes.
     - **future_XXX.wav**  
       The final, modified audio (where `XXX` is your original `.wav` name).
     - **natural_lang.png**  
       Strict sign-based coloring on a single continuous wave.
     - **wave_comparison.png**  
       One line for the original wave, one line for the modified wave, each in a single color.

---

## Usage

1. **Clone/Download** this repository.
2. **Install** dependencies:
   ```bash
   pip install matplotlib numpy scipy sounddevice
Run the main script:
bash
Copy
Edit
python 🍘Natural_Language.py
Choose:
1 to use an existing .wav file
2 to generate a custom wave
If custom, pick a numeric preset or go manual.
Enter a custom output name (e.g. my_custom_signal.wav).
Drawing:
A Matplotlib window appears, no panning or zooming.
Click and drag in the upper half → positive envelope, lower half → negative envelope.
Keyboard shortcuts:
p = preview (listen to the drawn envelope)
r = reset (erase envelope)
u = undo last stroke
Color Pickers:
For each output file, you can pick custom or default background/positive/negative colors from a vibrant palette.
final_drawing → shows your actual envelope on the wave
natural_lang → single continuous wave with sign-based color logic
wave_comparison → original wave vs. modified wave, each in a single color
Outputs:
A new folder named after your .wav file is created.
Inside, you’ll find .png images and your future_XXX.wav.
Technical Details
Zero-Crossing Subdivision

In the strict_sign_subdivision() function, each segment [i, i+1] is subdivided if the wave crosses zero between samples.
Crossing from negative → positive → color the crossing as positive.
Crossing from positive → negative → color the crossing as negative.
Ensures each sub-segment is purely negative or purely positive.
No Toolbar

We do:
python
Copy
Edit
import matplotlib
matplotlib.rcParams['toolbar'] = 'None'
so you cannot accidentally pan or zoom during the drawing phase.
Sound Playback

We use sounddevice to preview the envelope. If you face issues, ensure your audio device is recognized by sounddevice.
Future_XXX.wav

The final, modified wave after applying your drawn envelope is stored as future_<originalName>.wav.
Space-Signal Context
You can potentially use this tool to shape a wave for space transmission. For example:

Generate a custom wave that encodes data or patterns.
Modify its envelope with this drawing interface to create unique amplitude structures.
Export the .wav and feed it into radio hardware or additional software that broadcasts signals into space.
While this script doesn’t handle actual RF modulation or cosmic distances, it’s a starting point for conceptualizing and shaping waveforms intended for interstellar messaging or other experiments.

