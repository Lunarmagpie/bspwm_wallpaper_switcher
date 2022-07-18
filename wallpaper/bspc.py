from __future__ import annotations

from typing import List
from subprocess import Popen, PIPE
from os import path, mkdir, getcwd
from dataclasses import dataclass

from PIL import Image

from wallpaper.config import CONFIG, BASE_DIR, MAX_WIDTH, MAX_HEIGHT
from wallpaper.resize import zoom_fill
from backgrounds import ImlibImage, BackgroundSetter


TMP_DIR = "/tmp/bspwm_wallpaper/"

if not path.exists(TMP_DIR):
    mkdir(TMP_DIR)


@dataclass
class MonitorInfo:
    width: int
    height: int
    x_offset: int
    y_offset: int


def get_output(*args: List[str]) -> str:
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8').strip()


def set_wallpaper(img_setter: BackgroundSetter, wallpaper: ImlibImage, monitor: MonitorInfo):
    img_setter.set_wallpaper(wallpaper, monitor.x_offset, monitor.y_offset)


def get_focused(display_map: dict[str, int]) -> int:
    return display_map[get_output("bspc", "query", "-D", "-d", "--names")]


def open_wallpapers(display_map: dict[str, int], monitor_map: dict[str, MonitorInfo]) -> dict[int, ImlibImage]:
    out = {}
    for workspace, name in CONFIG.items():
        if not name:
            continue

        display_number = display_map[workspace]

        img = Image.open(path.expanduser(BASE_DIR + name))
        monitor = monitor_map[get_output(
            'bspc', 'query', '-M', '-d', workspace)]
        img = zoom_fill(img, monitor.width, monitor.height)

        imgpath = f"{TMP_DIR}{display_number}.bmp"
        img.convert("RGB").save(
            imgpath)
        out[display_number] = ImlibImage(imgpath)
    return out


def main():
    ids = get_output('bspc', 'query', '-M').splitlines()
    names = get_output('bspc', 'query', '-M', '--names').splitlines()
    active_displays = get_output('xrandr', '--listactivemonitors').splitlines()
    display_names = get_output('bspc', 'query', '-D', '--names')

    display_map = {
        k: v for v, k in enumerate(display_names.splitlines())
    }

    def get_offset(display_name: str):
        for row_name in active_displays[1:]:
            if row_name.endswith(display_name):
                x_offset, y_offset = row_name.split(" ")[3].split("+")[-2:]
                width, height = [
                    sec.split("x")[-1] for sec in row_name.split(" ")[3].split("/")[:-1]]

                return MonitorInfo(int(width), int(height), int(x_offset), int(y_offset))

    offset_map = {
        _id: get_offset(name) for _id, name in zip(ids, names)
    }

    wallpapers = open_wallpapers(display_map, offset_map)

    bspc = Popen(('bspc', 'subscribe', 'desktop_focus'),
                 stdout=PIPE, stderr=PIPE)

    img_setter = BackgroundSetter(MAX_WIDTH, MAX_HEIGHT)

    set_wallpaper(img_setter, wallpapers[get_focused(
        display_map)], offset_map[get_output("bspc", "query", "-M")])

    while True:
        next_line = bspc.stdout.readline().strip()
        _, monitor_id, desktop_id = next_line.decode('utf-8').split(' ')

        set_wallpaper(img_setter, wallpapers[get_focused(
            display_map)], offset_map[monitor_id])
