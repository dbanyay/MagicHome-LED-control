import pyaudio
from collections import deque
import numpy as np


class AudioInputDevices:
    MIC = "default"
    STEREO_MIX = "pulse"


class AudioStream:
    def __init__(self, audio_device=AudioInputDevices.MIC, format=pyaudio.paInt16, channels=1, rate=44100, chunk=256):

        self.audio_device = audio_device
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk

        self.audio = pyaudio.PyAudio()

        device_index = None
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)

            if info['name'] == audio_device:
                device_index = info['index']

        if device_index == None:
            print(f'Audio device {audio_device} not found!')

        # start Recording
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      input_device_index=device_index,
                                      frames_per_buffer=self.chunk)

        print(f"latency: {self.stream.get_input_latency()}")

    def read_audio(self):
        data = self.stream.read(self.chunk)
        wav_chunk = np.frombuffer(data, dtype=np.int16)
        return wav_chunk

if __name__ == '__main__':
    audio_stream = AudioStream(audio_device=AudioInputDevices.STEREO_MIX)
    print(audio_stream.read_audio())
