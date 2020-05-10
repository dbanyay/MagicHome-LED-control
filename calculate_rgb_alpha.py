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
    RANDOM = -1


class AudioController():
    def __init__(self,
                 fs: int = 44100,
                 nperseg: int = 2048,
                 start_hue: int = HUECOLORS.RED,
                 inverse_hue: bool = False,
                 num_colors: int = 300,
                 alpha_rms_max: int = 1000,
                 alpha_min: int = 0.1,
                 audio_min_freq: int = 40,
                 audio_max_freq: int = 1000,
                 is_verbose: bool=True):

        # audio related parameters
        self.fs = fs
        self.nperseg = nperseg
        self.alpha_rms_max = alpha_rms_max
        self.audio_min_freq = audio_min_freq
        self.audio_max_freq = audio_max_freq

        # light related parameters
        self.alpha_min = alpha_min
        self.num_colors = num_colors
        self.start_hue = start_hue
        self.inverse_hue = inverse_hue
        self.hue_array = self.create_hue_array()

        self.is_verbose = is_verbose

    def calculate_rgb(self, cur_segment):

        # perform C weighting filter twice
        c_weighted_cur_segment = weight_signal(cur_segment, weighting="C")
        c_weighted_cur_segment = weight_signal(c_weighted_cur_segment, weighting="C")

        # Fourier-transform signal
        f, t, Sxx = spectrogram(c_weighted_cur_segment, fs=self.fs, nperseg=self.nperseg)
        calculated_hue = self.color_mapping(Sxx, f) / 360

        # calculate RMS to control light intensity
        rms = np.sqrt(np.mean(np.array(c_weighted_cur_segment, dtype=np.float) ** 2))

        if rms / self.alpha_rms_max < self.alpha_min:
            alpha = 2
        elif rms / self.alpha_rms_max > 1:
            alpha = 1
        else:
            alpha = rms / self.alpha_rms_max


        if self.is_verbose:
            print(f'calculated hue: {calculated_hue}, alpha: {alpha}, measured rms: {rms}')

        rgb_norm = colorsys.hls_to_rgb(calculated_hue, alpha / 2, 1)

        r = int(np.round(rgb_norm[0] * 255))
        g = int(np.round(rgb_norm[1] * 255))
        b = int(np.round(rgb_norm[2] * 255))

        return r, g, b

    def create_hue_array(self):
        if self.inverse_hue:
            hue_array = np.arange(self.start_hue, self.start_hue - self.num_colors, step=-1)
            hue_array[hue_array < 0] += 360

        else:
            hue_array = np.arange(self.start_hue, self.start_hue + self.num_colors)
            hue_array[hue_array >= 360] -= 360
        return hue_array

    def color_mapping(self, Sxx, f):
        dominant_freq = f[np.argmax(Sxx)]
        lin_f = np.linspace(start=self.audio_min_freq, stop=self.audio_max_freq, num=self.num_colors)
        lin_hue = self.closest_freq(lin_f, dominant_freq)
        return self.hue_array[lin_hue]

    def closest_freq(self, freq_array, K):
        idx = (np.abs(freq_array - K)).argmin()
        return idx
