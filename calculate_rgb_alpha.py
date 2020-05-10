# pacmd load-module module-loopback latency_msec=1
# pavucontrol

import numpy as np
from time import perf_counter
import colorsys
from scipy.signal import spectrogram
from matplotlib import pyplot as plt
from collections import deque
from colorsys import hls_to_rgb
from pyfilterbank.splweighting import weight_signal

NUM_COLORS = 300  # range from 0 to NUM_COLORS
# ALPHA_MAX = 32768
ALPHA_MAX = 1000

ALPHA_MIN = 0.1
AUDIO_FS = 44100
MIN_FREQ = 40
MAX_FREQ = 1000


def calculate_rgb(cur_segment, fs=AUDIO_FS, nperseg=512):
    c_weighted_cur_segment = weight_signal(cur_segment, weighting="C")
    # a_weighted_cur_segment = cur_segment
    c_weighted_cur_segment = weight_signal(c_weighted_cur_segment, weighting="C")

    f, t, Sxx = spectrogram(c_weighted_cur_segment, fs=fs, nperseg=nperseg)
    calculated_hue = logarithmic_mapping(Sxx, f) / 360

    rms = np.sqrt(np.mean(np.array(c_weighted_cur_segment, dtype=np.float) ** 2))
    # print(calculated_hue, rms)

    if rms / ALPHA_MAX < ALPHA_MIN:
        alpha = 2
    elif rms / ALPHA_MAX > 1:
        alpha = 1
    else:
        alpha = rms / ALPHA_MAX

    rgb_norm = colorsys.hls_to_rgb(calculated_hue, alpha / 2, 1)

    rgb = (int(np.round(rgb_norm[0] * 255)), int(np.round(rgb_norm[1] * 255)), int(np.round(rgb_norm[2] * 255)))

    r = int(rgb[0])
    g = int(rgb[1])
    b = int(rgb[2])

    return r, g, b


def logarithmic_mapping(Sxx, f):
    dominant_freq = f[np.argmax(Sxx)]
    # print(dominant_freq)
    # log_f = np.logspace(start=np.log10(MIN_FREQ), stop=np.log10(MAX_FREQ), num=NUM_COLORS)
    log_f = np.linspace(start=MIN_FREQ, stop=MAX_FREQ, num=NUM_COLORS)

    log_hue = closest_freq(log_f, dominant_freq)
    return log_hue


def closest_freq(freq_array, K):
    idx = (np.abs(freq_array - K)).argmin()
    return idx
