import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# Read .wav file
sample_rate, data = wavfile.read('input.wav')

# Ensure data is in mono
if len(data.shape) > 1:
    data = data.mean(axis=1)

# Find positive and negative peaks
positive_peaks = data[data > 0]
negative_peaks = data[data < 0]

# Calculate average of peaks
average_positive = np.mean(positive_peaks)
average_negative = np.mean(negative_peaks)

# Create a copy of the data to modify
modified_data = data.copy()
modified_data[modified_data > 0] = average_positive
modified_data[modified_data < 0] = average_negative

# Save modified signal to a new .wav file
wavfile.write('flattened.wav', sample_rate, modified_data.astype(np.int16))

# Plot original and modified signals
plt.figure(figsize=(12, 6))

# Plot original signal
plt.subplot(2, 1, 1)
plt.plot(data, label='Original Signal')
plt.title('Original Signal')
plt.xlabel('Sample')
plt.ylabel('Amplitude')
plt.legend()

# Plot modified signal
plt.subplot(2, 1, 2)
plt.plot(modified_data, label='Modified Signal')
plt.title('Modified Signal')
plt.xlabel('Sample')
plt.ylabel('Amplitude')
plt.legend()

plt.tight_layout()
plt.show()
