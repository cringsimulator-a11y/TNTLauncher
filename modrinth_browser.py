import os
import json
import re
import threading
import io
import requests
import tkinter as tk
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "launcher_data.json")
MC_DIR = os.path.join(os.getenv("APPDATA"), ".minecraft")
MODS_DIR = os.path.join(MC_DIR, "mods")

SEARCH_URL = "https://api.modrinth.com/v2/search"
VERSION_URL = "https://api.modrinth.com/v2/project/{}/version"

os.makedirs(MODS_DIR, exist_ok=True)


def load_data():
    if os.path.exists(DATA_FILE):
        return json.load(open(DATA_FILE, "r", encoding="utf-8"))
    return {}


data = load_data()


def get_mc_version():
    fv = data.get("fabric_version", "")
    m = re.search(r"(\d+\.\d+(\.\d+)?)", fv)
    if m:
        return m.group(1)
    return data.get("vanilla_version")


MC_VERSION = get_mc_version()


class ModrinthBrowser:
    def __init__(self, parent):
        self.root = parent
        self.root.configure(bg="#121212")

        self.images = {}

        top = tk.Frame(self.root, bg="#121212")
        top.pack(fill="x", pady=12)

        self.search_entry = tk.Entry(top, font=("Segoe UI", 13), width=42)
        self.search_entry.pack(side="left", padx=12)

        tk.Button(
            top,
            text="Search",
            bg="#3ba55d",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=self.search
        ).pack(side="left")

        self.status = tk.Label(
            self.root,
            text="",
            fg="#aaa",
            bg="#121212",
            font=("Segoe UI", 10)
        )
        self.status.pack(anchor="w", padx=16)

        self.canvas = tk.Canvas(self.root, bg="#121212", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.root, command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.container = tk.Frame(self.canvas, bg="#121212")
        self.canvas.create_window((0, 0), window=self.container, anchor="nw")

        self.container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.search()

    def search(self):
        for w in self.container.winfo_children():
            w.destroy()

        q = self.search_entry.get().strip()
        self.status.config(text="Loading mods...")
        threading.Thread(target=self.fetch_mods, args=(q,), daemon=True).start()

    def fetch_mods(self, query):
        params = {
            "query": query,
            "facets": '[["categories:fabric"]]',
            "limit": 40
        }

        try:
            r = requests.get(SEARCH_URL, params=params, timeout=15)
            r.raise_for_status()
            mods = r.json()["hits"]

            self.root.after(0, lambda: self.render_mods(mods))
            self.root.after(0, lambda:
                self.status.config(text=f"Found {len(mods)} Fabric mods")
            )

        except Exception as e:
            self.root.after(0, lambda:
                self.status.config(text=f"Error: {e}")
            )

    def render_mods(self, mods):
        cols = 4
        row = col = 0

        for mod in mods:
            card = self.create_card(self.container, mod)
            card.grid(row=row, column=col, padx=14, pady=14)

            col += 1
            if col >= cols:
                col = 0
                row += 1

    def create_card(self, parent, mod):
        card = tk.Frame(parent, bg="#1e1e1e", width=240, height=300)
        card.pack_propagate(False)

        icon_lbl = tk.Label(card, bg="#1e1e1e")
        icon_lbl.pack(pady=10)

        if mod.get("icon_url"):
            threading.Thread(
                target=self.load_icon,
                args=(mod["icon_url"], icon_lbl, mod["project_id"]),
                daemon=True
            ).start()

        tk.Label(
            card,
            text=mod.get("title", ""),
            fg="white",
            bg="#1e1e1e",
            font=("Segoe UI", 11, "bold"),
            wraplength=200,
            justify="center"
        ).pack(pady=(6, 2))

        tk.Label(
            card,
            text=mod.get("description", ""),
            fg="#bbb",
            bg="#1e1e1e",
            font=("Segoe UI", 9),
            wraplength=200,
            justify="center"
        ).pack(pady=(0, 8))

        tk.Button(
            card,
            text="DOWNLOAD",
            bg="#5865f2",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            state="normal" if MC_VERSION else "disabled",
            command=lambda pid=mod["project_id"]: self.download(pid)
        ).pack(pady=8, ipadx=14, ipady=4)

        return card

    def load_icon(self, url, label, pid):
        try:
            r = requests.get(url, timeout=10)
            img = Image.open(io.BytesIO(r.content)).resize((96, 96))
            tkimg = ImageTk.PhotoImage(img)
            self.images[pid] = tkimg
            self.root.after(0, lambda: label.config(image=tkimg))
        except:
            pass

    def download(self, project_id):
        self.status.config(text="Downloading...")
        threading.Thread(
            target=self.download_thread,
            args=(project_id,),
            daemon=True
        ).start()

    def download_thread(self, project_id):
        try:
            r = requests.get(VERSION_URL.format(project_id), timeout=15)
            r.raise_for_status()
            versions = r.json()

            for v in versions:
                if "fabric" in v["loaders"] and MC_VERSION in v["game_versions"]:
                    file = v["files"][0]
                    path = os.path.join(MODS_DIR, file["filename"])

                    with requests.get(file["url"], stream=True) as d:
                        with open(path, "wb") as f:
                            for c in d.iter_content(8192):
                                if c:
                                    f.write(c)

                    self.root.after(0, lambda:
                        self.status.config(text="Downloaded successfully")
                    )
                    return

            self.root.after(0, lambda:
                self.status.config(text="No compatible version found")
            )

        except Exception as e:
            self.root.after(0, lambda:
                self.status.config(text=f"Download error: {e}")
            )
