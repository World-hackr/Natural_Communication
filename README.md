🍘Natural_Language.py
Advanced  Wave Envelope Editor
Table of Contents
Section	Description
Overview	High-level description of the tool
Features	Key features summarized in tables
Installation	How to install prerequisites and set up
Usage	Step-by-step instructions with tables
How It Works	Explanations for non-technical and technical users
Sample Commit Message	A sample commit message for version control
Overview
This tool allows you to create or import a WAV file and interactively draw custom envelopes over its waveform. After editing, it exports three images:

Final Drawing: A faithful capture of your drawing phase.
Natural Language Visualization: A continuous, strictly sign‑colored waveform image.
Wave Comparison: An overlay of the original and modified waveforms for easy comparison.
The exported images are intended to exactly match what you see on the drawing window.

Features
Feature	Description
Custom Wave Generation	Generate a waveform using presets (sine, square, triangle, sawtooth) or manual input (frequency, samples per wavelength, periods).
Existing File Import	Load an existing WAV file for processing.
Interactive Envelope Drawing	Draw custom envelopes on the displayed waveform using your mouse, with preview, undo, and reset options.
Color Customization	Select colors for the drawing canvas, positive envelope, and negative envelope through an interactive console-based color picker.
Export Options	Export your work as three PNG images: final drawing, natural language visualization (strict sign‑colored), and wave comparison (overlay).
Consistent Aspect Ratio	The natural_lang and wave_comparison images are exported with axis limits and aspect ratio set to match the interactive drawing window.
Installation
Step	Instructions
Prerequisites	Python 3.x and the following packages: matplotlib, numpy, scipy, sounddevice.
Installation	Use pip to install required packages:
bash<br>pip install matplotlib numpy scipy sounddevice<br>
Download	Clone or download the repository containing the code.
Usage
Wave Generation and Import
Option	Description
Custom Generation	Choose a preset (sine, square, triangle, sawtooth) or manually enter parameters to generate a new wave.
Existing Import	Provide the path to an existing WAV file to load and process.
Color Customization
Component	Description
Background Color	Sets the color of the drawing canvas.
Positive Envelope	Sets the color for positive parts of the envelope.
Negative Envelope	Sets the color for negative parts of the envelope.
The color picker displays a table with color names, hex codes, and a swatch for easy selection.

Interactive Envelope Drawing
Key	Action
p	Preview the modified audio.
r	Reset the envelope (clear the current drawing).
u	Undo the last drawn stroke.
Export Phases
Export Type	Description
Final Drawing	Exports an image (final_drawing.png) exactly as seen during the drawing phase. (This export remains unchanged.)
Natural Language	Exports a PNG (natural_lang.png) where the waveform is rendered using strict sign-based coloring.
Wave Comparison	Exports a PNG (wave_comparison.png) overlaying the original and modified waveforms for comparison.
Note: The natural_lang and wave_comparison exports include a reset of axis limits and aspect ratio to match the interactive window view.

How It Works
Layman Explanation
Concept	Explanation
Input Wave	You either create a new sound wave or load an existing one, which is displayed as a wavy line.
Drawing on the Wave	You use your mouse to "draw" on the wave—like marking on a paper—to change its shape.
Preview and Adjust	You can preview your changes, undo mistakes, or reset the drawing if needed.
Export	When done, the tool saves images that look exactly like your drawing window: one is a final capture, another shows a smooth, colored continuous line, and the third compares the original and modified waves side by side.
Technical Explanation
Component	Technical Details
Wave Generation/Import	Uses NumPy and SciPy to generate or load a WAV file and normalize its waveform.
Color Picker	A console-based color picker prints color options (with ANSI swatches) and lets you select custom colors for the drawing canvas and envelopes.
Interactive Drawing	The EnvelopePlot class handles mouse events (press, move, release) to allow real-time envelope drawing with a blit-based update for performance.
Export Routines	Three separate export phases produce PNG images:
- Final Drawing: a direct capture of the drawing phase.
- Natural Language Visualization: uses a strict sign‑subdivision algorithm to create a continuous colored line.
- Wave Comparison: overlays the original and modified waveforms.
Axis limits and aspect ratios are reset for the latter two exports to match the interactive view.
