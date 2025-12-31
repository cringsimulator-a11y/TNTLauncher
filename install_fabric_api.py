import os
import json
import requests

# ---------------- Setup paths ----------------
base_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(base_dir, "launcher_data.json")

mc_dir = os.path.join(os.getenv("APPDATA"), ".minecraft")  # Windows
mods_dir = os.path.join(mc_dir, "mods")
os.makedirs(mods_dir, exist_ok=True)

# ---------------- Load launcher data ----------------
def load_data():
    if os.path.exists(data_file):
        return json.load(open(data_file, "r", encoding="utf-8"))
    return {}

data = load_data()
mc_version = data.get("FabricAPI_Version")
if not mc_version:
    raise SystemExit("FabricAPI_Version (Minecraft version) not set")

# ---------------- Modrinth API ----------------
project_id = "P7dR8mSH"
api_url = f"https://api.modrinth.com/v2/project/{project_id}/version"

resp = requests.get(api_url, timeout=20)
resp.raise_for_status()
versions = resp.json()

selected = None
for v in versions:
    if mc_version in v.get("game_versions", []) and v.get("loaders") == ["fabric"]:
        selected = v
        break

if not selected:
    raise SystemExit(f"No Fabric API found for Minecraft {mc_version}")

file_info = None
for f in selected["files"]:
    if f["primary"]:
        file_info = f
        break
if not file_info:
    file_info = selected["files"][0]

download_url = file_info["url"]
filename = file_info["filename"]

# ---------------- Download to mods folder ----------------
out_path = os.path.join(mods_dir, filename)

print("Downloading Fabric API for Minecraft", mc_version)
print("File:", filename)
print("Saving to Minecraft mods folder:", out_path)

r = requests.get(download_url, stream=True, timeout=30)
r.raise_for_status()

with open(out_path, "wb") as f:
    for chunk in r.iter_content(8192):
        if chunk:
            f.write(chunk)

print("Fabric API successfully installed in your mods folder!")
