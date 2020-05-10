from flux_led import WifiLedBulb, BulbScanner
from audio_stream import AudioStream, AudioInputDevices
from calculate_rgb_alpha import AudioController
import numpy as np
from collections import deque
from enum import auto, Enum
from capture_screen_color import MonitorColorController


class LEDControlMode(Enum):
    AUDIO_STEREO_MIX = auto()
    AUDIO_MIC = auto()
    MONITOR_COLOR = auto()


class LEDController():
    def __init__(self,
                 mode: LEDControlMode = LEDControlMode.AUDIO_STEREO_MIX,
                 rgb_buffer_len: int = 5):

        self.mode = mode

        if self.mode == LEDControlMode.AUDIO_STEREO_MIX:

            self.controller = AudioController()
            self.audio_stream = AudioStream(audio_device=AudioInputDevices.STEREO_MIX, chunk=self.controller.nperseg)

        elif self.mode == LEDControlMode.MONITOR_COLOR:
            self.controller = MonitorColorController()
            rgb_buffer_len = 2

        self.rgb_buffer = {'r': deque([255 for _ in range(rgb_buffer_len)], maxlen=rgb_buffer_len),
                           'g': deque([255 for _ in range(rgb_buffer_len)], maxlen=rgb_buffer_len),
                           'b': deque([255 for _ in range(rgb_buffer_len)], maxlen=rgb_buffer_len)}


        # scan available LED devices
        scanner = BulbScanner()
        scanner.scan(timeout=4)
        print("Found LED controllers:")
        [print(bulb) for bulb in scanner.found_bulbs]

        self.bulbs = []
        for bulb in scanner.found_bulbs:
            bulb_info = scanner.getBulbInfoByID(bulb['id'])
            self.bulbs.append(WifiLedBulb(bulb_info['ipaddr']))

    def updateLED(self):

        if self.mode == LEDControlMode.MONITOR_COLOR:

            r, g, b = self.controller.calculate_monitor_average()

            for bulb in self.bulbs:
                bulb.setRgb(r, g, b)

        elif self.mode == LEDControlMode.AUDIO_STEREO_MIX:

            wav_chunk = self.audio_stream.read_audio()
            r, g, b = self.controller.calculate_rgb(wav_chunk)

            self.rgb_buffer['r'].appendleft(r)
            self.rgb_buffer['g'].appendleft(g)
            self.rgb_buffer['b'].appendleft(b)

            r = np.mean(self.rgb_buffer['r'])
            g = np.mean(self.rgb_buffer['g'])
            b = np.mean(self.rgb_buffer['b'])

            for bulb in self.bulbs:
                bulb.setRgb(r, g, b)

        elif self.mode == LEDControlMode.AUDIO_MIC:
            pass
        else:
            raise print(f'Mode {self.mode} not found!')


if __name__ == '__main__':

    # led_controller = LEDController(mode=LEDControlMode.MONITOR_COLOR)
    led_controller = LEDController()

    while 1:
        led_controller.updateLED()

print("Finished!")
