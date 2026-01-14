import os
import sys
import json
import subprocess
import tkinter as tk
import re
import minecraft_launcher_lib
import webbrowser
import threading
import io
import requests
from PIL import Image, ImageTk

ICONS = {}

script_dir = os.path.dirname(__file__)  # path to the script itself
def load_icon2(name, relative_path, size=32):
    path = os.path.join(script_dir, relative_path)
    img = Image.open(path).resize((size, size), Image.LANCZOS)
    # ... store img somewhere, e.g., in a dict
    print(f"Loaded {name} from {path}")

mc_dir = os.path.join(os.getenv("APPDATA"), ".minecraft")

def ensure_launcher_profiles():
    profiles_path = os.path.join(mc_dir, "launcher_profiles.json")

    if os.path.exists(profiles_path):
        return

    default_profiles = {
        "profiles": {},
        "settings": {
            "crashAssistance": True,
            "enableAdvanced": True,
            "enableAnalytics": True,
            "enableHistorical": True,
            "enableReleases": True,
            "enableSnapshots": False,
            "keepLauncherOpen": False,
            "profileSorting": "LastPlayed",
            "showGameLog": False,
            "showMenu": True,
            "soundOn": True
        },
        "version": 3
    }

    with open(profiles_path, "w", encoding="utf-8") as f:
        json.dump(default_profiles, f, indent=2)


if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

data_file = os.path.join(base_dir, "launcher_data.json")
MODS_DIR = os.path.join(mc_dir, "mods")
os.makedirs(MODS_DIR, exist_ok=True)

SEARCH_URL = "https://api.modrinth.com/v2/search"
VERSION_URL = "https://api.modrinth.com/v2/project/{}/version"


def load_data():
    if os.path.exists(data_file):
        return json.load(open(data_file, "r", encoding="utf-8"))
    return {
        "username": "Player",
        "vanilla_version": "",
        "fabric_version": "",
        "download_version": "",
        "FabricAPI_Version": ""
    }

def save_data():
    json.dump(data, open(data_file, "w", encoding="utf-8"), indent=2)

data = load_data()
ensure_launcher_profiles()

def get_vanilla_versions():
    out = []
    path = os.path.join(mc_dir, "versions")
    if not os.path.exists(path):
        return out
    for v in os.listdir(path):
        if v[0].isdigit() and os.path.exists(os.path.join(path, v, f"{v}.json")):
            out.append(v)
    return sorted(out, reverse=True)

def get_fabric_versions():
    out = []
    path = os.path.join(mc_dir, "versions")
    if not os.path.exists(path):
        return out
    for v in os.listdir(path):
        if v.startswith("fabric-loader") and os.path.exists(os.path.join(path, v, f"{v}.json")):
            out.append(v)
    return sorted(out, reverse=True)

def fabric_installed():
    versions_dir = os.path.join(mc_dir, "versions")
    if not os.path.exists(versions_dir):
        return False

    for v in os.listdir(versions_dir):
        if v.startswith("fabric-loader"):
            json_path = os.path.join(versions_dir, v, f"{v}.json")
            if os.path.exists(json_path):
                return True
    return False

def set_page(name):
    for p in pages.values():
        p.pack_forget()
    pages[name].pack(fill="both", expand=True)

def update_username(*_):
    data["username"] = username_entry.get()
    save_data()

def update_vanilla(v):
    data["vanilla_version"] = v
    save_data()

def update_fabric(v):
    data["fabric_version"] = v
    save_data()




def get_drive():
    return "D:\\" if os.path.exists("D:\\") else "C:\\"

BASE_DIR = os.path.join(get_drive(), "TNTLauncher")

def open_skins_page():
    skins_path = os.path.join(BASE_DIR, "skins.html")
    skins_path = os.path.abspath(skins_path)

    if not os.path.exists(skins_path):
        print("skins.html not found")
        return

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]

    for chrome in chrome_paths:
        if os.path.exists(chrome):
            subprocess.Popen([chrome, skins_path])
            return

    webbrowser.open(skins_path)


