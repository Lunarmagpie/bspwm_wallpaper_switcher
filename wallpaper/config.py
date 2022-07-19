import toml
import os
import sys

if len(sys.argv) >= 2:
    config_path = sys.argv[1]
else:
    config_path = "~/.config/bspwm_wallpaper.toml"

with open(os.path.expanduser(config_path)) as f:
    config_file = toml.loads(f.read())

BASE_DIR = config_file.get("base_dir")
CONFIG = config_file.get("wallpaper")
MAX_WIDTH = config_file.get("width", 1920)
MAX_HEIGHT = config_file.get("height", 1080)

TMP_DIR = "/tmp/bspwm_wallpaper/"
