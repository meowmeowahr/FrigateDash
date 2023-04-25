import cv2
import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class FrameWorker(QThread):
    # noinspection PyArgumentList
    ImageUpdated = pyqtSignal(QImage)
    ImageUpdated2 = pyqtSignal(QImage)

    def __init__(self, url, resolution) -> None:
        # noinspection PyArgumentList
        super(FrameWorker, self).__init__()

        self.url = url
        self.resolution = resolution
        self.__thread_active = True
        self.__thread_pause = False
        self.time_elapsed = 0
        self.prev_time = 0
        self.fps = 5

    def run(self) -> None:
        cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)

        if cap.isOpened():
            while self.__thread_active:
                ret, frame = cap.read()

                self.time_elapsed = time.time() - self.prev_time

                if self.time_elapsed > 1. / self.fps:
                    self.prev_time = time.time()

                    if ret:
                        height, width, channels = frame.shape
                        bytes_per_line = width * channels

                        cv_rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                        qt_rgb_image_scaled = qt_rgb_image.scaled(self.resolution[0], self.resolution[1],
                                                                  Qt.AspectRatioMode.KeepAspectRatio)

                        self.ImageUpdated.emit(qt_rgb_image_scaled)
                        self.ImageUpdated2.emit(qt_rgb_image_scaled)
                    else:
                        break
        cap.release()
        self.quit()

    def stop(self) -> None:
        self.__thread_active = False

    def pause(self) -> None:
        self.__thread_pause = True

    def unpause(self) -> None:
        self.__thread_pause = False


class Display(QLabel):
    def __init__(self) -> None:
        super(Display, self).__init__()

        self.url = None
        self.worker = None

        self.setAlignment(Qt.AlignCenter)
        self.resize(200, 200)

    def setUrl(self, url: str):
        self.url = url

    def run(self, resolution):
        self.worker = FrameWorker(self.url, resolution)
        self.worker.ImageUpdated.connect(self.updateImg)
        self.worker.start()

        return self.worker

    def updateImg(self, image):
        self.setPixmap(QPixmap.fromImage(image).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                               transformMode=Qt.TransformationMode.SmoothTransformation))

    def closeEvent(self, event) -> None:
        if self.worker.isRunning():
            self.worker.quit()
        event.accept()
