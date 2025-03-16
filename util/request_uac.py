import ctypes
import sys


def request_uac_or_skip():
    ctypes.windll.shell32.IsUserAnAdmin() or ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1) > 32 and sys.exit()


def request_uac_or_exit():
    ctypes.windll.shell32.IsUserAnAdmin() or (ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1) > 32, sys.exit())
