import numpy as np
import csv
from scipy.io import wavfile
import matplotlib.pyplot as plt

def adjust_audio_from_csv(audio_file, csv_file, output_file):
    # Read the audio file
    sample_rate, audio_data = wavfile.read(audio_file)
    audio_data = audio_data / np.max(np.abs(audio_data))
    
    # Read the CSV file
    indices = []
    pos_amplitude = []
    neg_amplitude = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            indices.append(int(row['Index']))
            pos_amplitude.append(float(row['Positive Amplitude']))
            neg_amplitude.append(float(row['Negative Amplitude']))
    
    pos_amplitude = np.array(pos_amplitude)
    neg_amplitude = np.array(neg_amplitude)
    
    # Adjust audio data based on CSV values
    adjusted_audio_data = np.zeros_like(audio_data)
    for i in range(len(audio_data)):
        if audio_data[i] > 0:
            adjusted_audio_data[i] = pos_amplitude[i]
        elif audio_data[i] < 0:
            adjusted_audio_data[i] = neg_amplitude[i]
        else:
            adjusted_audio_data[i] = audio_data[i]

    # Save the adjusted audio data to a new file
    wavfile.write(output_file, sample_rate, (adjusted_audio_data * 32767).astype(np.int16))
    
    # Plot the original and adjusted audio waveforms
    plt.figure(figsize=(10, 6))
    
    plt.subplot(2, 1, 1)
    plt.plot(audio_data, color='blue')
    plt.title('Original Audio Waveform')
    
    plt.subplot(2, 1, 2)
    plt.plot(adjusted_audio_data, color='green')
    plt.title('Adjusted Audio Waveform')
    
    plt.tight_layout()
    plt.show()

# Example usage
adjust_audio_from_csv('elephant-225994.wav', 'drawing_output.csv', 'output_audio.wav')
