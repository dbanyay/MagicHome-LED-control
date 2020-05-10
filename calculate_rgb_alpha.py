# pacmd load-module module-loopback latency_msec=1
# pavucontrol

import numpy as np
import colorsys
from scipy.signal import spectrogram
from pyfilterbank.splweighting import weight_signal


class HUECOLORS():
    RED = 0
    ORANGE = 35
    YELLOW = 60
    GREEN = 100
    CYAN = 175
    BLUE = 240
    MAGENTA = 310


def calculate_rgb(cur_segment, fs: int = 44100,
                  nperseg: int = 512,
                  start_hue: HUECOLORS = HUECOLORS.RED,
                  reverse_hue: bool = False):
    output_hue_array = create_hue_array(start_hue, reverse_hue)

    # perform C weighting filter twice
    c_weighted_cur_segment = weight_signal(cur_segment, weighting="C")
    c_weighted_cur_segment = weight_signal(c_weighted_cur_segment, weighting="C")

    # Fourier-transform signal
    f, t, Sxx = spectrogram(c_weighted_cur_segment, fs=fs, nperseg=nperseg)
    calculated_hue = color_mapping(Sxx, f, output_hue_array) / 360

    # calculate RMS to control light intensity
    rms = np.sqrt(np.mean(np.array(c_weighted_cur_segment, dtype=np.float) ** 2))

    if rms / ALPHA_MAX < ALPHA_MIN:
        alpha = 2
    elif rms / ALPHA_MAX > 1:
        alpha = 1
    else:
        alpha = rms / ALPHA_MAX

    rgb_norm = colorsys.hls_to_rgb(calculated_hue, alpha / 2, 1)

    r = int(np.round(rgb_norm[0] * 255))
    g = int(np.round(rgb_norm[1] * 255))
    b = int(np.round(rgb_norm[2] * 255))

    return r, g, b


def create_hue_array(start_hue, inverse_hue):
    if inverse_hue:
        hue_array = np.arange(start_hue, start_hue - NUM_COLORS, step=-1)
        hue_array[hue_array < 0] += 360

    else:
        hue_array = np.arange(start_hue, start_hue + NUM_COLORS)
        hue_array[hue_array >= 360] -= 360
    return hue_array


def color_mapping(Sxx, f, hue_array):
    dominant_freq = f[np.argmax(Sxx)]
    lin_f = np.linspace(start=MIN_FREQ, stop=MAX_FREQ, num=NUM_COLORS)
    lin_hue = closest_freq(lin_f, dominant_freq)
    return hue_array[lin_hue]


def closest_freq(freq_array, K):
    idx = (np.abs(freq_array - K)).argmin()
    return idx


NUM_COLORS = 300  # range from 0 to NUM_COLORS
# ALPHA_MAX = 32768
ALPHA_MAX = 1000

ALPHA_MIN = 0.1
AUDIO_FS = 44100
MIN_FREQ = 40
MAX_FREQ = 1000
