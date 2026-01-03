import os
import sys
import json
import shutil
import zipfile
import threading
import urllib.request
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from io import BytesIO

# ---------------- CONFIG ----------------
REPO_ZIP = "https://github.com/cringsimulator-a11y/TNTLauncher/archive/refs/heads/main.zip"
PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe"
REQUIRED_LIBS = ["requests", "Pillow", "minecraft-launcher-lib"]

def get_drive():
    return "D:\\" if os.path.exists("D:\\") else "C:\\"

BASE_DIR = os.path.join(get_drive(), "TNTLauncher")
MC_DIR = os.path.join(os.getenv("APPDATA"), ".minecraft")
LAUNCHER_DATA = os.path.join(BASE_DIR, "launcher_data.json")
PROFILES = os.path.join(MC_DIR, "launcher_profiles.json")

# ---------------- UTILITIES ----------------
def ensure_dirs():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(MC_DIR, exist_ok=True)

def create_launcher_profiles():
    if not os.path.exists(PROFILES):
        data = {"profiles": {}, "settings": {}, "version": 3}
        with open(PROFILES, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def safe_launcher_data():
    if os.path.exists(LAUNCHER_DATA):
        try:
            with open(LAUNCHER_DATA, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}

    if data.get("hasFabric") is True:
        fabric_path = os.path.join(MC_DIR, "libraries", "net", "fabricmc")
        if not os.path.exists(fabric_path):
            data["hasFabric"] = False

    with open(LAUNCHER_DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ---------------- PYTHON CHECK/INSTALL ----------------
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

def install_python(progress, status):
    status.config(text="Downloading Python installer...")
    progress["value"] = 5
    root.update()

    installer_path = os.path.join(BASE_DIR, "python_installer.exe")
    urllib.request.urlretrieve(PYTHON_INSTALLER_URL, installer_path)

    status.config(text="Installing Files...")
    progress["value"] = 15
    root.update()

    subprocess.run([installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_pip=1"], check=True)
    os.remove(installer_path)

def install_libs(py_cmd, progress, status):
    step = 20
    for lib in REQUIRED_LIBS:
        status.config(text=f"Installing {lib}...")
        progress["value"] = step
        root.update()
        subprocess.run([py_cmd, "-m", "pip", "install", "--upgrade", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        step += 10

# ---------------- DOWNLOAD TNTLAUNCHER ----------------
def download_repo(progress, status):
    status.config(text="Downloading launcher files...")
    progress["value"] = 60
    root.update()

    zip_path = os.path.join(BASE_DIR, "repo.zip")
    def report(block, size, total):
        percent = int(block * size * 100 / total)
        progress["value"] = min(60 + percent // 2, 80)
        root.update()
    urllib.request.urlretrieve(REPO_ZIP, zip_path, report)

    status.config(text="Extracting launcher files...")
    progress["value"] = 85
    root.update()

    with zipfile.ZipFile(zip_path, "r") as z:
        base = z.namelist()[0]
        for member in z.namelist():
            target = os.path.join(BASE_DIR, os.path.relpath(member, base))
            if member.endswith("/"):
                os.makedirs(target, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with z.open(member) as src, open(target, "wb") as dst:
                    dst.write(src.read())
    os.remove(zip_path)

# ---------------- INSTALLER THREAD ----------------
def start_install(root, progress, status):
    try:
        ensure_dirs()
        create_launcher_profiles()
        safe_launcher_data()

        py_cmd = python_exists()
        if not py_cmd:
            install_python(progress, status)
            py_cmd = python_exists()
        install_libs(py_cmd, progress, status)

        download_repo(progress, status)

        progress["value"] = 100
        status.config(text="Download complete! Preparing Java setup...")
        root.update()
        root.after(1000, lambda: show_java_window(root))
    except Exception as e:
        status.config(text=f"Error: {e}")

# ---------------- JAVA SETUP ----------------
def show_java_window(root):
    root.destroy()
    win = tk.Tk()
    win.title("Java Setup")
    win.geometry("420x220")

    tk.Label(win, text="Please Download Java First", font=("Arial", 14)).pack(pady=15)

    def next_step():
        for widget in win.winfo_children():
            widget.destroy()

        tk.Label(win, text="Please paste the Java path here:").pack(pady=5)
        entry = tk.Entry(win, width=50)
        entry.pack(pady=5)

        def save():
            path = entry.get().strip()
            if not path:
                messagebox.showerror("Error", "Path cannot be empty")
                return
            if os.path.exists(LAUNCHER_DATA):
                with open(LAUNCHER_DATA, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {}
            data["javaPath"] = path
            with open(LAUNCHER_DATA, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Done", "Java path saved successfully")
            win.destroy()

        tk.Button(win, text="OK", command=save).pack(pady=10)

    tk.Button(win, text="I have Installed Java", command=next_step).pack(pady=10)
    win.mainloop()

# ---------------- MAIN ----------------
def main():
    global root
    root = tk.Tk()
    root.title("TNTLauncher Installer")
    root.geometry("420x160")
    root.resizable(False, False)

    tk.Label(root, text="TNTLAUNCHER IS DOWNLOADING", font=("Arial", 12)).pack(pady=10)
    progress = ttk.Progressbar(root, length=350, mode="determinate")
    progress.pack(pady=10)
    status = tk.Label(root, text="Starting...", font=("Arial", 10))
    status.pack()

    threading.Thread(target=start_install, args=(root, progress, status), daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
