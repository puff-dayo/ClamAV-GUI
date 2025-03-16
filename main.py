import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, askdirectory
import subprocess
import os
import threading
import queue
from datetime import datetime
from tkinter import PhotoImage
from pathlib import Path
from ctypes import windll


VERSION = "0.0.10"

class ClamAVScanner:
    def __init__(self, root):
        self.root = root
        self.lang = "en"
        self.texts = self.load_texts()
        self.result_queue = queue.Queue()
        self.history_dir = Path.home() / "ClamAV_History"
        self.history_dir.mkdir(exist_ok=True)

        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.icon_path = os.path.join(self.script_dir, "shield.png")

        try:
            self.icon_image = PhotoImage(file=self.icon_path)
            self.root.iconphoto(True, self.icon_image)
        except Exception as e:
            print(f"Error al cargar el ícono: {e}")

        self.setup_ui()

    def load_texts(self):
        return {
            "es": {
                "app_title": "ClamAV Tkinter - Escáner de archivos y directorios",
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
                "scan":"Escaneando",
                "scan_complete": "Escaneo Completado",
                "stdout": "Salida estándar",
                "stderr": "Salida de error",
                "result_saved": "Resultado guardado en",
                "recursive_search": "Buscar amenazas de manera recursiva",
                "delete_threats": "Eliminar amenazas encontradas",

                "version":"Versión",
                "about":"ClamAV GUI es una interfaz gráfica de usuario (GUI) diseñada para facilitar el uso "
                "de ClamAV, un software antivirus de código abierto. Esta aplicación está inspirada en proyectos "
                "como ClamWin y ClamTk, y ofrece una experiencia más accesible y visual para los usuarios que desean "
                "realizar escaneos antivirus en sus sistemas de forma rápida y sencilla."
            },
            "en": {
                "app_title": "ClamAV Tkinter - File and Directory Scanner",
                "menu_bar1": "Language",
                "menu_bar2": "Help",
                "language_menu1": "English",
                "language_menu2": "Español",
                "help_menu1": "About",
                "tab1": "Analysis",
                "tab2": "History",
                "tab3": "Updates",
                "tab4": "Configuration",
                "button_label1": "Scan a file",
                "button_label2": "Scan a directory",
                "button_label3": "View scan history",
                "button_label4": "Update database",
                "checkbox_label1": "Search for threats recursively",
                "checkbox_label2": "Remove found threats",
                "version_label": "ClamAV Version: ",
                "database_label": "Database Version: ",
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
                "database_updated_on": "Database updated on:",
                "current_date": "Current date",
                "version_date": "Version date",
                "unexpected_version_format": "Unexpected version format.",
                "version_fetch_error": "Failed to fetch ClamAV version.",
                "generic_error": "Error:",
                "loading_message": "Loading, please wait...",
                "error_message": "An error occurred. Please try again.",
                "about_message": "ClamAV Tkinter is a graphical interface for scanning files and directories using the ClamAV engine.",
                "scan":"Scanning",
                "scan_complete": "Scan Complete",
                "stdout": "Standard output",
                "stderr": "Error output",
                "result_saved": "Result saved at",
                "recursive_search": "Search for threats recursively",
                "delete_threats": "Delete found threats",

                "version":"Version",
                "about":"ClamAV GUI is a graphical user interface designed to simplify the use of ClamAV, an open-source antivirus software. This application is inspired by projects such as ClamWin and ClamTk, and provides a more accessible and visual experience for users who wish to perform antivirus scans on their systems quickly and easily."
            }
        }

    def setup_ui(self):
        self.root.title(self.texts[self.lang]['app_title'])
        self.root.resizable(False, False)
        self.center_window()
        self.create_menu()
        self.create_tabs()
        self.create_buttons()
        self.create_checkboxes()
        self.get_version()

    def center_window(self, window=None, marginx=100, marginy=100):
        if window is None:
            window = self.root

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        window.geometry(f"+{x-marginx}+{y-marginy}")

    def create_menu(self):
        if hasattr(self, "menu_bar"):
            self.menu_bar.destroy()

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.language_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.language_menu.add_command(
            label=self.texts[self.lang]["language_menu1"],
            command=lambda: self.change_lang("en")
        )
        self.language_menu.add_command(
            label=self.texts[self.lang]["language_menu2"],
            command=lambda: self.change_lang("es")
        )

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(
            label=self.texts[self.lang]["help_menu1"],
            command=lambda: self.view_about()
        )

        self.menu_bar.add_cascade(
            label=self.texts[self.lang]["menu_bar1"],
            menu=self.language_menu
        )
        self.menu_bar.add_cascade(
            label=self.texts[self.lang]["menu_bar2"],
            menu=self.help_menu
        )

    def create_tabs(self):
        self.tabs_notebook = ttk.Notebook(self.root)
        self.tabs_notebook.pack(fill="both", expand=True, pady=10, padx=5)

        self.scan_frame = ttk.Frame(self.tabs_notebook)
        self.history_frame = ttk.Frame(self.tabs_notebook)
        self.update_frame = ttk.Frame(self.tabs_notebook)
        self.config_frame = ttk.Frame(self.tabs_notebook)

        self.tabs_notebook.add(
            self.scan_frame, text=self.texts[self.lang]["tab1"])
        self.tabs_notebook.add(
            self.history_frame, text=self.texts[self.lang]["tab2"])
        self.tabs_notebook.add(
            self.update_frame, text=self.texts[self.lang]["tab3"])
        self.tabs_notebook.add(
            self.config_frame, text=self.texts[self.lang]["tab4"])

    def create_buttons(self):
        self.button_scan_a_file = ttk.Button(
            self.scan_frame, text=self.texts[self.lang]["button_label1"], command=self.scan_a_file)
        self.button_scan_a_file.pack(fill="x", pady=10, padx=10)

        self.button_scan_a_directory = ttk.Button(
            self.scan_frame, text=self.texts[self.lang]["button_label2"], command=self.scan_a_directory)
        self.button_scan_a_directory.pack(fill="x", pady=5, padx=10)

        self.button_view_history = ttk.Button(
            self.history_frame, text=self.texts[self.lang]["button_label3"], command=self.view_history)
        self.button_view_history.pack(fill="x", pady=10, padx=10)

        self.button_update_database = ttk.Button(
            self.update_frame, text=self.texts[self.lang]["button_label4"], command=self.update_database)
        self.button_update_database.pack(fill="x", padx=10, pady=10)

        self.label_version = ttk.Label(
            self.update_frame, text="", wraplength=280)
        self.label_version.pack(padx=10, pady=10)

    def create_checkboxes(self):
        self.checkbox_var_recursive = tk.IntVar(value=1)
        self.checkbox_var_kill = tk.IntVar(value=0)

        self.checkbox_recursive = tk.Checkbutton(
            self.config_frame, text=self.texts[self.lang]['recursive_search'], variable=self.checkbox_var_recursive)
        self.checkbox_kill = tk.Checkbutton(
            self.config_frame, text=self.texts[self.lang]['delete_threats'], variable=self.checkbox_var_kill)

        self.checkbox_recursive.pack(pady=5, padx=5, anchor="w")
        self.checkbox_kill.pack(pady=5, padx=5, anchor="w")

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

        self.create_menu()

    def run_scan(self, path):
        args = ['clamscan']

        if self.checkbox_var_recursive.get() == 1:
            args.append('-r')

        if self.checkbox_var_kill.get() == 1:
            args.append('--remove')

        args.append(path)

        try:
            result = subprocess.run(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.result_queue.put(result)
        except Exception as e:
            self.result_queue.put(e)

    def check_scan_status(self, progressbar, newWindow, label_loading):
        try:
            result = self.result_queue.get_nowait()
        except queue.Empty:
            self.root.after(100, self.check_scan_status, progressbar, newWindow, label_loading)
            return

        if progressbar.winfo_exists():
            progressbar.stop()
            progressbar.destroy()

        if label_loading.winfo_exists():
            label_loading.destroy()

        newWindow.title(self.texts[self.lang]['scan_complete'])
        self.center_window(newWindow, 500, 250)

        text_square = tk.Text(newWindow, wrap=tk.WORD, font=("Courier New", 12))
        text_square.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if isinstance(result, Exception):
            text_square.insert(tk.END, f"{self.texts[self.lang]['error_message']}:\n{str(result)}")
        else:
            text_square.insert(tk.END, f"{self.texts[self.lang]['stdout']}:\n")
            text_square.insert(tk.END, result.stdout)
            text_square.insert(tk.END, f"\n{self.texts[self.lang]['stderr']}:\n")
            text_square.insert(tk.END, result.stderr)

            filepath = self.save_scan_result(result)
            messagebox.showinfo(self.texts[self.lang]['scan_complete'],
                                f"{self.texts[self.lang]['result_saved']} {filepath}")

        try:
            text_square.config(state="disabled")
        except tk.TclError as e:
            print(f"Error configuring text widget: {e}")
        
    def save_scan_result(self, result):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.txt"
        filepath = self.history_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"{self.texts[self.lang]['stdout']}:\n")
            f.write(result.stdout)
            f.write(f"\n{self.texts[self.lang]['stderr']}:\n")
            f.write(result.stderr)

        return filepath

    def start_scan(self, title, filetypes=None, initialdir=None, is_file=True):
        path = askopenfilename(title=title, filetypes=filetypes, initialdir=initialdir) if is_file else askdirectory(
            title=title, initialdir=initialdir)

        if path:
            newWindow = tk.Toplevel(self.root)
            newWindow.title(self.texts[self.lang]['scan'])
            self.center_window(newWindow, 200, 150)

            label_loading = ttk.Label(
                newWindow, text=f"{self.texts[self.lang]['scan']} {path}", justify="left", wraplength=280)
            label_loading.pack(padx=10, pady=10)

            progressbar = ttk.Progressbar(newWindow, mode="indeterminate")
            progressbar.pack(fill=tk.X, padx=10, pady=10)
            progressbar.start(10)

            threading.Thread(target=self.run_scan,
                             args=(path,), daemon=True).start()
            self.root.after(100, self.check_scan_status,
                            progressbar, newWindow,label_loading)

    def scan_a_file(self):
        self.start_scan(
            title=self.texts[self.lang]['select_file'],
            filetypes=[
                (self.texts[self.lang]['all_files'], "*.*"),
                (self.texts[self.lang]['text_files'], "*.txt"),
                (self.texts[self.lang]['image_files'], "*.png *.jpg *.jpeg"),
            ],
            initialdir=os.path.expanduser("~"),
            is_file=True
        )

    def scan_a_directory(self):
        self.start_scan(
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

        image_label = tk.Label(about_window, image=about_image)
        image_label.image = about_image  # ¡Importante! Mantener la referencia a la imagen.
        image_label.pack(pady=10)

        label_version = tk.Label(about_window, text=f"{self.texts[self.lang]['version']} {VERSION}")
        label_about = tk.Label(
            about_window,
            text=self.texts[self.lang]['about'],
            wraplength=280
        )
        label_version.pack(padx=10, pady=10)
        label_about.pack(pady=10, padx=10)

    def view_history(self):
        history_files = os.listdir(self.history_dir)

        if not history_files:
            messagebox.showinfo(
                "Historial", self.texts[self.lang]['no_history_files'])
            return

        history_window = tk.Toplevel(self.root)
        history_window.title(self.texts[self.lang]['history_title'])
        self.center_window(history_window, 200, 100)

        listbox = tk.Listbox(history_window, font=("Courier New", 12))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for file in sorted(history_files, reverse=True):
            listbox.insert(tk.END, file)

        def open_selected_file(e=None):
            selected_index = listbox.curselection()
            if not selected_index:
                return

            selected_file = listbox.get(selected_index)
            filepath = self.history_dir / selected_file

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            result_window = tk.Toplevel(self.root)
            result_window.title(
                f"{self.texts[self.lang]['history_title']}: {selected_file}")
            self.center_window(result_window, 100, 200)

            text_square = tk.Text(
                result_window, wrap=tk.WORD, font=("Courier New", 12))
            text_square.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_square.insert(tk.END, content)
            text_square.config(state="disabled")

        history_window.bind('<Double-Button-1>', open_selected_file)

        open_button = ttk.Button(
            history_window, text=self.texts[self.lang]['open_result'], command=open_selected_file)
        open_button.pack(pady=10)

    def update_database(self):
        result = subprocess.run(["pkexec", "freshclam"],
                                capture_output=True, text=True)

        if "Failed to lock the log file" in result.stderr:
            self.label_version["text"] = self.texts[self.lang]['database_locked']
        elif result.returncode != 0:
            self.label_version["text"] = f"{self.texts[self.lang]['database_update_error']}\n{result.stderr}"
        else:
            self.label_version["text"] = self.texts[self.lang]['database_updated']

        if "Problem with internal logger" in result.stderr or result.returncode == 0:
            self.label_version["text"] = self.texts[self.lang]['database_up_to_date']

    def get_version(self):
        try:
            result = subprocess.run(
                ["clamscan", "--version"], capture_output=True, text=True)

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


if __name__ == "__main__":
    windll.shcore.SetProcessDpiAwareness(1)

    root = tk.Tk()
    app = ClamAVScanner(root)
    root.mainloop()
