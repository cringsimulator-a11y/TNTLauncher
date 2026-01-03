import threading
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import minecraft_launcher_lib

MC_DIR = os.path.join(os.getenv("APPDATA"), ".minecraft")
DATA_FILE = "launcher_data.json"
DEFAULT_VERSION = "1.21.1"


def load_launcher_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"download_version": DEFAULT_VERSION}, f, indent=4)
        return DEFAULT_VERSION

    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    if "download_version" not in data:
        data["download_version"] = DEFAULT_VERSION
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    return data["download_version"]


DOWNLOAD_VERSION = load_launcher_data()


root = tk.Tk()
root.title("Minecraft Version Installer")
root.geometry("500x220")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text=f"Installing Minecraft {DOWNLOAD_VERSION}",
    font=("Segoe UI", 12, "bold")
)
title_label.pack(pady=10)

status_label = tk.Label(root, text="Waiting...", font=("Segoe UI", 10))
status_label.pack()

progress = ttk.Progressbar(root, length=440, mode="determinate")
progress.pack(pady=10)

percent_label = tk.Label(root, text="0%")
percent_label.pack()


def install_version():
    def set_status(text):
        root.after(0, lambda: status_label.config(text=text))

    def set_progress(value):
        root.after(0, lambda: progress.config(value=value))
        if progress["maximum"] > 0:
            percent = (value / progress["maximum"]) * 100
            root.after(0, lambda: percent_label.config(text=f"{int(percent)}%"))

    def set_max(value):
        root.after(0, lambda: progress.config(maximum=value))

    callbacks = {
        "setStatus": set_status,
        "setProgress": set_progress,
        "setMax": set_max
    }

    try:
        set_status("Downloading files...")
        minecraft_launcher_lib.install.install_minecraft_version(
            DOWNLOAD_VERSION,
            MC_DIR,
            callback=callbacks
        )
        set_progress(progress["maximum"])
        set_status("Installation complete")
        messagebox.showinfo(
            "Done",
            f"Minecraft {DOWNLOAD_VERSION} installed successfully"
        )
    except Exception as e:
        set_status("Error")
        messagebox.showerror("Error", str(e))


def start_install():
    progress["value"] = 0
    percent_label.config(text="0%")
    threading.Thread(target=install_version, daemon=True).start()


install_btn = tk.Button(
    root,
    text="Install Version",
    font=("Segoe UI", 11),
    width=22,
    command=start_install
)
install_btn.pack(pady=15)

root.mainloop()
