from __future__ import annotations

from typing import List
from subprocess import Popen, PIPE
from os import path, mkdir

from PIL import Image

from config import CONFIG, BASE_DIR
from resize import zoom_fill


TMP_DIR = "/tmp/bspwm_wallpaper/"

if not path.exists(TMP_DIR):
    mkdir(TMP_DIR)


def get_output(*args: List[str]) -> str:
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8').strip()


def set_wallpaper(img_setter: Popen, focused_id: str, offset: int):
    # Workspace
    img_setter.stdin.write(f"{int(focused_id)-1}\n".encode("ASCII"))
    # X
    img_setter.stdin.write(f"{offset}\n".encode("ASCII"))
    # Y
    img_setter.stdin.write(f"{0}\n".encode("ASCII"))

    img_setter.stdin.flush()


def get_focused() -> str:
    return get_output("bspc", "query", "-D", "-d", "--names")


def copy_wallpapers():
    for workspace, name in CONFIG.items():
        if not name:
            continue
        img = Image.open(BASE_DIR + name)
        img = zoom_fill(img)
        img.convert("RGB").save(f"{TMP_DIR}{workspace}.bmp", optimize=True)


def main():
    ids = get_output('bspc', 'query', '-M').splitlines()
    names = get_output('bspc', 'query', '-M', '--names').splitlines()
    active_displays = get_output('xrandr', '--listactivemonitors').splitlines()

    def get_offset(display_name):
        for row_name in active_displays[1:]:
            if row_name.endswith(display_name):
                return row_name.split(" ")[3].split("+")[-2]

    offset_map = {
        _id: get_offset(name) for _id, name in zip(ids, names)
    }

    copy_wallpapers()

    img_setter = Popen(('./window.o', TMP_DIR), stdin=PIPE, stdout=PIPE)
    bspc = Popen(('bspc', 'subscribe', 'desktop_focus'),
                 stdout=PIPE, stderr=PIPE)

    while True:
        next_line = bspc.stdout.readline().strip()
        _, monitor_id, desktop_id = next_line.decode('utf-8').split(' ')

        set_wallpaper(img_setter, get_focused(), offset_map[monitor_id])
