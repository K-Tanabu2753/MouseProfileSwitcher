import json
import ctypes
import sys
import winreg
import os

from PySide6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QStyle
)

from PySide6.QtGui import QAction,QIcon

from settings_dialog import SettingsDialog
from pathlib import Path

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent
BASE_DIR = get_base_dir()
SETTINGS_FILE = BASE_DIR / "settings.json"


SPI_SETMOUSESPEED = 0x0071


def set_mouse_speed(speed: int):
    speed = max(1, min(20, speed))

    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETMOUSESPEED,
        0,
        speed,
        0
    )

def set_scroll_lines(lines: int):

    lines = max(1, min(100, lines))

    SPI_SETWHEELSCROLLLINES = 0x0069

    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETWHEELSCROLLLINES,
        lines,
        None,
        0
    )

    print(f"Scroll Lines = {lines}")



def load_settings():
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            settings,
            f,
            ensure_ascii=False,
            indent=2
        )

class TrayApp:

    def __init__(self):

        self.settings = load_settings()

        self.current_profile = self.settings.get(
            "current_profile",
            self.settings["profiles"][0]["name"]
        )

        self.profile_actions = {}

        self.tray = QSystemTrayIcon()

        icon = QApplication.style().standardIcon(
            QStyle.StandardPixmap.SP_ComputerIcon
        )

        self.tray.setIcon((QIcon(str(BASE_DIR / "trackball.ico"))))

        self.build_menu()

        self.tray.setToolTip("Mouse Profile Switcher")
        self.tray.show()

        profile = self.get_profile(
            self.current_profile
        )

        if profile:
            set_mouse_speed(profile["speed"])

    def get_profile(self, name):

        for profile in self.settings["profiles"]:
            if profile["name"] == name:
                return profile

        return None

    def build_menu(self):

        self.tray.setContextMenu(None)

        menu = QMenu()
        self.menu = menu

        self.status_action = QAction(
            f"現在: {self.current_profile}"
        )

        self.status_action.setEnabled(False)

        menu.addAction(self.status_action)
        menu.addSeparator()

        self.profile_actions = {}

        for profile in self.settings["profiles"]:

            name = profile["name"]
            speed = profile["speed"]
            scroll_lines = profile.get("scroll_lines", 5)

            action = QAction(
                f"{name} ({speed})"
            )

            action.setCheckable(True)

            if name == self.current_profile:
                action.setChecked(True)

            action.triggered.connect(
                lambda checked=False,
                n=name,
                s=speed,
                sl=scroll_lines: self.apply_profile(n, s, sl    )
            )

            self.profile_actions[name] = action

            menu.addAction(action)

        menu.addSeparator()

        self.settings_action = QAction("設定...")
        self.settings_action.triggered.connect(
            self.open_settings
        )

        menu.addAction(self.settings_action)

        menu.addSeparator()

        self.exit_action = QAction("終了")
        self.exit_action.triggered.connect(
            QApplication.quit
        )

        menu.addAction(self.exit_action)

        self.tray.setContextMenu(menu)

    def apply_profile(self, name, speed, scroll_lines):

        set_mouse_speed(speed)

        if scroll_lines is not None:
            set_scroll_lines(scroll_lines)

        self.current_profile = name

        self.settings["current_profile"] = name

        save_settings(self.settings)

        self.status_action.setText(
            f"現在: {name}"
        )

        for action in self.profile_actions.values():
            action.setChecked(False)

        self.profile_actions[name].setChecked(True)

        self.tray.showMessage(
            "Mouse Profile Switcher",
            f"{name} を適用しました (速度: {speed})"
        )

    def open_settings(self):

        dialog = SettingsDialog(
            self.settings
        )

        dialog.exec()
        
    
        self.settings = load_settings()

        self.current_profile = self.settings.get(
            "current_profile",
            self.settings["profiles"][0]["name"]
        )

        self.build_menu()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)

    tray_app = TrayApp()

    sys.exit(app.exec())