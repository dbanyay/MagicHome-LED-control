import pyaudio # Soundcard audio I/O access library
import wave # Python 3 module for reading / writing simple .wav files
import numpy as np
from matplotlib import pyplot as plt

# Setup channel info
CHUNK = 256
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"

# Startup pyaudio instance
audio = pyaudio.PyAudio()

for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    print(info)
    if info['name'] == 'pulse':
        device_index = info['index']

    elif 'Analog' in info['name']:
        device_index = info['index']

# start Recording
stream = audio.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK)

print("recording...")
frames = []

# Record for RECORD_SECONDS
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    wav_chunk = np.frombuffer(data, dtype=np.int16)
    frames.append(data)
print("finished recording")


# Stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

# Write your new .wav file with built in Python 3 Wave module
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()