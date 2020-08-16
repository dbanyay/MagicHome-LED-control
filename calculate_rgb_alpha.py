# pacmd load-module module-loopback latency_msec=1
# pavucontrol

import numpy as np
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
                 start_hue: int = HUECOLORS.GREEN,
                 inverse_hue: bool = True,
                 num_colors: int = 200,
                 alpha_rms_max: int = 3000,
                 alpha_min: int = 0.01,
                 audio_min_freq: int = 40,
                 audio_max_freq: int = 1000,
                 is_verbose: bool = True):

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
        calculated_hue, dominant_freq = self.color_mapping(Sxx, f, mode='log')

        # calculate RMS to control light intensity
        rms = np.sqrt(np.mean(np.array(c_weighted_cur_segment, dtype=np.float) ** 2))

        if rms / self.alpha_rms_max < self.alpha_min:
            alpha = 2
        elif rms / self.alpha_rms_max > 1:
            alpha = 1
        else:
            alpha = rms / self.alpha_rms_max

        if self.is_verbose:
            print(
                f'dominant freq: {dominant_freq:.2f}Hz, calculated hue: {calculated_hue:.2f}, alpha: {alpha:.2f}, measured rms: {rms:.2f}')

        return calculated_hue, alpha

    def create_hue_array(self):
        if self.inverse_hue:
            hue_array = np.arange(self.start_hue, self.start_hue - self.num_colors, step=-1)
            hue_array[hue_array < 0] += 360

        else:
            hue_array = np.arange(self.start_hue, self.start_hue + self.num_colors)
            hue_array[hue_array >= 360] -= 360
        return hue_array

    def color_mapping(self, Sxx, f, mode='lin'):
        dominant_freq = f[np.argmax(Sxx)]
        lin_f = np.linspace(start=self.audio_min_freq, stop=self.audio_max_freq, num=self.num_colors)
        lin_hue = self.closest_freq(lin_f, dominant_freq)
        if mode == 'lin':
            return self.hue_array[lin_hue], dominant_freq
        elif mode == 'log':
            log_f = np.logspace(
                start=np.log10(self.audio_min_freq), stop=np.log10(self.audio_max_freq), num=self.num_colors)

            log_hue = self.closest_freq(log_f, dominant_freq)
            return self.hue_array[log_hue] / 360, dominant_freq

    def closest_freq(self, freq_array, K):
        idx = (np.abs(freq_array - K)).argmin()
        return idx
