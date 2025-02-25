# Integrated Waveform Envelope Tool

A Python-based tool for processing and modifying audio waveforms by drawing custom envelopes. This tool allows you to load a WAV file, interactively draw envelopes for the positive and negative portions of the waveform, and then apply these envelopes to adjust the audio. It generates several output files, including PNG images of the drawn envelope, a comparison between the original and modified waveforms, and the adjusted audio file. Additionally, it exports envelope data in CSV and NumPy formats.

## Features

- **Interactive Envelope Drawing**: Use your mouse to draw custom envelopes over the waveform.
- **Real-Time Audio Preview**: Preview the effect of your envelope drawing on the audio in real-time.
- **Customizable Colors**: Choose preset color options for the background, positive envelope, and negative envelope for each output image.
- **Multiple Outputs**:
  - PNG of the drawn envelope.
  - Comparison PNG (original vs. drawn envelope).
  - PNG of the modified waveform.
  - Adjusted WAV audio file.
  - Envelope data as CSV and `.npy` files.
- **Stereo-to-Mono Conversion & Normalization**: Automatically handles stereo audio by converting to mono and normalizing the waveform.

## Requirements

- Python 3.x
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [SciPy](https://www.scipy.org/)
- [SoundDevice](https://python-sounddevice.readthedocs.io/)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/integrated-waveform-envelope-tool.git
   cd integrated-waveform-envelope-tool

