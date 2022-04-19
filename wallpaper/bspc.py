from __future__ import annotations

from typing import List
from subprocess import Popen, PIPE
from os import system, path, mkdir

from config import CONFIG, BASE_DIR, MAX_WIDTH
from PIL import Image

TMP_DIR = "/tmp/bspwm_wallpaper/"

if not path.exists(TMP_DIR):
    mkdir(TMP_DIR)


def get_output(*args: List[str]) -> str:
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8').strip()


def set_wallpaper(focused_id: str):
    wallpaper_name = f"{TMP_DIR}{focused_id}.jpg"
    system(f"nitrogen --set-zoom-fill \"{wallpaper_name}\"")


def get_focused() -> str:
    return get_output("bspc", "query", "-D", "-d", "--names")


def copy_wallpapers():
    for workspace, name in CONFIG.items():
        if not name:
            continue
        img = Image.open(BASE_DIR + name)
        w, h = img.size

        if w > MAX_WIDTH:
            ratio = MAX_WIDTH/w
            new_h = h * ratio
            img = img.resize((MAX_WIDTH, int(new_h)),
                             Image.Resampling.BILINEAR)

        print(img.size)

        img.convert("RGB").save(f"{TMP_DIR}{workspace}.jpg")


def main():
    names_map = []

    ids = get_output('bspc', 'query', '-M').splitlines()
    names = get_output("bspc", "query", "-M", "--names").splitlines()

    id_map = {
        _id: name for _id, name in zip(ids, names)
    }

    copy_wallpapers()
    set_wallpaper(get_focused())

    bspc = Popen(('bspc', 'subscribe', 'desktop_focus'),
                 stdout=PIPE, stderr=PIPE)

    while True:
        next_line = bspc.stdout.readline().strip()
        _, monitor_id, desktop_id = next_line.decode('utf-8').split(' ')

        focused_id = get_focused()
        set_wallpaper(focused_id)
