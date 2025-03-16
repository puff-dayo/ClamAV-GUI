import platform

import darkdetect
import ctypes as ct


def refresh_window(window, dx=1, dy=1):
    current_geometry = window.geometry()
    new_width = current_geometry.width() + dx
    new_height = current_geometry.height() + dy
    window.setGeometry(current_geometry.x(), current_geometry.y(), new_width, new_height)
    window.setGeometry(current_geometry.x(), current_geometry.y(), current_geometry.width(),
                     current_geometry.height())

def dark_title_bar(hwnd, use_dark_mode=False):
    if platform.system() != "Windows":
        print("Dark mode is only supported on Windows.")
        return

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 1 if use_dark_mode else 0
    value = ct.c_int(value)
    result = set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))
    if result != 0:
        print(f"Failed to set dark mode: {result}")

def set_dark_bar(window):
    winId = window.winId()
    dark_title_bar(winId, use_dark_mode=darkdetect.isDark())

def apply_dark(window):
    set_dark_bar(window)
    refresh_window(window)