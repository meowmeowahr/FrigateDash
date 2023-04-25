import datetime
import json

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import platform
import sys
import os

import stream_widget

if platform.system() == "Windows":
    from ctypes import byref, c_bool, sizeof, windll
    from ctypes.wintypes import BOOL


def asset_dir(asset: str) -> str:
    return os.path.join(os.path.realpath(os.path.dirname(__file__)), "assets", asset)


def file_dir(file: str) -> str:
    return os.path.join(os.path.realpath(os.path.dirname(__file__)), file)


class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()

        # noinspection PyArgumentList
        self.setPixmap(QPixmap(asset_dir("icon.svg")).scaled(220, 220,
                                                             transformMode=Qt.TransformationMode.SmoothTransformation))
        self.setFixedSize(QSize(220, 220))

        self.close_timer = QTimer(self)
        self.close_timer.singleShot(1500, self.end)

        self.show()

    def end(self):
        window.open()
        self.close()


# noinspection PyArgumentList
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("FrigateDash")
        self.setWindowIcon(QIcon(asset_dir("cctv.svg")))
        self.set_windows_dark(True)

        if settings["no_cursor"]:
            self.setCursor(Qt.CursorShape.BlankCursor)

        with open(asset_dir("style.qss"), "r") as file:
            self.setStyleSheet(file.read())

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.root_layout = QVBoxLayout()
        self.widget.setLayout(self.root_layout)

        self.page_view = PaginationView()
        self.page_view.clockVisible(settings["clock"])
        self.page_view.nameVisible(settings["name"])
        self.page_view.arrowsVisible(settings["arrows"])
        self.page_view.setKeys(settings["keys"])
        self.root_layout.addWidget(self.page_view)

        # camera views
        self.media_views = []
        for index, view in enumerate(settings["views"]):
            self.media_views.append(stream_widget.Display())
            self.media_views[index].setUrl(view["stream"])
            self.media_views[index].run(settings["resolution"])
            self.page_view.addView(self.media_views[index], view["name"])

        # grid view
        self.camera_grid = QGridLayout()
        for index, view in enumerate(self.media_views):
            item = stream_widget.Display()
            item.setUrl(settings["grid_view"]["cameras"][index]["stream"])
            item.run(settings["mini_resolution"])
            self.camera_grid.addWidget(item, index % settings["grid_view"]["size"],
                                       index // settings["grid_view"]["size"])

        self.camera_widget = QWidget()
        self.camera_widget.setLayout(self.camera_grid)
        self.page_view.addView(self.camera_widget, "name")

    def open(self):
        self.showFullScreen()

    def set_windows_dark(self, dark: bool):
        if platform.system() == "Windows":
            windll.LoadLibrary("dwmapi").DwmSetWindowAttribute(int(self.winId()), 20, byref(c_bool(dark)), sizeof(BOOL))


# noinspection PyArgumentList
class PaginationView(QWidget):
    def __init__(self):
        super(PaginationView, self).__init__()

        self.page_names = []

        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.__layout)

        self.pages = QStackedWidget()
        self.__layout.addWidget(self.pages)

        self.pagination_layout = QHBoxLayout()
        self.__layout.addLayout(self.pagination_layout)

        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon(asset_dir("arrow-left-circle.svg")))
        self.back_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.back_button.clicked.connect(self.previous)
        self.back_button.setDisabled(self.pages.currentIndex() == 0)
        self.back_button.setIconSize(QSize(24, 24))
        self.pagination_layout.addWidget(self.back_button)

        self.pagination_layout.addStretch()

        self.__time = QLabel("")
        self.pagination_layout.addWidget(self.__time)

        self.__time_timer = QTimer()
        self.__time_timer.setInterval(500)
        self.__time_timer.timeout.connect(lambda: self.__time.
                                          setText(f"{datetime.datetime.now().strftime('%a, %B %d %I:%M %p')} "
                                                  f"{'|' if self.__name.isVisible() else ''}"))
        self.__time_timer.start()

        self.__name = QLabel("")
        self.pagination_layout.addWidget(self.__name)

        self.pagination_layout.addStretch()

        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon(asset_dir("arrow-right-circle.svg")))
        self.next_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.next_button.clicked.connect(self.next)
        self.next_button.setEnabled(self.pages.currentIndex() == self.pages.count())
        self.next_button.setIconSize(QSize(24, 24))
        self.pagination_layout.addWidget(self.next_button)

    def next(self):
        self.pages.setCurrentIndex(self.pages.currentIndex() + 1)
        self.__name.setText(self.page_names[self.pages.currentIndex()])
        self.next_button.setDisabled(self.pages.currentIndex() == self.pages.count() - 1)
        self.back_button.setDisabled(self.pages.currentIndex() == 0)

    def previous(self):
        self.pages.setCurrentIndex(self.pages.currentIndex() - 1)
        self.__name.setText(self.page_names[self.pages.currentIndex()])
        self.next_button.setDisabled(self.pages.currentIndex() == self.pages.count() - 1)
        self.back_button.setDisabled(self.pages.currentIndex() == 0)

    def addView(self, widget: QWidget, name: str):
        self.pages.addWidget(widget)
        self.page_names.append(name)
        self.__name.setText(self.page_names[self.pages.currentIndex()])
        self.back_button.setDisabled(self.pages.currentIndex() == 0)
        self.next_button.setDisabled(self.pages.currentIndex() == self.pages.count())

    def clockVisible(self, visible: bool):
        self.__time.setVisible(visible)

    def nameVisible(self, visible: bool):
        self.__name.setVisible(visible)

    def arrowsVisible(self, visible: bool):
        self.back_button.setVisible(visible)
        self.next_button.setVisible(visible)

    def setKeys(self, shortcuts: list):
        self.back_button.setShortcut(shortcuts[0])
        self.next_button.setShortcut(shortcuts[1])


def gpio_change(pin):
    if pin == settings["arrow_gpios"][0]:
        window.page_view.previous()
    elif pin == settings["arrow_gpios"][1]:
        window.page_view.next()


if __name__ == "__main__":
    # settings
    with open(file_dir("settings.json"), "r") as s_file:
        settings = json.loads(s_file.read())

    if settings["enable_gpio"]:
        import RPi.GPIO as GPIO

    # io
    if settings["enable_gpio"]:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(settings["arrow_gpios"][0], GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(settings["arrow_gpios"][1], GPIO.IN, GPIO.PUD_UP)

    app = QApplication(sys.argv)
    splash = SplashScreen()
    window = MainWindow()

    if settings["enable_gpio"]:
        GPIO.add_event_detect(settings["arrow_gpios"][0], GPIO.FALLING, callback=gpio_change, bouncetime=200)
        GPIO.add_event_detect(settings["arrow_gpios"][1], GPIO.FALLING, callback=gpio_change, bouncetime=200)

    sys.exit(app.exec())
