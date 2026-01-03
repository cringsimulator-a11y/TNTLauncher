import os
import json
import subprocess
import tkinter as tk
import minecraft_launcher_lib
import webbrowser


mc_dir = os.path.join(os.getenv("APPDATA"), ".minecraft")
base_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(base_dir, "launcher_data.json")

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

def run_script(f):
    p = os.path.join(base_dir, f)
    if not os.path.exists(p):
        status.config(text=f"{f} not found")
        return

    status.config(text="Installing...")
    root.update_idletasks()

    if f.endswith(".py"):
        subprocess.Popen(["python", p], cwd=base_dir)
    else:  # .exe
        subprocess.Popen([p], cwd=base_dir)

    status.config(text="Installed")


def play_vanilla():
    run_script("VanillaLoaderLauncher.exe")

def play_fabric():
    run_script("FabricLoaderLauncher.exe")

def styled_dropdown(parent, values, key):
    var = tk.StringVar(value=data.get(key) or (values[0] if values else ""))
    box = tk.Frame(parent, bg="#2a2a2a", height=40)
    box.pack_propagate(False)

    lbl = tk.Label(box, textvariable=var, fg="white", bg="#2a2a2a",
                   font=("Segoe UI", 11), anchor="w", padx=12)
    lbl.pack(fill="both")

    lb = tk.Listbox(parent, bg="#1e1e1e", fg="white",
                    font=("Segoe UI", 11), height=6,
                    selectbackground="#3ba55d")

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

root = tk.Tk()
root.title("TNT Launcher")
root.state("zoomed")
root.configure(bg="#121212")

top = tk.Frame(root, bg="#121212")
top.pack(side="top", fill="x", pady=12)

pages = {}

for name in ("Home", "Mods", "Installations", "Extra Installs", "Help"):
    l = tk.Label(top, text=name, fg="white", bg="#121212",
                 font=("Segoe UI", 14), cursor="hand2")
    l.pack(side="left", padx=28)
    l.bind("<Button-1>", lambda e, n=name: set_page(n))


bottom = tk.Frame(root, bg="#1a1a1a", height=120)
bottom.pack(side="bottom", fill="x")
bottom.pack_propagate(False)

content = tk.Frame(root, bg="#121212")
content.pack(fill="both", expand=True)

home = tk.Frame(content, bg="#121212")
mods = tk.Frame(content, bg="#121212")
installs = tk.Frame(content, bg="#121212")
help_page = tk.Frame(content, bg="#121212")

pages["Home"] = home
pages["Mods"] = mods
pages["Installations"] = installs
pages["Help"] = help_page

try:
    banner = tk.PhotoImage(file="mofm.png")
    tk.Label(home, image=banner, bg="#121212").pack(pady=20)
except:
    tk.Label(home, text="TNT LAUNCHER", fg="white", bg="#121212",
             font=("Segoe UI", 48, "bold")).pack(pady=80)

tk.Label(home, text="Welcome to TNT Launcher",
         fg="#aaa", bg="#121212", font=("Segoe UI", 16)).pack()

tk.Label(mods, text="Mods Page",
         fg="white", bg="#121212", font=("Segoe UI", 22)).pack(expand=True)

tk.Label(help_page, text="Help Page",
         fg="white", bg="#121212", font=("Segoe UI", 22)).pack(expand=True)

tk.Label(installs, text="Download Vanilla Version",
         fg="white", bg="#121212", font=("Segoe UI", 18, "bold")).pack(pady=(30, 8))

vanilla_list = [v["id"] for v in minecraft_launcher_lib.utils.get_version_list() if v["type"] == "release"]
vd = styled_dropdown(installs, vanilla_list, "download_version")
vd.pack(pady=6, ipadx=220, ipady=6)

tk.Button(installs, text="INSTALL",
          bg="#3ba55d", fg="white",
          font=("Segoe UI", 12, "bold"),
          width=22,
          command=lambda: run_script("thevdowntest.exe")).pack(pady=12)

tk.Label(installs, text="Download Fabric Version",
         fg="white", bg="#121212", font=("Segoe UI", 18, "bold")).pack(pady=(30, 8))

tk.Button(installs, text="INSTALL",
          bg="#5865f2", fg="white",
          font=("Segoe UI", 12, "bold"),
          width=22,
          command=lambda: run_script("install_fabric.exe")).pack(pady=12)

