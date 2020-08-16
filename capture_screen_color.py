import mss
import numpy as np

class MonitorColorController():

    def calculate_monitor_average(self):
        with mss.mss() as sct:
            img = np.asarray(sct.grab(sct.monitors[2]))
            rgb_mean = np.mean(np.mean(img, axis=0), axis=0, dtype=np.int)[:-1]

            return rgb_mean[2], rgb_mean[1], rgb_mean[0]


if __name__ == '__main__':

    controller = MonitorColorController()

    while 1:
        rgb_mean = controller.calculate_monitor_average()
        print(rgb_mean)