def run_script(f):
    p = os.path.join(base_dir, f)
    if not os.path.isfile(p):
        status.config(text=f"{f} not found")
        return
    status.config(text="Installing...")
    root.update_idletasks()
    try:
        if f.lower().endswith(".exe"):
            subprocess.Popen(p, cwd=base_dir, shell=True)
        else:
            subprocess.Popen([sys.executable, p], cwd=base_dir)
        status.config(text="Installed")
    except Exception as e:
        status.config(text=str(e))

def play_vanilla():
    run_script("VanillaLoaderLauncher.py")

def play_fabric():
    run_script("FabricLoaderLauncher.py")

def styled_dropdown(parent, values, key):
    var = tk.StringVar(value=data.get(key) or (values[0] if values else ""))
    box = tk.Frame(parent, bg="#2a2a2a", height=40)
    box.pack_propagate(False)
    lbl = tk.Label(
        box, textvariable=var, fg="white", bg="#2a2a2a",
        font=("Segoe UI", 11), anchor="w", padx=12
    )
    lbl.pack(fill="both")
    lb = tk.Listbox(
        parent, bg="#1e1e1e", fg="white",
        font=("Segoe UI", 11), height=6, selectbackground="#3ba55d"
    )
    for v in values:
        lb.insert("end", v)
    def toggle():
        if lb.winfo_ismapped():
            lb.place_forget()
        else:
            lb.place(x=box.winfo_x(), y=box.winfo_y()+42, width=box.winfo_width())
    def select(_):
        if not lb.curselection():
            return
        val = lb.get(lb.curselection())
        var.set(val)
        data[key] = val
        save_data()
        lb.place_forget()
    lbl.bind("<Button-1>", lambda e: toggle())
    lb.bind("<<ListboxSelect>>", select)
    return box


