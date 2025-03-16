import os
import sys

EXE_PATH = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
    os.path.abspath(__file__))
EXE_PATH = os.path.normpath(os.path.join(EXE_PATH)) if getattr(sys, 'frozen', False) else os.path.normpath(
    os.path.join(EXE_PATH, "../"))

TEMP_PATH = os.path.dirname(os.path.abspath(__file__))
TEMP_PATH = os.path.normpath(os.path.join(TEMP_PATH, "../"))

RES_PATH = os.path.join(TEMP_PATH, 'res')

CLAM_BIN = os.path.join(EXE_PATH, "bin")
os.environ["PATH"] = os.environ["PATH"] + os.pathsep + CLAM_BIN

if __name__ == '__main__':
    print(EXE_PATH)
    print(TEMP_PATH)
