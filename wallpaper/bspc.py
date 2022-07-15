from __future__ import annotations

from typing import List
from subprocess import Popen, PIPE
from os import path, mkdir, getcwd

from PIL import Image

from wallpaper.config import CONFIG, BASE_DIR, MAX_WIDTH, MAX_HEIGHT
from wallpaper.resize import zoom_fill


TMP_DIR = "/tmp/bspwm_wallpaper/"

if not path.exists(TMP_DIR):
    mkdir(TMP_DIR)


def get_output(*args: List[str]) -> str:
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8').strip()


def set_wallpaper(img_setter: Popen, focused_id: int, offset: int):
    # Workspace
    img_setter.stdin.write(f"{focused_id}\n".encode("ASCII"))
    # X
    img_setter.stdin.write(f"{offset}\n".encode("ASCII"))
    # Y
    img_setter.stdin.write(f"{0}\n".encode("ASCII"))

    img_setter.stdin.flush()


def get_focused(display_map: dict[str, int]) -> int:
    return display_map[get_output("bspc", "query", "-D", "-d", "--names")]


def copy_wallpapers(display_map: dict[str, int]):
    for workspace, name in CONFIG.items():
        if not name:
            continue

        display_number = display_map[workspace]

        img = Image.open(path.expanduser(BASE_DIR + name))
        img = zoom_fill(img)
        img.convert("RGB").save(f"{TMP_DIR}{display_number}.bmp", optimize=True)


def main():
    ids = get_output('bspc', 'query', '-M').splitlines()
    names = get_output('bspc', 'query', '-M', '--names').splitlines()
    active_displays = get_output('xrandr', '--listactivemonitors').splitlines()
    display_names = get_output('bspc', 'query', '-D', '--names')

    display_map = {
        k: v for v, k in enumerate(display_names.splitlines())
    }

    def get_offset(display_name):
        for row_name in active_displays[1:]:
            if row_name.endswith(display_name):
                return row_name.split(" ")[3].split("+")[-2]

    offset_map = {
        _id: get_offset(name) for _id, name in zip(ids, names)
    }

    copy_wallpapers(display_map)

    img_setter = Popen(
        (f'{path.realpath(__file__).replace("wallpaper/bspc.py", "")}/window.o', TMP_DIR), stdin=PIPE, stdout=PIPE)
    bspc = Popen(('bspc', 'subscribe', 'desktop_focus'),
                 stdout=PIPE, stderr=PIPE)

    img_setter.stdin.write(f"{MAX_WIDTH}\n".encode("ASCII"))
    img_setter.stdin.write(f"{MAX_HEIGHT}\n".encode("ASCII"))
    img_setter.stdin.flush()

    while True:
        next_line = bspc.stdout.readline().strip()
        _, monitor_id, desktop_id = next_line.decode('utf-8').split(' ')

        set_wallpaper(img_setter, get_focused(
            display_map), offset_map[monitor_id])
