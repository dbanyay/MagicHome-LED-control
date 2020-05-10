import numpy as np
import scipy
from matplotlib import pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import colorsys
from calculate_rgb_alpha import calculate_rgb
from pyfilterbank.splweighting import weight_signal

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

music_path = "/home/dbanyay/Downloads/LEDcontroller/output.wav"
message_freq = 50/1000

fs, wav_mono = wavfile.read(music_path)
nperseg = 256

plt.subplot(211)
plt.plot(wav_mono)

hue_array = []
cur_index = 0
while cur_index < len(wav_mono):
    cur_segment = wav_mono[cur_index:cur_index+nperseg]
    a_weightted_cur_segment = weight_signal(cur_segment)

    r, g, b = calculate_rgb(cur_segment, fs=fs, nperseg=len(cur_segment))

    rgb = (r,g,b)

    rgb_hex_str = rgb_to_hex(rgb)
    rms = np.mean(np.abs(cur_segment))
    plt.axvspan(xmin=cur_index, xmax=cur_index+nperseg, facecolor=rgb_hex_str, alpha=1)
    cur_index += nperseg

# plt.subplot(211)
# plt.plot(wav_mono)
# plt.subplot(212)
# plt.plot(hue_array)
plt.show()