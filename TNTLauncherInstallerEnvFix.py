import os
import subprocess
import urllib.request
import requests
import zipfile
import threading
from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- CONFIG ----------------
PYTHON_VERSION = "3.12.1"
PYTHON_INSTALLER_URL = (
    "https://www.python.org/ftp/python/3.12.1/"
    "python-3.12.1-amd64.exe"
)

GITHUB_ZIP_URL = (
    "https://github.com/cringsimulator-a11y/TNTLauncher/"
    "archive/refs/heads/main.zip"
)

REQUIRED_LIBS = [
    "requests",
    "Pillow",
    "minecraft-launcher-lib"
]

INSTALL_DRIVE = "D:" if os.path.exists("D:") else "C:"
INSTALL_FOLDER = os.path.join(INSTALL_DRIVE, "TNTLauncher")
PYTHON_PATH = r"C:\Program Files\Python312\python.exe"

# ---------------- UI ----------------
root = tk.Tk()
root.title("TNT Launcher Installer")
root.geometry("420x170")
root.resizable(False, False)
root.configure(bg="#121212")
root.eval("tk::PlaceWindow . center")

label = tk.Label(
    root,
    text="Installing TNT Launcher...",
    fg="white",
    bg="#121212",
    font=("Segoe UI", 12, "bold")
)
label.pack(pady=(25, 8))

progress = ttk.Progressbar(root, length=340, mode="determinate")
progress.pack(pady=10)

status = tk.Label(
    root,
    text="Starting...",
    fg="#aaa",
    bg="#121212",
    font=("Segoe UI", 9)
)
status.pack()

# ---------------- HELPERS ----------------
def set_status(text, value):
    status.config(text=text)
    progress["value"] = value
    root.update_idletasks()

def python_installed():
    return os.path.exists(PYTHON_PATH)

def install_python():
    set_status("Downloading Python...", 5)
    installer = os.path.join(os.getcwd(), "python_installer.exe")
    urllib.request.urlretrieve(PYTHON_INSTALLER_URL, installer)

    set_status("Installing Python...", 15)
    subprocess.run(
        [
            installer,
            "/quiet",
            "InstallAllUsers=1",
            "PrependPath=1",
            "Include_pip=1"
        ],
        check=True
    )

    os.remove(installer)

def install_libs():
    step = 25
    for lib in REQUIRED_LIBS:
        set_status(f"Installing {lib}...", step)
        subprocess.run(
            [PYTHON_PATH, "-m", "pip", "install", "--upgrade", lib],
            check=True
        )
        step += 10

def download_launcher():
    os.makedirs(INSTALL_FOLDER, exist_ok=True)

    set_status("Downloading launcher files...", 65)
    r = requests.get(GITHUB_ZIP_URL, stream=True, timeout=60)
    r.raise_for_status()

    buffer = BytesIO()
    for chunk in r.iter_content(8192):
        if chunk:
            buffer.write(chunk)

    set_status("Extracting files...", 85)
    buffer.seek(0)

    with zipfile.ZipFile(buffer) as zf:
        base = zf.namelist()[0]
        for member in zf.namelist():
            target = os.path.join(
                INSTALL_FOLDER,
                os.path.relpath(member, base)
            )
            if member.endswith("/"):
                os.makedirs(target, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "wb") as f:
                    f.write(zf.read(member))

# ---------------- MAIN THREAD ----------------
def installer_thread():
    try:
        if not python_installed():
            install_python()

        install_libs()
        download_launcher()

        set_status("Installation complete!", 100)
        messagebox.showinfo(
            "Done",
            "TNT Launcher installed successfully!"
        )
    except Exception as e:
        messagebox.showerror("Installer Error", str(e))

threading.Thread(target=installer_thread, daemon=True).start()
root.mainloop()
