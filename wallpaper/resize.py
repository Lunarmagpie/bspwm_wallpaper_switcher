from PIL import Image


def strech(img: Image) -> Image:
    w, h = img.size
    if w != 1920 and h != 1080:
        img = img.resize((1920, 1080), Image.BILINEAR)
    return img


def zoom_fill(img: Image):
    w, h = img.size

    if w == 1920 and h == 1080:
        return img

    # Scale the image to fill horizontally
    ratio = 1920/w
    resize_img = img.resize((1920, int(h*ratio)), Image.BILINEAR)

    w, h = resize_img.size

    if h == 1080:
        return resize_img

    # If height is too big, crop off top and bottom
    if h > 1080:
        offset = (h-1080)/2
        resize_img = resize_img.crop((0, offset, 1920, h-offset))
        return resize_img

    # If height is too small, resize original image and crop off sides
    w, h = img.size
    ratio = 1080/h
    img = img.resize((int(ratio*w), 1080), Image.BILINEAR)

    w, h = img.size
    offset = (w-1920)/2
    img = img.crop((0, 0, w-offset*2, 1080))
    return img