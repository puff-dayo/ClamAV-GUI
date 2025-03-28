import locale
import os
import queue
import subprocess
import threading
import tkinter as tk
import webbrowser
from ctypes import windll, wintypes
from ctypes.wintypes import RECT
from datetime import datetime
from idlelib.run import fix_scaling
from tkinter import PhotoImage
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.font import Font

import darkdetect
import psutil
import ttkbootstrap as ttk
from _ctypes import pointer, Structure, sizeof, byref

from util.animation import BreathingCircle
from util.app_path_helper import EXE_PATH, RES_PATH, find_clamav
from util.dark_theme import dark_title_bar
from util.palette import Palette
from util.path_escape import PathUtil
from util.request_uac import request_uac_or_skip
from util.sys_info import get_system_info

VERSION = "0.0.12"


class ClamAVScanner:
    def __init__(self, _root):
        self.root = _root
        self.lang = "en"
        self.texts = self.load_texts()
        self.result_queue = queue.Queue()

        self.history_dir = os.path.join(EXE_PATH, "history")
        os.makedirs(self.history_dir, exist_ok=True)

        self.setup_ui()

        self.icon_path = os.path.join(RES_PATH, "svg2png_x2.png")

        try:
            self.icon_image = PhotoImage(file=self.icon_path)
            self.root.iconphoto(True, self.icon_image)
        except Exception as e:
            print(f"Error al cargar el ícono: {e}")

    def load_texts(self):
        return {
            "es": {
                "app_title": "ClamAV Tk",
                "menu_bar1": "Idioma",
                "menu_bar2": "Ayuda",
                "language_menu1": "English",
                "language_menu2": "Español",
                "help_menu1": "Sobre",
                "tab1": "Análisis",
                "tab2": "Histórico",
                "tab3": "Actualizaciones",
                "tab4": "Config.",
                "button_label1": "Escanear un archivo",
                "button_label2": "Escanear un directorio",
                "button_label3": "Ver historial de escaneos",
                "button_label4": "Actualizar base de datos",
                "checkbox_label1": "Buscar amenazas de manera recursiva",
                "checkbox_label2": "Eliminar amenazas encontradas",
                "version_label": "Versión de ClamAV: ",
                "database_label": "Versión de la base de datos: ",
                "exit_label": "Salir",
                "select_file": "Selecciona un archivo",
                "all_files": "Todos los archivos",
                "text_files": "Archivos de texto",
                "image_files": "Archivos de imagen",
                "select_directory": "Selecciona un directorio",
                "no_history_files": "No hay archivos de historial disponibles.",
                "history_title": "Historial de escaneos",
                "open_result": "Abrir resultado",
                "database_locked": "El proceso de actualización de la base de datos se gestiona automáticamente y se ejecuta en segundo plano. No es necesario invocarlo manualmente.",
                "database_update_error": "Error al actualizar la base de datos:",
                "database_updated": "La base de datos se actualizó correctamente.",
                "database_up_to_date": "La base de datos ya está actualizada y se gestiona automáticamente en segundo plano. No es necesario actualizarla manualmente.",
                "database_updated_on": "Base de datos actualizada el:",
                "current_date": "Fecha actual",
                "version_date": "Fecha de versión",
                "unexpected_version_format": "Formato de versión inesperado.",
                "version_fetch_error": "No se pudo obtener la versión de ClamAV.",
                "generic_error": "Error:",
                "loading_message": "Cargando, por favor espere...",
                "error_message": "Hubo un error. Por favor, intente nuevamente.",
                "about_message": "ClamAV Tkinter es una interfaz gráfica para el escaneo de archivos y directorios usando el motor ClamAV.",
                "scan": "Escaneando",
                "scan_complete": "Escaneo Completado",
                "stdout": "Salida estándar",
                "stderr": "Salida de error",
                "result_saved": "Resultado guardado en",
                "recursive_search": "Buscar amenazas de manera recursiva",
                "delete_threats": "Eliminar amenazas encontradas",

                "version": "Versión",
                "about": "ClamAV GUI es una interfaz gráfica de usuario (GUI) diseñada para facilitar el uso "
                         "de ClamAV, un software antivirus de código abierto. Esta aplicación está inspirada en proyectos "
                         "como ClamWin y ClamTk, y ofrece una experiencia más accesible y visual para los usuarios que desean "
                         "realizar escaneos antivirus en sus sistemas de forma rápida y sencilla."
            },
            "en": {
                "app_title": "ClamAV Tk",
                "menu_bar1": "Language",
                "menu_bar2": "Help",
                "language_menu1": "English",
                "language_menu2": "Español",
                "help_menu1": "About",
                "tab1": "Scan",
                "tab2": "History",
                "tab3": "Update",
                "tab4": "Config",
                "button_label1": "Scan a file",
                "button_label2": "Scan a directory",
                "button_label3": "View scan history",
                "button_label4": "Update DB",
                "checkbox_label1": "Search for threats recursively",
                "checkbox_label2": "Remove found threats",
                "version_label": "ClamAV version: ",
                "database_label": "Database update: ",
                "exit_label": "Exit",
                "select_file": "Select a file",
                "all_files": "All files",
                "text_files": "Text files",
                "image_files": "Image files",
                "select_directory": "Select a directory",
                "no_history_files": "No history files available.",
                "history_title": "Scan history",
                "open_result": "Open result",
                "database_locked": "The database update process is managed automatically and runs in the background. Manual invocation is not necessary.",
                "database_update_error": "Error updating the database:",
                "database_updated": "The database was updated successfully.",
                "database_up_to_date": "The database is already up to date and managed automatically in the background. Manual updates are not necessary.",
                "database_updated_on": "Database version:",
                "current_date": "Current date",
                "version_date": "Version date",
                "unexpected_version_format": "Database not exist or unexpected version format.",
                "version_fetch_error": "Failed to fetch ClamAV version.",
                "generic_error": "Error:",
                "loading_message": "Loading, please wait...",
                "error_message": "An error occurred. Please try again.",
                "about_message": "ClamAV Tkinter is a graphical interface for scanning files and directories using the ClamAV engine.",
                "scan": "Scanning",
                "scan_complete": "Scan Complete",
                "stdout": "Standard output",
                "stderr": "Error output",
                "result_saved": "Result saved at",
                "recursive_search": "Search for threats recursively",
                "delete_threats": "Delete found threats",

                "version": "Version",
                "about": "ClamAV GUI is a graphical user interface designed to simplify the use of ClamAV, an open-source antivirus software. This application is inspired by projects such as ClamWin and ClamTk, and provides a more accessible and visual experience for users who wish to perform antivirus scans on their systems quickly and easily."
            }
        }

    def setup_ui(self):
        self.root.title(self.texts[self.lang]['app_title'])
        self.root.resizable(False, False)
        self.center_window()
        self.create_tabs()

        self.create_scan_frame()
        self.create_history_frame()
        self.create_update_frame()
        self.create_config_frame()

        self.get_version()
        self.get_main_version()

    def center_window(self, window=None, marginx=100, marginy=100):
        if window is None:
            window = self.root

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        window.geometry(f"+{x - marginx}+{y - marginy}")

    def create_config_frame(self):
        # self.language_menu.add_command(
        #     label=self.texts[self.lang]["language_menu1"],
        #     command=lambda: self.change_lang("en")
        # )
        # self.language_menu.add_command(
        #     label=self.texts[self.lang]["language_menu2"],
        #     command=lambda: self.change_lang("es")
        # )

        # self.button_switch_language = ttk.Button(
        #     self.config_frame, text=self.texts[self.lang]["button_label4"],
        #     command=lambda: self.change_lang("es"))
        # self.button_switch_language.pack(fill="x", padx=10, pady=10)

        self.about_info = ttk.Label(
            self.config_frame, text=f"ClamAV Tk - v{VERSION}\nForked and built. 2025-", wraplength=280 * scaler,
            anchor="w")
        self.about_info.pack(padx=10 * scaler, pady=10 * scaler, fill="x")

        self.sys_info = ttk.Label(
            self.config_frame, text=get_system_info(), wraplength=280 * scaler, anchor="w")
        self.sys_info.pack(padx=10 * scaler, pady=10 * scaler, fill="x")

        self.herf = ttk.Label(
            self.config_frame, text=f"Github: puff-dayo/ClamAV-GUI",
            wraplength=280 * scaler,
            cursor="hand2")
        self.herf.pack(padx=10, pady=10)
        self.herf.bind("<ButtonRelease-1>", lambda e: webbrowser.open_new("https://github.com/puff-dayo/ClamAV-GUI"))

        self.checkbox_var_recursive = tk.IntVar(value=1)
        self.checkbox_var_kill = tk.IntVar(value=0)
        self.checkbox_var_processfork = tk.IntVar(value=1)

        self.checkbox_recursive = ttk.Checkbutton(
            self.config_frame, text=self.texts[self.lang]['recursive_search'], variable=self.checkbox_var_recursive)
        self.checkbox_kill = ttk.Checkbutton(
            self.config_frame, text=self.texts[self.lang]['delete_threats'], variable=self.checkbox_var_kill)
        self.checkbox_processfork = ttk.Checkbutton(
            self.config_frame, text="Use all system resources", variable=self.checkbox_var_processfork)

        self.checkbox_recursive.pack(pady=5, padx=5, anchor="w")
        self.checkbox_kill.pack(pady=5, padx=5, anchor="w")
        self.checkbox_processfork.pack(pady=5, padx=5, anchor="w")

    def create_tabs(self):
        self.tabs_notebook = ttk.Notebook(self.root)
        self.tabs_notebook.pack(fill="both", expand=True, pady=0, padx=0)

        self.scan_frame = ttk.Frame(self.tabs_notebook)
        self.history_frame = ttk.Frame(self.tabs_notebook)
        self.update_frame = ttk.Frame(self.tabs_notebook)
        self.config_frame = ttk.Frame(self.tabs_notebook)

        self.tabs_notebook.add(
            self.scan_frame, text="🔍 " + self.texts[self.lang]["tab1"])
        self.tabs_notebook.add(
            self.history_frame, text="📋 " + self.texts[self.lang]["tab2"])
        # self.tabs_notebook.add(
        #     self.update_frame, text="☁️ " + self.texts[self.lang]["tab3"])
        self.tabs_notebook.add(
            self.config_frame, text="🛠 " + self.texts[self.lang]["tab4"])

        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Segoe UI Emoji", 10))
        style.configure("TButton", font=("Segoe UI Emoji", 9))

    def create_scan_frame(self):
        left_frame = ttk.Frame(self.scan_frame)
        right_frame = ttk.Frame(self.scan_frame)
        left_frame.grid(row=0, column=0, sticky="ns", pady=10, padx=10)
        right_frame.grid(row=0, column=1, sticky="nsew", pady=10, padx=10)

        self.scan_frame.grid_columnconfigure(1, weight=1)
        self.scan_frame.grid_rowconfigure(0, weight=1)

        # LEFT FRAME
        emoji_font = Font(family="Segoe UI Emoji", size=10)
        self.button_scan_quick = ttk.Button(
            left_frame, text="⚡" + "Quick scan", command=self.scan_mode_one_file)
        self.button_scan_quick.grid(row=0, column=0, sticky="ew", pady=10, padx=10)
        self.button_scan_quick.config(state="disabled")

        self.button_scan_ram = ttk.Button(
            left_frame, text="💾 " + "Memory", command=self.scan_mode_memory)
        self.button_scan_ram.grid(row=1, column=0, sticky="ew", pady=10, padx=10)

        self.button_scan_all = ttk.Button(
            left_frame, text="💻 " + "All files", command=self.scan_mode_one_file)
        self.button_scan_all.grid(row=2, column=0, sticky="ew", pady=10, padx=10)
        self.button_scan_all.config(state="disabled")

        self.button_scan_a_file = ttk.Button(
            left_frame, text="📄 " + "One file", command=self.scan_mode_one_file)
        self.button_scan_a_file.grid(row=3, column=0, sticky="ew", pady=10, padx=10)

        self.button_scan_a_directory = ttk.Button(
            left_frame, text="📁 " + "Directory", command=self.scan_mode_directory)
        self.button_scan_a_directory.grid(row=4, column=0, sticky="ew", pady=5, padx=10)

        self.button_update_database = ttk.Button(
            left_frame, text="☁️ " + self.texts[self.lang]["button_label4"],
            command=self.update_database, bootstyle="info"
        )
        self.button_update_database.grid(row=5, column=0, sticky="sew", pady=5, padx=10)

        left_frame.grid_rowconfigure(5, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # RIGHT FRAME
        self.scan_info = ttk.Label(
            right_frame, text="No scan is running currently.",
            wraplength=280 * scaler, anchor="center", font=("Arial", 22)
        )
        self.scan_info.grid(row=0, column=0, padx=10, pady=80)

        bg = Palette.BG_DARK if MODE == "light" else Palette.BG_LIGHT
        self.breathing_circle = BreathingCircle()
        self.canvas = self.breathing_circle.create_canvas(right_frame, bg)
        self.canvas.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        self.breathing_circle.set_line_width(10)
        self.breathing_circle.toggle_animation()
        self.breathing_circle.set_color(Palette.COLOR_GREEN)
        self.breathing_circle.set_symbol(2)
        self.breathing_circle.set_size(int(300 * scaler), int(200 * scaler))

        self.main_version = ttk.Label(
            right_frame, text="", anchor="e")
        self.main_version.grid(row=2, column=0, sticky="se", padx=10, pady=10)

        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

    def create_history_frame(self):
        left_frame = ttk.Frame(self.history_frame)
        right_frame = ttk.Frame(self.history_frame)
        left_frame.pack(side="left", fill="y")
        right_frame.pack(side="right", fill="both", expand=True)

        # LEFT FRAME

        history_files = os.listdir(self.history_dir)
        if not history_files:
            pass
        listbox = tk.Listbox(left_frame)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for file in sorted(history_files, reverse=True):
            listbox.insert(tk.END, file)

        def on_select(event):
            index = event.widget.curselection()
            if index:
                selected_value = event.widget.get(index)
                filepath = os.path.join(self.history_dir, selected_value)

                self.history_display.config(text=f"Scan history: {selected_value[:-4]}")

                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.label_history.config(state="normal")
                    self.label_history.delete('1.0', tk.END)  # clear
                    self.label_history.insert('1.0', content)  # insert
                    self.label_history.config(state="disabled")

        listbox.bind("<<ListboxSelect>>", on_select)

        # RIGHT FRAME

        self.history_display = ttk.Labelframe(right_frame, text="Scan history")
        self.history_display.pack(fill="both", expand=1, padx=10, pady=10)

        self.label_history = tk.Text(self.history_display, wrap="word")
        self.label_history.pack(side="left", fill="both", expand=1, padx=10, pady=10)

        scrollbar = tk.Scrollbar(self.label_history, width=20)
        scrollbar.pack(side="right", fill="y")

        self.label_history.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.label_history.yview)

    def create_update_frame(self):
        # self.button_update_database = ttk.Button(
        #     self.update_frame, text=self.texts[self.lang]["button_label4"], command=self.update_database)
        # self.button_update_database.pack(fill="x", padx=10, pady=10)

        self.label_version = ttk.Label(
            self.update_frame, text="", wraplength=280 * scaler)
        self.label_version.pack(padx=10, pady=10)

    def change_lang(self, lang):
        self.lang = lang
        self.update_texts()
        self.get_version()

    def update_texts(self):
        self.root.title(self.texts[self.lang]['app_title'])

        self.tabs_notebook.tab(0, text=self.texts[self.lang]["tab1"])
        self.tabs_notebook.tab(1, text=self.texts[self.lang]["tab2"])
        self.tabs_notebook.tab(2, text=self.texts[self.lang]["tab3"])
        self.tabs_notebook.tab(3, text=self.texts[self.lang]["tab4"])

        self.button_scan_a_file.config(
            text=self.texts[self.lang]["button_label1"])
        self.button_scan_a_directory.config(
            text=self.texts[self.lang]["button_label2"])
        self.button_view_history.config(
            text=self.texts[self.lang]["button_label3"])
        self.button_update_database.config(
            text=self.texts[self.lang]["button_label4"])

        self.checkbox_recursive.config(
            text=self.texts[self.lang]["checkbox_label1"])
        self.checkbox_kill.config(
            text=self.texts[self.lang]["checkbox_label2"])

    def _scan_util_start_thread(self, path, mode):
        args = ['clamscan']

        if mode == "files":
            if self.checkbox_var_recursive.get() == 1:
                args.append('-r')
            if self.checkbox_var_kill.get() == 1:
                args.append('--remove')

        if mode == "memory":
            args.append(f'--memory')
            if self.checkbox_var_kill.get() == 1:
                args.append('--unload')

        if self.checkbox_var_processfork.get() == 1:
            max_scan_size = int((psutil.virtual_memory().free / (1024 * 1024 * 1024)) / 0.6)
            max_scan_size = max(max_scan_size, psutil.cpu_count(logical=True) - 1)
            args.append(f'--max-scansize={max_scan_size}')

        args.append(path)

        try:
            result = subprocess.run(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.result_queue.put(result)
        except Exception as e:
            self.result_queue.put(e)

    def check_scan_status(self):
        try:
            result = self.result_queue.get_nowait()
        except queue.Empty:
            # self.root.after(100, self.check_scan_status, progressbar, newWindow, label_loading)
            self.root.after(100, self.check_scan_status)
            return

        # if progressbar.winfo_exists():
        #     progressbar.stop()
        #     progressbar.destroy()
        #
        # if label_loading.winfo_exists():
        #     label_loading.destroy()

        # after scan complete

        self.breathing_circle.set_symbol(2)
        self.breathing_circle.set_color(Palette.COLOR_GREEN)

        self.scan_info.config(text="No scan is running currently.", )

        # newWindow.title(self.texts[self.lang]['scan_complete'])
        # self.center_window(newWindow, 500, 250)
        #
        # text_square = tk.Text(newWindow, wrap=tk.WORD, font=("Courier New", 12))
        # text_square.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if isinstance(result, Exception):
            # text_square.insert(tk.END, f"{self.texts[self.lang]['error_message']}:\n{str(result)}")
            self.scan_info.config(text=f"Error in scan: {str(result)}")
            self.breathing_circle.set_color(Palette.COLOR_RED)
            self.breathing_circle.set_symbol(1)
        else:
            # text_square.insert(tk.END, f"{self.texts[self.lang]['stdout']}:\n")
            # text_square.insert(tk.END, result.stdout)
            # text_square.insert(tk.END, f"\n{self.texts[self.lang]['stderr']}:\n")
            # text_square.insert(tk.END, result.stderr)

            filepath = self.save_scan_result(result)
            messagebox.showinfo(self.texts[self.lang]['scan_complete'],
                                f"{self.texts[self.lang]['result_saved']} {filepath}")

    def save_scan_result(self, result):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.txt"
        filepath = os.path.join(self.history_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"{self.texts[self.lang]['stdout']}:\n")
            f.write(result.stdout)
            f.write(f"\n{self.texts[self.lang]['stderr']}:\n")
            f.write(result.stderr)

        return filepath

    def _scan_util_start(self, title, filetypes=None, initialdir=None, is_file=True, mode="files"):
        self.breathing_circle.set_color(Palette.COLOR_BLUE)
        self.breathing_circle.set_symbol(3)

        if mode == "files":
            path = askopenfilename(title=title, filetypes=filetypes,
                                   initialdir=initialdir) if is_file else askdirectory(
                title=title, initialdir=initialdir)
            if path:
                path = PathUtil.handle_path(path)
                #
                # newWindow = tk.Toplevel(self.root)
                # newWindow.title(self.texts[self.lang]['scan'])
                # self.center_window(newWindow, 200, 150)
                #
                # label_loading = ttk.Label(
                #     newWindow, text=f"{self.texts[self.lang]['scan']} {path}", justify="left", wraplength=280 * scaler)
                # label_loading.pack(padx=10, pady=10)
                #
                # progressbar = ttk.Progressbar(newWindow, mode="indeterminate")
                # progressbar.pack(fill=tk.X, padx=10, pady=10)
                # progressbar.start(10)

                threading.Thread(target=self._scan_util_start_thread,
                                 args=(path,), daemon=True).start()

                # self.root.after(100, self.check_scan_status,
                #                 progressbar, newWindow, label_loading)
                self.root.after(100, self.check_scan_status)
            elif mode == "memory":
                threading.Thread(target=self._scan_util_start_thread,
                                 args=(path, mode,), daemon=True).start()

                self.root.after(100, self.check_scan_status)

    def scan_mode_one_file(self):
        self._scan_util_start(
            title=self.texts[self.lang]['select_file'],
            filetypes=[
                (self.texts[self.lang]['all_files'], "*.*"),
                (self.texts[self.lang]['text_files'], "*.txt"),
                (self.texts[self.lang]['image_files'], "*.png *.jpg *.jpeg"),
            ],
            initialdir=os.path.expanduser("~"),
            is_file=True
        )

    def scan_mode_memory(self):
        self._scan_util_start(
            title="",
            mode="memory"
        )
        self.scan_info.config(text="Scanning memory.")

    def scan_mode_directory(self):
        self._scan_util_start(
            title=self.texts[self.lang]['select_directory'],
            initialdir=os.path.expanduser("~"),
            is_file=False
        )

    def view_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        self.center_window(about_window)

        about_image_original = tk.PhotoImage(file=self.icon_path)
        about_image = about_image_original.subsample(3, 3)

        image_label = ttk.Label(about_window, image=about_image)
        image_label.image = about_image  # ¡Importante! Mantener la referencia a la imagen.
        image_label.pack(pady=10)

        label_version = ttk.Label(about_window, text=f"{self.texts[self.lang]['version']} {VERSION}")
        label_about = ttk.Label(
            about_window,
            text=self.texts[self.lang]['about'],
            wraplength=280 * scaler
        )
        label_version.pack(padx=10, pady=10)
        label_about.pack(pady=10, padx=10)

    def update_database(self):
        self.button_update_database.config(state="disabled")
        thread = threading.Thread(target=self._update_database)
        thread.start()

    def _update_database(self):
        self.scan_info.config(text="Checking virus database.")
        result = subprocess.run(["freshclam"],
                                capture_output=True, text=True)

        if "Failed to lock the log file" in result.stderr:
            self.label_version["text"] = self.texts[self.lang]['database_locked']
        elif result.returncode != 0:
            self.label_version["text"] = f"{self.texts[self.lang]['database_update_error']}\n{result.stderr}"
        else:
            self.label_version["text"] = self.texts[self.lang]['database_updated']

        if "Problem with internal logger" in result.stderr or result.returncode == 0:
            self.label_version["text"] = self.texts[self.lang]['database_up_to_date']
        self.button_update_database.config(state="normal")

        self.scan_info.config(text="Database up to date.")
        self.get_main_version()
        self.get_version()

    def get_version(self):
        def run_version_fetch():
            try:
                result = subprocess.run(
                    ["freshclam", "--version"], capture_output=True, text=True)

                if result.returncode == 0:
                    first_line = result.stdout.strip().split("\n")[0]
                    parts = first_line.split("/")
                    if len(parts) >= 3:
                        version_full = parts[0].replace("ClamAV", "").strip()
                        version_date_str = parts[2].strip()

                        date_version = datetime.strptime(
                            version_date_str, "%a %b %d %H:%M:%S %Y")
                        version_date_formatted = date_version.strftime("%Y-%m-%d")
                        current_date = datetime.now().strftime("%Y-%m-%d")

                        self.label_version["text"] = (f"{self.texts[self.lang]['version_label']} {version_full}\n"
                                                      f"{self.texts[self.lang]['database_updated_on']} {date_version}")

                        if current_date == version_date_formatted:
                            self.button_update_database.config(state="disabled")
                            self.button_update_database["text"] = self.texts[self.lang]['database_updated']
                        else:
                            self.button_update_database.config(state="normal")
                    else:
                        self.label_version["text"] = self.texts[self.lang]['unexpected_version_format']
                else:
                    self.label_version["text"] = self.texts[self.lang]['version_fetch_error']
            except Exception as e:
                self.label_version["text"] = f"{self.texts[self.lang]['generic_error']} {e}"
            finally:
                self.root.update_idletasks()

        threading.Thread(target=run_version_fetch, daemon=True).start()
        self.root.update_idletasks()

    def get_main_version(self):
        def run_version_fetch():
            try:
                result = subprocess.run(
                    ["freshclam", "--version"], capture_output=True, text=True)

                if result.returncode == 0:
                    first_line = result.stdout.strip().split("\n")[0]
                    parts = first_line.split("/")
                    if len(parts) >= 3:
                        version_full = parts[0].replace("ClamAV", "").strip()
                        version_date_str = parts[2].strip()

                        date_version = datetime.strptime(
                            version_date_str, "%a %b %d %H:%M:%S %Y")
                        date_version.strftime("%Y-%m-%d")
                        datetime.now().strftime("%Y-%m-%d")

                        self.main_version["text"] = (
                            # f"{self.texts[self.lang]['version_label']} {version_full}\n"
                            f"{self.texts[self.lang]['database_updated_on']} {date_version}")
                    else:
                        self.main_version["text"] = self.texts[self.lang]['unexpected_version_format']
                else:
                    self.main_version["text"] = self.texts[self.lang]['version_fetch_error']
            except Exception as e:
                self.main_version["text"] = f"{self.texts[self.lang]['generic_error']} {e}"
            finally:
                self.root.update_idletasks()

        threading.Thread(target=run_version_fetch, daemon=True).start()
        self.root.update_idletasks()


class MONITORINFO(Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD)
    ]