def download_skyblock():
    with open("launcher_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    fabric_version = data.get("fabric_version", "")
    mc_version = fabric_version.split("-")[-1]

    mods_dir = os.path.join(os.getenv("APPDATA"), ".minecraft", "mods")
    os.makedirs(mods_dir, exist_ok=True)

    r = requests.get(
        "https://api.modrinth.com/v2/project/skyblock-infinite/version",
        timeout=20
    )
    r.raise_for_status()

    versions = r.json()

    for v in versions:
        if (
            mc_version in v.get("game_versions", [])
            and "fabric" in v.get("loaders", [])
            and "fabric-loader" not in v.get("loaders", [])
        ):
            file = v["files"][0]
            path = os.path.join(mods_dir, file["filename"])

            with requests.get(file["url"], stream=True) as d:
                with open(path, "wb") as f:
                    for c in d.iter_content(8192):
                        if c:
                            f.write(c)
            return

    raise RuntimeError("No compatible Skyblock version found")


def download_java21():
    webbrowser.open(
        "http://adoptium.net/es/download?link=https%3A%2F%2Fgithub.com%2Fadoptium%2Ftemurin21-binaries%2Freleases%2Fdownload%2Fjdk-21.0.9%252B10%2FOpenJDK21U-jdk_x64_windows_hotspot_21.0.9_10.msi&vendor=Adoptium"
    )
def download_oneblock():
    with open("launcher_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    fabric_version = data.get("fabric_version", "")
    mc_version = fabric_version.split("-")[-1]

    mods_dir = os.path.join(os.getenv("APPDATA"), ".minecraft", "mods")
    os.makedirs(mods_dir, exist_ok=True)

    r = requests.get(
        "https://api.modrinth.com/v2/project/skyblock-infinite/version",
        timeout=20
    )
    r.raise_for_status()

    versions = r.json()

    for v in versions:
        if (
            mc_version in v.get("game_versions", [])
            and "fabric" in v.get("loaders", [])
            and "fabric-loader" not in v.get("loaders", [])
        ):
            file = v["files"][0]
            path = os.path.join(mods_dir, file["filename"])

            with requests.get(file["url"], stream=True) as d:
                with open(path, "wb") as f:
                    for c in d.iter_content(8192):
                        if c:
                            f.write(c)
            return

    raise RuntimeError("No compatible OneBlock version found")


def update_launcher():
    script_path = os.path.join(os.path.dirname(__file__), "Updater.py")
    subprocess.Popen([sys.executable, script_path])
    
def download_custom_skin_loader(json_path="launcher_data.json"):
    # Determine .minecraft folder
    mc_dir = os.path.join(os.getenv("APPDATA"), ".minecraft")
    mods_folder = os.path.join(mc_dir, "mods")
    os.makedirs(mods_folder, exist_ok=True)

    # Read launcher_data.json
    with open(json_path, "r") as f:
        data = json.load(f)

    fabric_version_str = data.get("fabric_version", "")
    if not fabric_version_str:
        print("Fabric version not found in launcher_data.json")
        return

    # Extract Minecraft version from fabric_version string
    mc_version = fabric_version_str.split("-")[-1]

    # Modrinth API to get versions of CustomSkinLoader
    mod_slug = "customskinloader"
    url = f"https://api.modrinth.com/v2/project/{mod_slug}/version?game_versions[]={mc_version}&loaders[]=fabric"

    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch mod info from Modrinth")
        return

    versions = response.json()
    if not versions:
        print(f"No CustomSkinLoader version found for Minecraft {mc_version}")
        return

    # Get the first (latest compatible) version
    file_info = versions[0]["files"][0]
    mod_download_url = file_info["url"]
    file_name = os.path.join(mods_folder, file_info["filename"])

    print(f"Downloading CustomSkinLoader for MC {mc_version} into '{mods_folder}'...")
    r = requests.get(mod_download_url, stream=True)
    r.raise_for_status()

    with open(file_name, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    print(f"Downloaded {file_info['filename']} to '{mods_folder}'")
    return file_name


# ---------- Modrinth Browser ----------
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

        self.LAUNCHER_DATA = self.load_launcher_data()
        self.MC_VERSION = self.get_mc_version()

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

    def load_launcher_data(self):
        try:
            with open("launcher_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def extract_mc_version(self, fabric_version):
        if not fabric_version:
            return None
        matches = re.findall(r"\d+\.\d+(?:\.\d+)?", fabric_version)
        return matches[-1] if matches else None

    def get_mc_version(self):
        fabric = self.LAUNCHER_DATA.get("fabric_version")
        mc = self.extract_mc_version(fabric)
        if mc:
            return mc
        return self.LAUNCHER_DATA.get("vanilla_version")

    def search(self):
        for w in self.container.winfo_children():
            w.destroy()
        q = self.search_entry.get().strip()
        self.status.config(text="Loading mods...")
        threading.Thread(
            target=self.fetch_mods,
            args=(q,),
            daemon=True
        ).start()

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
            self.root.after(
                0,
                lambda: self.status.config(
                    text=f"Found {len(mods)} Fabric mods (MC {self.MC_VERSION})"
                )
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: self.status.config(text=f"Error: {e}")
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
            mc_dir = os.path.join(os.getenv("APPDATA"), ".minecraft")
            mods_dir = os.path.join(mc_dir, "mods")
            os.makedirs(mods_dir, exist_ok=True)

            r = requests.get(VERSION_URL.format(project_id), timeout=20)
            r.raise_for_status()
            versions = r.json()

            for v in versions:
                if "fabric" not in v.get("loaders", []):
                    continue
                if self.MC_VERSION not in v.get("game_versions", []):
                    continue

                file = None
                for f in v.get("files", []):
                    name = f.get("filename", "").lower()
                    if "fabric-loader" in name:
                        continue
                    if f.get("primary") and name.endswith(".jar"):
                        file = f
                        break

                if not file:
                    for f in v.get("files", []):
                        name = f.get("filename", "").lower()
                        if "fabric-loader" in name:
                            continue
                        if name.endswith(".jar"):
                            file = f
                            break

                if not file:
                    continue

                path = os.path.join(mods_dir, file["filename"])

                with requests.get(file["url"], stream=True, timeout=60) as d:
                    d.raise_for_status()
                    with open(path, "wb") as out:
                        for chunk in d.iter_content(8192):
                            if chunk:
                                out.write(chunk)

                self.root.after(
                    0,
                    lambda: self.status.config(
                        text=f"Downloaded: {file['filename']}"
                    )
                )
                return

            self.root.after(
                0,
                lambda: self.status.config(
                    text=f"No compatible Fabric mod for MC {self.MC_VERSION}"
                )
            )

        except Exception as e:
            self.root.after(
                0,
                lambda: self.status.config(
                    text=f"Download error: {e}"
                )
            )


            
            
class ModrinthShaders:
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
        self.status.config(text="Loading shaders...")
        threading.Thread(
            target=self.fetch_shaders,
            args=(q,),
            daemon=True
        ).start()

    def fetch_shaders(self, query):
        params = {
            "query": query,
            "limit": 40,
            "facets": '[["project_type:shader"]]'
        }
        try:
            r = requests.get(SEARCH_URL, params=params, timeout=15)
            r.raise_for_status()
            shaders = r.json()["hits"]
            self.root.after(0, lambda: self.render_shaders(shaders))
            self.root.after(
                0,
                lambda: self.status.config(
                    text=f"Found {len(shaders)} shaders"
                )
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: self.status.config(text=f"Error: {e}")
            )

    def render_shaders(self, shaders):
        cols = 4
        row = col = 0
        for shader in shaders:
            card = self.create_card(self.container, shader)
            card.grid(row=row, column=col, padx=14, pady=14)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def create_card(self, parent, shader):
        card = tk.Frame(parent, bg="#1e1e1e", width=240, height=300)
        card.pack_propagate(False)

        icon_lbl = tk.Label(card, bg="#1e1e1e")
        icon_lbl.pack(pady=10)

        if shader.get("icon_url"):
            threading.Thread(
                target=self.load_icon,
                args=(shader["icon_url"], icon_lbl, shader["project_id"]),
                daemon=True
            ).start()

        tk.Label(
            card,
            text=shader.get("title", ""),
            fg="white",
            bg="#1e1e1e",
            font=("Segoe UI", 11, "bold"),
            wraplength=200,
            justify="center"
        ).pack(pady=(6, 2))

        tk.Label(
            card,
            text=shader.get("description", ""),
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
            command=lambda pid=shader["project_id"]: self.download(pid)
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
        self.status.config(text="Downloading shader...")
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
            if not versions:
                self.root.after(
                    0,
                    lambda: self.status.config(
                        text="No files found"
                    )
                )
                return
            MC_DIR = os.path.join(os.getenv("APPDATA"), ".minecraft")
            SHADERPACKS_DIR = os.path.join(MC_DIR, "shaderpacks")
            os.makedirs(SHADERPACKS_DIR, exist_ok=True)


            file = versions[0]["files"][0]
            path = os.path.join(SHADERPACKS_DIR, file["filename"])
            with requests.get(file["url"], stream=True) as d:
                with open(path, "wb") as f:
                    for c in d.iter_content(8192):
                        if c:
                            f.write(c)
            self.root.after(
                0,
                lambda: self.status.config(
                    text="Shader downloaded"
                )
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: self.status.config(
                    text=f"Download error: {e}"
                )
            )

   
                
class ModrinthResourcePacks:
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
        self.status.config(text="Loading resource packs...")
        threading.Thread(
            target=self.fetch_packs,
            args=(q,),
            daemon=True
        ).start()

    def fetch_packs(self, query):
        params = {
            "query": query,
            "limit": 40,
            "facets": '[["project_type:resourcepack"]]'
        }
        try:
            r = requests.get(SEARCH_URL, params=params, timeout=15)
            r.raise_for_status()
            packs = r.json()["hits"]
            self.root.after(0, lambda: self.render_packs(packs))
            self.root.after(
                0,
                lambda: self.status.config(
                    text=f"Found {len(packs)} resource packs"
                )
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: self.status.config(text=f"Error: {e}")
            )

    def render_packs(self, packs):
        cols = 4
        row = col = 0
        for pack in packs:
            card = self.create_card(self.container, pack)
            card.grid(row=row, column=col, padx=14, pady=14)
            col += 1
            if col >= cols:
                col = 0
                row += 1

    def create_card(self, parent, pack):
        card = tk.Frame(parent, bg="#1e1e1e", width=240, height=300)
        card.pack_propagate(False)

        icon_lbl = tk.Label(card, bg="#1e1e1e")
        icon_lbl.pack(pady=10)

        if pack.get("icon_url"):
            threading.Thread(
                target=self.load_icon,
                args=(pack["icon_url"], icon_lbl, pack["project_id"]),
                daemon=True
            ).start()

        tk.Label(
            card,
            text=pack.get("title", ""),
            fg="white",
            bg="#1e1e1e",
            font=("Segoe UI", 11, "bold"),
            wraplength=200,
            justify="center"
        ).pack(pady=(6, 2))

        tk.Label(
            card,
            text=pack.get("description", ""),
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
            command=lambda pid=pack["project_id"]: self.download(pid)
        ).pack(pady=8, ipadx=14, ipady=4)

        return card



    def download(self, project_id):
        self.status.config(text="Downloading resource pack...")
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
            if not versions:
                self.root.after(
                    0,
                    lambda: self.status.config(text="No files found")
                )
                return

            MC_DIR = os.path.join(os.getenv("APPDATA"), ".minecraft")
            RESOURCEPACKS_DIR = os.path.join(MC_DIR, "resourcepacks")
            os.makedirs(RESOURCEPACKS_DIR, exist_ok=True)

            file = versions[0]["files"][0]
            filename = file.get("filename") or file["url"].split("/")[-1]
            path = os.path.join(RESOURCEPACKS_DIR, filename)

            with requests.get(file["url"], stream=True) as d:
                with open(path, "wb") as f:
                    for c in d.iter_content(8192):
                        if c:
                            f.write(c)

            self.root.after(
                0,
                lambda: self.status.config(text="Resource pack downloaded")
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: self.status.config(text=f"Download error: {e}")
            )
            

# ---------- Launcher UI ----------
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("TNTLauncher")
root.geometry("1200x720")
root.configure(bg="#0b0b12")
root.resizable(False, False)

# THE LOGO THING CODE HERE STARTS
# ---------- SPLASH ----------
splash = tk.Frame(root, bg="#141420")
splash.place(relx=0, rely=0, relwidth=1, relheight=1)

icon_path = os.path.join(base_dir, "icons", "logo.png")
icon_img = Image.open(icon_path).resize((100, 100), Image.LANCZOS)
icon_photo = ImageTk.PhotoImage(icon_img)

splash.icon_photo = icon_photo
icon_label = tk.Label(splash, image=splash.icon_photo, bg="#141420")
icon_label.place(relx=0.5, rely=0.5, anchor="center")

# Force splash to render immediately
root.update()

# Function to hide splash after 10s
def hide_splash():
    splash.destroy()
    # Continue loading the rest of the UI here if you want

# Schedule splash removal
root.after(30000, hide_splash)


# ---------------- PAGE SWITCHER ----------------

pages = {}

def show_page(name):
    for p in pages.values():
        p.pack_forget()
    pages[name].pack(fill="both", expand=True)

# ---------------- SIDEBAR ----------------

sidebar = tk.Frame(root, bg="#0f0f18", width=90)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="🔥",
    fg="white",
    bg="#0f0f18",
    font=("Segoe UI", 28)
).pack(pady=20)

def nav_button(icon_name, page):
    return tk.Button(
        sidebar,
        text=f"   {page.capitalize()}",
        image=ICONS.get(icon_name),
        compound="left",
        anchor="w",
        font=("Segoe UI", 11, "bold"),
        bg="#141414",
        fg="white",
        activebackground="#1f1f1f",
        relief="flat",
        cursor="hand2",
        padx=14,
        command=lambda: show_page(page)
    )



load_icon2("home", "icons/home.png")
load_icon2("skins", "icons/skins.png")
load_icon2("settings", "icons/settings.png")
load_icon2("installs", "icons/install.png")
load_icon2("mods", "icons/mods.png")
load_icon2("shaders", "icons/shader.png")
load_icon2("packs", "icons/pack.png")

nav_button("home", "home").pack(pady=8, fill="x")
nav_button("skins", "skins").pack(pady=8, fill="x")
nav_button("settings", "settings").pack(pady=8, fill="x")
nav_button("installs", "installs").pack(pady=8, fill="x")
nav_button("mods", "mods").pack(pady=8, fill="x")
nav_button("shaders", "shaders").pack(pady=8, fill="x")
nav_button("packs", "packs").pack(pady=8, fill="x")


# ---------------- MAIN AREA ----------------

main = tk.Frame(root, bg="#0b0b12")
main.pack(fill="both", expand=True)

# ---------------- HOME PAGE ----------------

home = tk.Frame(main, bg="#0b0b12")
pages["home"] = home

tk.Label(
    home,
    text="Minecraft 1.20.1",
    fg="white",
    bg="#0b0b12",
    font=("Segoe UI", 28, "bold")
).pack(anchor="w", padx=40, pady=(30, 5))

tk.Label(
    home,
    text="Custom Modpack",
    fg="#7ddc6f",
    bg="#0b0b12",
    font=("Segoe UI", 12)
).pack(anchor="w", padx=40)

card = tk.Frame(home, bg="#141420")
card.pack(fill="both", expand=True, padx=40, pady=30)

tk.Label(
    card,
    text="Welcome to TNTLauncher",
    fg="white",
    bg="#141420",
    font=("Segoe UI", 24, "bold")
).pack(anchor="w", padx=30, pady=(30, 10))

tk.Label(
    card,
    text="Launch vanilla, mods, skins and more from one place.",
    fg="#aaa",
    bg="#141420",
    font=("Segoe UI", 13)
).pack(anchor="w", padx=30)

tk.Button(
    card,
    text="LAUNCH GAME",
    font=("Segoe UI", 15, "bold"),
    bg="#3ba55d",
    fg="white",
    activebackground="#2e8b57",
    relief="flat",
    cursor="hand2",
    width=18
).pack(anchor="w", padx=30, pady=30)

# ---------------- SKINS PAGE ----------------

Skins = tk.Frame(main, bg="#0b0b12")
pages["skins"] = Skins

tk.Label(
    Skins,
    text="Skins",
    fg="white",
    bg="#0b0b12",
    font=("Segoe UI", 28, "bold")
).pack(anchor="w", padx=40, pady=(30, 10))

skins_card = tk.Frame(Skins, bg="#141420")
skins_card.pack(fill="both", expand=True, padx=40, pady=30)

tk.Button(
    skins_card,
    text="Download Skin Mod",
    font=("Segoe UI", 12, "bold"),
    bg="#3ba55d",
    fg="white",
    activebackground="#2f8f4f",
    relief="flat",
    cursor="hand2",
    width=22,
    command=download_custom_skin_loader
).pack(pady=6)

tk.Button(
    skins_card,
    text="Open Skin Page",
    font=("Segoe UI", 12, "bold"),
    bg="#5865f2",
    fg="white",
    activebackground="#4752c4",
    relief="flat",
    cursor="hand2",
    width=22,
    command=open_skins_page
).pack(pady=6)

# ---------------- SETTINGS PAGE ----------------

settings = tk.Frame(main, bg="#0b0b12")
pages["settings"] = settings

tk.Label(
    settings,
    text="Settings",
    fg="white",
    bg="#0b0b12",
    font=("Segoe UI", 28, "bold")
).pack(anchor="w", padx=40, pady=(30, 10))

settings_card = tk.Frame(settings, bg="#141420")
settings_card.pack(fill="both", expand=True, padx=40, pady=30)


# ---------------- SETTINGS PAGE ----------------

installs = tk.Frame(main, bg="#0b0b12")
pages["installs"] = installs

tk.Label(
    installs,
    text="Installs",
    fg="white",
    bg="#0b0b12",
    font=("Segoe UI", 28, "bold")
).pack(anchor="w", padx=40, pady=(30, 10))

installs_card = tk.Frame(installs, bg="#141420")
installs_card.pack(fill="both", expand=True, padx=40, pady=30)

tk.Label(installs_card, text="Download Vanilla Version", fg="white", bg="#121212",
         font=("Segoe UI", 18, "bold")).pack(pady=(30, 8))
vanilla_list = [v["id"] for v in minecraft_launcher_lib.utils.get_version_list() if v["type"]=="release"]
vd = styled_dropdown(installs_card, vanilla_list, "download_version")
vd.pack(pady=6, ipadx=220, ipady=6)
tk.Button(installs_card, text="INSTALL", bg="#3ba55d", fg="white",
          font=("Segoe UI", 12, "bold"), width=22,
          command=lambda: run_script("thevdowntest.py")).pack(pady=12)
tk.Label(installs_card, text="Download Fabric Version", fg="white", bg="#121212",
         font=("Segoe UI", 18, "bold")).pack(pady=(30, 8))
tk.Button(installs_card, text="INSTALL", bg="#5865f2", fg="white",
          font=("Segoe UI", 12, "bold"), width=22,
          command=lambda: run_script("fabric-installer-1.1.0 (3).exe")).pack(pady=12)
tk.Label(installs_card, text="Fabric API Download", fg="white", bg="#121212",
         font=("Segoe UI", 18, "bold")).pack(pady=(30, 8))
fabric_api_versions = ["1.21.11","1.21.10","1.21.9","1.21.8"]
fad = styled_dropdown(installs_card, fabric_api_versions, "FabricAPI_Version")
fad.pack(pady=6, ipadx=220, ipady=6)
tk.Button(installs_card, text="INSTALL", bg="#5865f2", fg="white",
          font=("Segoe UI", 12, "bold"), width=22,
          command=lambda: run_script("install_fabric_api.py")).pack(pady=12)

# ---------------- SETTINGS PAGE ----------------

extra_installs = tk.Frame(main, bg="#0b0b12")
pages["extra_installs"] = extra_installs

tk.Label(
    extra_installs,
    text="Extra Installs",
    fg="white",
    bg="#0b0b12",
    font=("Segoe UI", 28, "bold")
).pack(anchor="w", padx=40, pady=(30, 10))

extra_installs_card = tk.Frame(extra_installs, bg="#141420")
extra_installs_card.pack(fill="both", expand=True, padx=40, pady=30)

tk.Label(
    extra_installs_card,
    text="Extra Installs",
    fg="white",
    bg="#121212",
    font=("Segoe UI", 22, "bold")
).pack(pady=(20, 14))


btn_frame = tk.Frame(extra_installs, bg="#121212")
btn_frame.pack(pady=10)


tk.Button(
    extra_installs_card,
    text="Download Skyblock",
    font=("Segoe UI", 12, "bold"),
    bg="#5865f2",
    fg="white",
    activebackground="#4752c4",
    relief="flat",
    cursor="hand2",
    width=22,
    command=download_skyblock
).pack(pady=6)


tk.Button(
    extra_installs_card,
    text="Download Oneblock",
    font=("Segoe UI", 12, "bold"),
    bg="#3ba55d",
    fg="white",
    activebackground="#2f8f4f",
    relief="flat",
    cursor="hand2",
    width=22,
    command=download_oneblock
).pack(pady=6)

tk.Button(
    extra_installs_card,
    text="Download Java 21",
    font=("Segoe UI", 12, "bold"),
    bg="#3ba55d",
    fg="white",
    activebackground="#2f8f4f",
    relief="flat",
    cursor="hand2",
    width=22,
    command=download_java21
).pack(pady=6)

# ---------------- SETTINGS PAGE ----------------

mods = tk.Frame(main, bg="#0b0b12")
pages["mods"] = mods

tk.Label(
    mods,
    text="Mods",
    fg="white",
    bg="#0f0f18",
    font=("Segoe UI", 28, "bold")
).pack(anchor="w", padx=40, pady=(30, 10))

ModrinthBrowser(mods)

# ---------------- SETTINGS PAGE ----------------

shaders = tk.Frame(main, bg="#0b0b12")
pages["shaders"] = shaders

tk.Label(
    shaders,
    bg="#141420",
    text="Shaders",
    fg="white",
    font=("Segoe UI", 28, "bold")
).pack(anchor="w", padx=40, pady=(30, 10))

ModrinthShaders(shaders)

# ---------------- SETTINGS PAGE ----------------

packs = tk.Frame(main, bg="#0b0b12")
pages["packs"] = packs

tk.Label(
    packs,
    text="Packs",
    bg="#0f0f18",
    fg="white",
    font=("Segoe UI", 28, "bold")
).pack(anchor="w", padx=40, pady=(30, 10))

ModrinthResourcePacks(packs)





tk.Label(home, text="Username:", fg="white", font=("Segoe UI", 12),bg="#0f0f18").pack(side="left", padx=16)
username_entry = tk.Entry(home, font=("Segoe UI",12), width=20, bg="#0f0f18",)
username_entry.insert(0, data["username"])
username_entry.pack(side="left")
username_entry.bind("<FocusOut>", update_username)

vanilla_versions = get_vanilla_versions()
fabric_versions = get_fabric_versions()
vanilla_var = tk.StringVar(value=data.get("vanilla_version") or (vanilla_versions[0] if vanilla_versions else ""))
fabric_var = tk.StringVar(value=data.get("fabric_version") or (fabric_versions[0] if fabric_versions else ""))

tk.Label(home, bg="#0f0f18", text="Vanilla", fg="white", font=("Segoe UI",12)).pack(side="left", padx=18)
tk.OptionMenu(home, vanilla_var, *vanilla_versions, command=update_vanilla).pack(side="left")
tk.Button(home, text="PLAY", bg="#3ba55d", fg="white", font=("Segoe UI",12,"bold"),
          command=play_vanilla).pack(side="left", padx=14, ipadx=26, ipady=10)

tk.Label(home, bg="#0f0f18", text="Fabric", fg="white", font=("Segoe UI",12)).pack(side="left", padx=18)
tk.OptionMenu(home, fabric_var, *fabric_versions, command=update_fabric).pack(side="left")
tk.Button(home, text="PLAY", bg="#5865f2", fg="white", font=("Segoe UI",12,"bold"),
          command=play_fabric).pack(side="left", padx=14, ipadx=26, ipady=10)

status = tk.Label(home, bg="#0f0f18", text="", fg="#aaa", font=("Segoe UI",11))
status.pack(side="right", padx=20)
# ---------------- START ----------------

show_page("home")
root.mainloop()
