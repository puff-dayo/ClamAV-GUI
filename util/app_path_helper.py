import os
import string
import sys

EXE_PATH = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
    os.path.abspath(__file__))
EXE_PATH = os.path.normpath(os.path.join(EXE_PATH)) if getattr(sys, 'frozen', False) else os.path.normpath(
    os.path.join(EXE_PATH, "../"))

TEMP_PATH = os.path.dirname(os.path.abspath(__file__))
TEMP_PATH = os.path.normpath(os.path.join(TEMP_PATH, "../"))

RES_PATH = os.path.join(TEMP_PATH, 'res')


def find_clamav():
    dir_name = "ClamAV"

    def init_clamav(path):
        def check_and_create(file_path):
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    pass  # Create an empty file
                return True
            else:
                return False

        def check_and_write(file_path, content):
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write(content)
                return True
            else:
                return False

        check_and_create(os.path.join(path, "clamd.conf"))
        check_and_write(os.path.join(path, "freshclam.conf"), "DatabaseMirror database.clamav.net")

    for drive in string.ascii_uppercase[2:]:
        path = f"{drive}:\\Program Files\\{dir_name}"
        if os.path.exists(path):
            # print(f"{dir_name} found at {path}")
            os.environ["PATH"] = os.environ["PATH"] + os.pathsep + path
            init_clamav(path)
            return path


if __name__ == '__main__':
    print(EXE_PATH)
    print(TEMP_PATH)
