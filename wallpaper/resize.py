from PIL import Image
from wallpaper.config import CONFIG


def strech(img: Image, width: int, height: int) -> Image:
    w, h = img.size
    if w != width and h != height:
        img = img.resize((width, height), Image.BILINEAR)
    return img


def zoom_fill(img: Image, width: int, height: int):
    w, h = img.size

    if w == width and h == height:
        return img

    # Scale the image to fill horizontally
    ratio = width/w
    resize_img = img.resize((width, int(h*ratio)), Image.BILINEAR)

    w, h = resize_img.size

    if h == height:
        return resize_img

    # If height is too big, crop off top and bottom
    if h > height:
        offset = (h-height)/2
        resize_img = resize_img.crop((0, offset, width, h-offset))
        return resize_img

    # If height is too small, resize original image and crop off sides
    w, h = img.size
    ratio = height/h
    img = img.resize((int(ratio*w), height), Image.BILINEAR)

    w, h = img.size
    offset = (w-width)/2
    img = img.crop((offset, 0, w-offset, height))

    return img