def fix_HiDPI(_root):
    global scale_factor
    global scaler
    if os.name == "nt":
        try:
            windll.shcore.SetProcessDpiAwareness(2)
            scale_factor = windll.shcore.GetScaleFactorForDevice(0)
            shcore = True
        except Exception:
            try:
                windll.user32.SetProcessDPIAware()
                shcore = False
            except Exception:
                scaler = 1
                return

        if shcore:
            scaler = 96 * scale_factor / 100 / 60
            print(scaler)
            _root.tk.call('tk', 'scaling', scaler)

            win_handle = wintypes.HWND(_root.winfo_id())
            monitor_handle = windll.user32.MonitorFromWindow(win_handle, 2)  # MONITOR_DEFAULTTONEAREST = 2

            x_dpi = wintypes.UINT()
            y_dpi = wintypes.UINT()
            windll.shcore.GetDpiForMonitor(monitor_handle, 0, pointer(x_dpi), pointer(y_dpi))  # MDT_EFFECTIVE_DPI = 0

            monitor_info = MONITORINFO()
            monitor_info.cbSize = sizeof(MONITORINFO)
            windll.user32.GetMonitorInfoW(monitor_handle, byref(monitor_info))

            monitor_width = monitor_info.rcMonitor.right - monitor_info.rcMonitor.left
            monitor_height = monitor_info.rcMonitor.bottom - monitor_info.rcMonitor.top

            target_width = 1920
            target_height = 1080

            scale_w = target_width / monitor_width
            scale_h = target_height / monitor_height
            scale = max(scale_w, scale_h)

            actual_width = int(1024 * scale)
            actual_height = int(768 * scale)

            _root.geometry(f"{actual_width}x{actual_height}")

    # Adjust font sizes for HiDPI displays
    fix_scaling(_root)


MODE = ""

if __name__ == "__main__":
    # fix ttkbootstrap conflicts with datetime parser
    # don't delete this line
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    windll.shcore.SetProcessDpiAwareness(1)

    # DEV_MODE = True
    DEV_MODE = False
    if not DEV_MODE:
        request_uac_or_skip()
    try:
        CLAM_PATH = find_clamav()
    except:
        pass

    # DEV_MODE_LIGHT = True
    DEV_MODE_LIGHT = False

    if darkdetect.isLight() or DEV_MODE_LIGHT:
        MODE = "light"
        root = ttk.Window(themename="minty")
    else:
        MODE = "dark"
        root = ttk.Window(themename="darkly")

    fix_HiDPI(root)

    app = ClamAVScanner(_root=root)

    if MODE == "dark":
        dark_title_bar(root)

    root.lift()
    root.attributes("-topmost", True)
    root.mainloop()
