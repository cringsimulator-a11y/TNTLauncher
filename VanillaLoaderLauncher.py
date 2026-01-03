import json
import os
import subprocess
import minecraft_launcher_lib

base_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(base_dir, "launcher_data.json")
mc = os.path.join(os.getenv("APPDATA"), ".minecraft")

def load_data():
    if os.path.exists(data_file):
        return json.load(open(data_file, "r", encoding="utf-8"))
    return {"username": "Player", "vanilla_version": "1.21.1"}

def save_data():
    json.dump(data, open(data_file, "w", encoding="utf-8"), indent=2)

data = load_data()

version = data.get("vanilla_version", "1.21.1")
username = data.get("username", "Player")

version_dir = os.path.join(mc, "versions", version)

if not os.path.exists(version_dir):
    minecraft_launcher_lib.install.install_minecraft_version(version, mc)

version_json = json.load(open(os.path.join(version_dir, f"{version}.json"), "r", encoding="utf-8"))

libs = []
for lib in version_json["libraries"]:
    if "downloads" in lib and "artifact" in lib["downloads"]:
        libs.append(os.path.join(mc, "libraries", lib["downloads"]["artifact"]["path"]))

libs.append(os.path.join(version_dir, f"{version}.jar"))
classpath = ";".join(libs)

cmd = [
    "java",
    "-Xmx2G",
    "-Djava.library.path=" + os.path.join(version_dir, "natives"),
    "-cp", classpath,
    version_json["mainClass"],
    "--username", username,
    "--version", version,
    "--gameDir", mc,
    "--assetsDir", os.path.join(mc, "assets"),
    "--assetIndex", version_json["assetIndex"]["id"],
    "--uuid", "0",
    "--accessToken", "0",
    "--userType", "legacy"
]

subprocess.Popen(cmd)
