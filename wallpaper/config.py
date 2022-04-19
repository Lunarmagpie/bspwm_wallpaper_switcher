import toml
import os

with open(os.path.expanduser("~/.config/bspwm_wallpaper.toml")) as f:
    config_file = toml.loads(f.read())

BASE_DIR = config_file.get("BASE_DIR")
MAX_WIDTH = config_file.get("MAX_WIDTH")
CONFIG = config_file.get("WALLPAPER")
