import toml
import os

with open(os.path.expanduser("~/.config/bspwm_wallpaper.toml")) as f:
    config_file = toml.loads(f.read())

BASE_DIR = config_file.get("base_dir")
CONFIG = config_file.get("wallpaper")
MAX_WIDTH = config_file.get("width", 1920)
MAX_HEIGHT = config_file.get("height", 1080)

TMP_DIR = "/tmp/bspwm_wallpaper/"
