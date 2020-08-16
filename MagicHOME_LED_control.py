from flux_led import WifiLedBulb, BulbScanner
from audio_stream import AudioStream, AudioInputDevices
from calculate_rgb_alpha import AudioController
import numpy as np
from collections import deque
from enum import auto, Enum
from capture_screen_color import MonitorColorController
import colorsys


class LEDControlMode(Enum):
    AUDIO_STEREO_MIX = auto()
    AUDIO_MIC = auto()
    MONITOR_COLOR = auto()


class LEDController():
    def __init__(self,
                 mode: LEDControlMode = LEDControlMode.AUDIO_STEREO_MIX,
                 rgb_buffer_len: int = 8,
                 alpha_buffer_length=8,
                 silence_buffer_length=2):

        self.mode = mode

        if self.mode == LEDControlMode.AUDIO_STEREO_MIX:

            self.controller = AudioController()
            self.audio_stream = AudioStream(audio_device=AudioInputDevices.STEREO_MIX, chunk=self.controller.nperseg)

        elif self.mode == LEDControlMode.MONITOR_COLOR:
            self.controller = MonitorColorController()
            rgb_buffer_len = 2

        self.hue_buffer = deque([0 for _ in range(rgb_buffer_len)], maxlen=rgb_buffer_len)
        self.alpha_buffer = deque([2 for _ in range(alpha_buffer_length)], maxlen=alpha_buffer_length)

        self.silence_buffer = deque(
            ['music' for _ in range(int(silence_buffer_length / self.controller.nperseg * self.controller.fs))],
            maxlen=int(silence_buffer_length / self.controller.nperseg * self.controller.fs))

        self.state = 'music'

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
            calculated_hue, calculated_alpha = self.controller.calculate_rgb(wav_chunk)

            self.hue_buffer.appendleft(calculated_hue)
            self.alpha_buffer.appendleft(calculated_alpha)

            hue_mean = np.mean(self.hue_buffer)
            alpha_mean = np.mean(self.alpha_buffer)

            rgb_norm = colorsys.hls_to_rgb(hue_mean, alpha_mean / 2, 1)

            r = int(np.round(rgb_norm[0] * 255))
            g = int(np.round(rgb_norm[1] * 255))
            b = int(np.round(rgb_norm[2] * 255))

            for bulb in self.bulbs:
                bulb.setRgb(r, g, b)

            if alpha_mean == 2.0:
                self.silence_buffer.appendleft('silence')
            else:
                self.silence_buffer.appendleft('music')

            if len(set(self.silence_buffer)) == 1:
                if self.state == 'music' and self.silence_buffer[0] == 'silence':
                    self.state = 'silence'
                    self.controller.start_hue = np.random.randint(0,359)
                    self.controller.hue_array = self.controller.create_hue_array()
                    print(f'\n\n\nnew start hue: {self.controller.start_hue}\n\n\n')
                elif self.state == 'silence' and self.silence_buffer[0] == 'music':
                    self.state = 'music'



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
