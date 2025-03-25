.venv\Scripts\activate
uv sync
uv run pyinstaller -F -n ClamAVTk -w --hidden-import darkdetect --add-data "util;util" --add-data "res;res" --icon="res/svg2png_x2.png" "main.py"