tk.Label(installs, text="Fabric API Download",
         fg="white", bg="#121212", font=("Segoe UI", 18, "bold")).pack(pady=(30, 8))

fabric_api_versions = ["1.21.11", "1.21.10", "1.21.9", "1.21.8"]
fad = styled_dropdown(installs, fabric_api_versions, "FabricAPI_Version")
fad.pack(pady=6, ipadx=220, ipady=6)

tk.Button(installs, text="INSTALL",
          bg="#5865f2", fg="white",
          font=("Segoe UI", 12, "bold"),
          width=22,
          command=lambda: run_script("install_fabric_api.exe")).pack(pady=12)



# ----------------- EXTRA INSTALLS PAGE -----------------
extra_installs = tk.Frame(content, bg="#121212")
pages["Extra Installs"] = extra_installs

tk.Label(extra_installs, text="Extra Installs",
         fg="white", bg="#121212", font=("Segoe UI", 22, "bold")).pack(pady=(20, 20))

# --- Java 21 & SkyBlock Buttons (same row) ---
frame_js = tk.Frame(extra_installs, bg="#121212")
frame_js.pack(pady=(10, 12))

tk.Button(frame_js, text="INSTALL JAVA 21",
          bg="#ff6f00", fg="white", font=("Segoe UI", 12, "bold"),
          width=22,
          command=lambda: webbrowser.open("https://adoptium.net/es/download?link=https%3A%2F%2Fgithub.com%2Fadoptium%2Ftemurin21-binaries%2Freleases%2Fdownload%2Fjdk-21.0.9%252B10%2FOpenJDK21U-jdk_x64_windows_hotspot_21.0.9_10.msi&vendor=Adoptium")).pack(side="left", padx=10)

tk.Button(frame_js, text="INSTALL SKYBLOCK",
          bg="#ff6f00", fg="white", font=("Segoe UI", 12, "bold"),
          width=22, command=lambda: run_script("install_skyblock.exe")).pack(side="left", padx=10)

# --- OneBlock Button (alone row) ---
frame_oneblock = tk.Frame(extra_installs, bg="#121212")
frame_oneblock.pack(pady=(10, 12))

tk.Button(frame_oneblock, text="INSTALL ONEBLOCK",
          bg="#ff6f00", fg="white", font=("Segoe UI", 12, "bold"),
          width=22, command=lambda: run_script("install_oneblock.exe")).pack()










set_page("Home")

tk.Label(bottom, text="Username:",
         fg="white", bg="#1a1a1a",
         font=("Segoe UI", 12)).pack(side="left", padx=16)

username_entry = tk.Entry(bottom, font=("Segoe UI", 12), width=20)
username_entry.insert(0, data["username"])
username_entry.pack(side="left")
username_entry.bind("<FocusOut>", update_username)

vanilla_versions = get_vanilla_versions()
fabric_versions = get_fabric_versions()

vanilla_var = tk.StringVar(value=data.get("vanilla_version") or (vanilla_versions[0] if vanilla_versions else ""))
fabric_var = tk.StringVar(value=data.get("fabric_version") or (fabric_versions[0] if fabric_versions else ""))

tk.Label(bottom, text="Vanilla",
         fg="white", bg="#1a1a1a",
         font=("Segoe UI", 12)).pack(side="left", padx=18)

tk.OptionMenu(bottom, vanilla_var, *vanilla_versions, command=update_vanilla).pack(side="left")

tk.Button(bottom, text="PLAY",
          bg="#3ba55d", fg="white",
          font=("Segoe UI", 12, "bold"),
          command=play_vanilla).pack(side="left", padx=14, ipadx=26, ipady=10)

tk.Label(bottom, text="Fabric",
         fg="white", bg="#1a1a1a",
         font=("Segoe UI", 12)).pack(side="left", padx=18)

tk.OptionMenu(bottom, fabric_var, *fabric_versions, command=update_fabric).pack(side="left")

tk.Button(bottom, text="PLAY",
          bg="#5865f2", fg="white",
          font=("Segoe UI", 12, "bold"),
          command=play_fabric).pack(side="left", padx=14, ipadx=26, ipady=10)

status = tk.Label(bottom, text="", fg="#aaa", bg="#1a1a1a",
                  font=("Segoe UI", 11))
status.pack(side="right", padx=20)

root.mainloop()
