# Integrated Waveform Tool

## Overview

The Integrated Waveform Tool is an interactive Python utility that lets you process audio WAV files by drawing custom envelopes directly onto their waveforms. It normalizes the audio, allows real-time envelope drawing and preview, and then applies the drawn envelope to modify the audio. The tool outputs several files for further analysis and usage.

## Features

- **Interactive Envelope Drawing:**  
  Draw separate envelopes for the positive and negative portions of the waveform using your mouse.
  
- **Real-Time Audio Preview:**  
  Preview the adjusted audio on the fly before saving.

- **Custom Color Selection:**  
  Choose colors for the drawing background, positive envelope, and negative envelope via a text-based preset palette.

- **Multiple Output Files:**  
  - **Drawn Envelope PNG:** `future_[basename].png` – shows your drawn envelope over the waveform.
  - **Comparison PNG:** `comparison_[basename].png` – a side-by-side comparison of the original versus adjusted waveforms.
  - **Modified Waveform PNG:** `modified_wave_[basename].png` – displays only the modified (adjusted) waveform.
  - **Modified Audio WAV:** `future_[basename].wav` – the audio file with the envelope applied.
  - **Envelope Data:** CSV and NumPy `.npy` files with the envelope data.

- **Undo and Reset Options:**  
  Use keyboard shortcuts (`u` for undo and `r` for reset) during the drawing phase.

## Dependencies

- Python 3.x
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [SciPy](https://www.scipy.org/) (for WAV file I/O)
- [SoundDevice](https://python-sounddevice.readthedocs.io/) (for audio preview)
- (Optional) Standard libraries such as `os`, `shutil`, and `csv`

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/integrated-waveform-tool.git
   cd integrated-waveform-tool
