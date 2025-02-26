# Envelope Drawing & Audio Modification Tool

This Python tool allows you to interactively draw envelope curves over an audio waveform from a WAV file. With integrated color picking, you can customize the appearance of the drawing canvas and final outputs. Once you have drawn the envelope, the tool can preview the modified audio, save the envelope data as a CSV file, and output several images (including a final drawing, a natural language version, and a comparison of the original and modified waves) along with a modified audio WAV file.

## Features

- **Custom Color Picking:**  
  Choose custom colors for the drawing canvas, positive envelope, and negative envelope using an interactive ANSI color swatch display.

- **Interactive Drawing:**  
  Draw envelope curves on the audio waveform using your mouse.  
  - **Keyboard Commands:**  
    - `p`: Preview the modified audio.
    - `r`: Reset the envelope.
    - `u`: Undo the last stroke.

- **File Management:**  
  - The input WAV file is copied to a new folder (named after the file, without its extension).
  - The following outputs are saved in that folder:
    - `final_drawing.png`: The canvas after the first color adjustment.
    - `envelope.csv`: CSV data of the drawn envelope.
    - A modified audio file (WAV) with the applied envelope.
    - `natural_lang.png`: Image after a second round of color picking.
    - `wave_comparison.png`: A side-by-side comparison image of the original and modified waveforms.

- **Continuous Processing:**  
  After finishing with one file, you are prompted whether you want to process another file.

## Requirements

- Python 3.x
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [SciPy](https://www.scipy.org/) (for WAV file I/O)
- [sounddevice](https://python-sounddevice.readthedocs.io/) (for audio preview)
- Standard libraries: `os`, `sys`, `shutil`, `csv`

## Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
