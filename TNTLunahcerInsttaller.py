import os
import sys
import subprocess
import urllib.request
import requests
import zipfile
import threading
from io import BytesIO
import tkinter as tk
from tkinter import ttk

PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe"
GITHUB_ZIP_URL = "https://github.com/cringsimulator-a11y/TNTLauncher/archive/refs/heads/main.zip"

REQUIRED_LIBS = [
    "requests",
    "Pillow",
    "minecraft-launcher-lib"
]

base_drive = "D:" if os.path.exists("D:") else "C:"
INSTALL_FOLDER = os.path.join(base_drive, "TNTLauncher")

# ---------------- UI ----------------
root = tk.Tk()
root.title("TNT Launcher Installer")
root.geometry("420x160")
root.resizable(False, False)
root.configure(bg="#121212")

root.eval('tk::PlaceWindow . center')

label = tk.Label(
    root,
    text="Installing TNT Launcher...",
    fg="white",
    bg="#121212",
    font=("Segoe UI", 12, "bold")
)
label.pack(pady=(25, 10))

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

# ---------------- LOGIC ----------------
def python_exists():
    try:
        subprocess.check_output(["py", "-3", "--version"])
        return "py"
    except:
        try:
            subprocess.check_output(["python", "--version"])
            return "python"
        except:
            return None

def install_python():
    status.config(text="Downloading Python...")
    progress["value"] = 5
    root.update()

    installer_path = os.path.join(os.getcwd(), "python_installer.exe")
    urllib.request.urlretrieve(PYTHON_INSTALLER_URL, installer_path)

    status.config(text="Installing Python...")
    progress["value"] = 15
    root.update()

    subprocess.run([
        installer_path,
        "/quiet",
        "InstallAllUsers=1",
        "PrependPath=1",
        "Include_pip=1"
    ], check=True)

    os.remove(installer_path)

def install_libs(py_cmd):
    step = 20
    for lib in REQUIRED_LIBS:
        status.config(text=f"Installing {lib}...")
        progress["value"] = step
        root.update()

        subprocess.run(
            [py_cmd, "-m", "pip", "install", "--upgrade", lib],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        step += 10

def download_launcher():
    os.makedirs(INSTALL_FOLDER, exist_ok=True)

    status.config(text="Downloading launcher files...")
    progress["value"] = 60
    root.update()

    r = requests.get(GITHUB_ZIP_URL, stream=True, timeout=60)
    r.raise_for_status()

    total = int(r.headers.get("Content-Length", 1))
    downloaded = 0
    buffer = BytesIO()

    for chunk in r.iter_content(8192):
        if chunk:
            buffer.write(chunk)
            downloaded += len(chunk)
            progress["value"] = 60 + (downloaded / total) * 20
            root.update()

    status.config(text="Extracting files...")
    progress["value"] = 85
    root.update()

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

def installer_thread():
    try:
        py_cmd = python_exists()
        if not py_cmd:
            install_python()
            py_cmd = python_exists()

        install_libs(py_cmd)
        download_launcher()

        progress["value"] = 100
        status.config(text="Installation complete!")
    except Exception as e:
        status.config(text=f"Error: {e}")

threading.Thread(target=installer_thread, daemon=True).start()
root.mainloop()
