import platform

import psutil
import wmi


def get_system_info():
    windows_version = platform.win32_ver()[0]

    c = wmi.WMI()
    cpu_model = c.Win32_Processor()[0].Name

    architecture = platform.machine()

    total_memory = psutil.virtual_memory().total / (1024 * 1024 * 1024)

    info = f"Windows Version: {windows_version}\n"
    info += f"CPU Model: {cpu_model}\n"
    info += f"Architecture: {architecture}\n"
    info += f"Total Memory: {total_memory:.2f} GB"

    return info
