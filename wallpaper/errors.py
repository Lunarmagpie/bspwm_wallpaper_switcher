from PIL import Image, ImageDraw, ImageFont
from wallpaper.config import MAX_WIDTH, MAX_HEIGHT, TMP_DIR
from backgrounds import BackgroundSetter, ImlibImage


def send_error(img_setter: BackgroundSetter, msg: str) -> None:
    img = Image.new("RGB", (MAX_WIDTH, MAX_HEIGHT), color=(230, 230, 230))

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font="UbuntuMono-R.ttf", size=48)
    draw.text((100, 100), f"ERROR:{msg}", fill=(0, 0, 0), font=font)

    img.save(f"{TMP_DIR}/error.bmp")
    img_setter.set_wallpaper(ImlibImage(f"{TMP_DIR}/error.bmp"), 0, 0)