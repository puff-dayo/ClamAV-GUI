import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, askdirectory
import subprocess
import os
import threading
import queue
from datetime import datetime
from tkinter import PhotoImage

root = tk.Tk()
root.title("ClamAV Tkinter - Escáner de archivos y directorios")
root.update_idletasks() 

root.resizable(False, False)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = root.winfo_width()
window_height = root.winfo_height()

x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

root.geometry(f"+{x}+{y}")

result_queue = queue.Queue()


script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)   

script_dir = os.path.dirname(os.path.realpath(__file__))
icon_path = os.path.join(script_dir, "shield.png")

try:
    icon_image = PhotoImage(file=icon_path)
    root.iconphoto(True, icon_image)
except Exception as e:
    print(f"Error setting icon: {e}")

#Crear el directorio para almacenar los logs
history_dir = os.path.join(os.path.expanduser("~"), "ClamAV_History")
os.makedirs(history_dir, exist_ok=True)

def save_scan_result(result):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}.txt"
    filepath = os.path.join(history_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("Salida estándar:\n")
        f.write(result.stdout)
        f.write("\n\nSalida de error:\n")
        f.write(result.stderr)

    return filepath

def run_scan(path, result_queue):
    global checkbox_var_recursive
    if checkbox_var_recursive == 1:
        args = ['clamscan', '-r', path]
    else:
        args = ['clamscan', path]
    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        result_queue.put(result)
    except Exception as e:
        result_queue.put(e)

def check_scan_status(progressbar, newWindow, result_queue):
    try:
        result = result_queue.get_nowait()
    except queue.Empty:
        root.after(100, check_scan_status, progressbar, newWindow, result_queue)
        return

    progressbar.stop()
    progressbar.destroy()

    newWindow.geometry(f"+{x}+{y}")

    text_square = tk.Text(newWindow, wrap=tk.WORD, font=("Courier New", 12))
    text_square.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    if isinstance(result, Exception):
        text_square.insert(tk.END, f"Error durante el escaneo:\n{str(result)}")
    else:
        text_square.insert(tk.END, "Salida estándar:\n")
        text_square.insert(tk.END, result.stdout)
        text_square.insert(tk.END, "\nSalida de error:\n")
        text_square.insert(tk.END, result.stderr)

        filepath = save_scan_result(result)
        messagebox.showinfo("Escaneo completado", f"Resultado guardado en: {filepath}")

    text_square.config(state="disabled")
    tk.Label(newWindow, text="Escaneo completado", fg="green").pack()

def start_scan(title, filetypes=None, initialdir=None, is_file=True):
    path = askopenfilename(title=title, filetypes=filetypes, initialdir=initialdir) if is_file else askdirectory(title=title, initialdir=initialdir)

    if path:
        newWindow = tk.Toplevel(root)
        newWindow.title("Resultado del escaneo")
        newWindow.geometry(f"+{x}+{y}")

        label = ttk.Label(newWindow, text=f"Escaneando: {path}", justify="left", wraplength=280)
        label.pack(padx=10, pady=10)
        progressbar = ttk.Progressbar(newWindow, mode="indeterminate")
        progressbar.pack(fill=tk.X, padx=10, pady=10)
        progressbar.start(10)

        threading.Thread(target=run_scan, args=(path, result_queue), daemon=True).start()
        root.after(100, check_scan_status, progressbar, newWindow, result_queue)

def scan_a_file():
    start_scan(
        title="Selecciona un archivo",
        filetypes=[
            ("Todos los archivos", "*.*"),
            ("Archivos de texto", "*.txt"),
            ("Archivos de imagen", "*.png *.jpg *.jpeg"),
        ],
        initialdir=os.path.expanduser("~"),
        is_file=True
    )

def scan_a_directory():
    start_scan(
        title="Selecciona un directorio",
        initialdir=os.path.expanduser("~"),
        is_file=False
    )

def view_history():
    history_files = os.listdir(history_dir)

    if not history_files:
        messagebox.showinfo("Historial", "No hay archivos de historial disponibles.")
        return

    history_window = tk.Toplevel(root)
    history_window.title("Historial de escaneos")
    history_window.geometry(f"+{x}+{y}")

    listbox = tk.Listbox(history_window, font=("Courier New", 12))
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for file in sorted(history_files, reverse=False):
        listbox.insert(tk.END, file)

    def open_selected_file(e):
        selected_index = listbox.curselection()
        if not selected_index:
            return

        selected_file = listbox.get(selected_index)
        filepath = os.path.join(history_dir, selected_file)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        result_window = tk.Toplevel(root)
        result_window.title(f"Historial: {selected_file}")
        result_window.geometry(f"+{x}+{y}")

        text_square = tk.Text(result_window, wrap=tk.WORD, font=("Courier New", 12))
        text_square.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_square.insert(tk.END, content)
        text_square.config(state="disabled")

    history_window.bind('<Double-Button-1>', open_selected_file)

    open_button = ttk.Button(history_window, text="Abrir resultado", command=open_selected_file)
    open_button.pack(pady=10)

def update_database():
    result = subprocess.run(["sudo", "freshclam"], capture_output=True, text=True)

    if "Failed to lock the log file" in result.stderr:
        label_version["text"] = ("El proceso de actualización de la base de datos se gestiona automáticamente y "
                                 "se ejecuta en segundo plano. No es necesario invocarlo manualmente.")
    
    elif result.returncode != 0:
        label_version["text"] = f"Error al actualizar la base de datos:\n{result.stderr}"
        print(result.stderr)
    
    else:
        label_version["text"] = "La base de datos se actualizó correctamente."

    if "Problem with internal logger" in result.stderr or result.returncode == 0:
        label_version["text"] = ("La base de datos ya está actualizada y se gestiona automáticamente en segundo plano. "
                                 "No es necesario actualizarla manualmente.")

def get_version():
    try:
        result = subprocess.run(["clamscan", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
      
            # ClamAV 0.103.12/27575/Wed Mar 12 05:37:42 2025
            first_line = result.stdout.strip().split("\n")[0]
         
            # Esto asume que el formato es: "ClamAV <versión>/<algo>/<fecha string>"
            parts = first_line.split("/")
            if len(parts) >= 3:
                version_full = parts[0].replace("ClamAV", "").strip()
                version_date_str = parts[2].strip()
            
                fecha_version = datetime.strptime(version_date_str, "%a %b %d %H:%M:%S %Y")
                label_version["text"] = f"Versión de ClamAV: {version_full}\nBase de datos actualizada el: {fecha_version}"
                version_date_formatted = fecha_version.strftime("%Y-%m-%d")
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                print("Fecha actual:", current_date)
                print("Fecha de version:", version_date_formatted)
                
                if current_date == version_date_formatted:
                    button_update_database.config(state="disabled")
                    button_update_database["text"] = "Base de datos actualizada"
                else:
                    button_update_database.config(state="normal")
            else:
                label_version["text"] = "Formato de versión inesperado."
        else:
            label_version["text"] = "No se pudo obtener la versión de ClamAV."
    except Exception as e:
        label_version["text"] = f"Error: {e}"

tabs_notebook = ttk.Notebook(root)
tabs_notebook.pack(fill="both", expand=True, pady=5, padx=5)

scan_frame = ttk.Frame(tabs_notebook)
history_frame = ttk.Frame(tabs_notebook)
update_frame = ttk.Frame(tabs_notebook)
config_frame = ttk.Frame(tabs_notebook)

tabs_notebook.add(scan_frame, text="Escanear")
tabs_notebook.add(history_frame, text="Histórico")
tabs_notebook.add(update_frame, text="Actualizaciones")
tabs_notebook.add(config_frame, text="Config.")

button_scan_a_file = ttk.Button(scan_frame, text="Escanear un archivo", command=scan_a_file)
button_scan_a_file.pack(fill="x", pady=10, padx=10)

button_scan_a_directory = ttk.Button(scan_frame, text="Escanear un directorio", command=scan_a_directory)
button_scan_a_directory.pack(fill="x", pady=5, padx=10)

button_view_history = ttk.Button(history_frame, text="Ver historial de escaneos", command=view_history)
button_view_history.pack(fill="x", pady=10, padx=10)

button_update_database = ttk.Button(update_frame, text="Actualizar base de datos", command=update_database)
button_update_database.pack(fill="x", padx=10, pady=10)

label_version = ttk.Label(update_frame, text="", wraplength=270)
label_version.pack(padx=10, pady=10)

get_version()

checkbox_var_recursive = tk.IntVar(value=1)

checkbox_recursive = tk.Checkbutton(config_frame, text="Buscar amenazas de manera recursiva", variable=checkbox_var_recursive)
checkbox_recursive.pack(pady=20)

root.mainloop()
