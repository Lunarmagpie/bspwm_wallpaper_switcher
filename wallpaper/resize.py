from PIL import Image
from wallpaper.config import CONFIG, MAX_WIDTH, MAX_HEIGHT


def strech(img: Image) -> Image:
    w, h = img.size
    if w != MAX_WIDTH and h != MAX_HEIGHT:
        img = img.resize((MAX_WIDTH, MAX_HEIGHT), Image.BILINEAR)
    return img


def zoom_fill(img: Image):
    w, h = img.size

    if w == MAX_WIDTH and h == MAX_HEIGHT:
        return img

    # Scale the image to fill horizontally
    ratio = MAX_WIDTH/w
    resize_img = img.resize((MAX_WIDTH, int(h*ratio)), Image.BILINEAR)

    w, h = resize_img.size

    if h == MAX_HEIGHT:
        return resize_img

    # If height is too big, crop off top and bottom
    if h > MAX_HEIGHT:
        offset = (h-MAX_HEIGHT)/2
        resize_img = resize_img.crop((0, offset, MAX_WIDTH, h-offset))
        return resize_img

    # If height is too small, resize original image and crop off sides
    w, h = img.size
    ratio = MAX_HEIGHT/h
    img = img.resize((int(ratio*w), MAX_HEIGHT), Image.BILINEAR)

    w, h = img.size
    offset = (w-MAX_WIDTH)/2
    img = img.crop((offset, 0, w-offset, MAX_HEIGHT))

    return img
