import os
import shutil
import requests
import zipfile
from io import BytesIO
import tkinter as tk
from tkinter import ttk
import threading
import sys

def install_launcher(progress_var, status_label, root):
    # Step 0: Rename self to TEMPFILE.PY
    try:
        script_path = os.path.abspath(__file__)
        temp_path = os.path.join(os.path.dirname(script_path), "TEMPFILE.PY")
        if script_path != temp_path:
            os.rename(script_path, temp_path)
        script_path = temp_path
    except Exception as e:
        status_label.config(text=f"Failed to rename installer: {e}")
        return

    parent_dir = os.path.dirname(script_path)

    # Step 1: Delete everything in parent folder except TEMPFILE.PY
    status_label.config(text="Cleaning folder...")
    root.update_idletasks()
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        if item_path == script_path:
            continue
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")

    progress_var.set(10)

    # Step 2: Download GitHub repo ZIP
    status_label.config(text="Downloading launcher files...")
    root.update_idletasks()
    github_zip_url = "https://github.com/cringsimulator-a11y/TNTLauncher/archive/refs/heads/main.zip"
    try:
        r = requests.get(github_zip_url, stream=True, timeout=60)
        r.raise_for_status()
        zip_bytes = BytesIO(r.content)
    except Exception as e:
        status_label.config(text=f"Download failed: {e}")
        return

    progress_var.set(40)

    # Step 3: Extract ZIP into parent folder (no extra folder)
    status_label.config(text="Extracting files...")
    root.update_idletasks()
    try:
        with zipfile.ZipFile(zip_bytes) as zf:
            root_folder = zf.namelist()[0]  # e.g., "TNTLauncher-main/"
            files = zf.namelist()
            total_files = len(files)
            for i, member in enumerate(files, start=1):
                filename = os.path.join(parent_dir, os.path.relpath(member, start=root_folder))
                if member.endswith('/'):
                    os.makedirs(filename, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, "wb") as f:
                        f.write(zf.read(member))
                progress_var.set(40 + int(50 * (i / total_files)))  # progress from 40% to 90%
                root.update_idletasks()
    except Exception as e:
        status_label.config(text=f"Extraction failed: {e}")
        return

    progress_var.set(100)
    status_label.config(text="Installation complete!")

    # Step 4: Delete self
    try:
        os.remove(script_path)
    except Exception as e:
        print(f"Failed to delete installer: {e}")


def main():
    root = tk.Tk()
    root.title("TNTLauncher Installer")
    root.geometry("400x150")
    root.configure(bg="#121212")
    root.resizable(False, False)

    status_label = tk.Label(root, text="Starting...", fg="white", bg="#121212", font=("Segoe UI", 12))
    status_label.pack(pady=20)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=progress_var)
    progress_bar.pack(pady=10)

    threading.Thread(target=install_launcher, args=(progress_var, status_label, root), daemon=True).start()

    root.mainloop()


if __name__ == "__main__":
    main()
