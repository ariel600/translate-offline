import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Fonts", "segoeuib.ttf")
SIZE = 1024
BACK = (57, 73, 171, 255)
FRONT = (0, 172, 193, 255)
WHITE = (255, 255, 255, 255)


def letter(draw, center, char, size):
    font = ImageFont.truetype(FONT, size)
    left, top, right, bottom = draw.textbbox((0, 0), char, font=font)
    draw.text((center[0] - (left + right) / 2, center[1] - (top + bottom) / 2), char, font=font, fill=WHITE)


def render():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 40, 640, 600), radius=110, fill=BACK)
    d.polygon([(150, 560), (120, 770), (340, 590)], fill=BACK)
    letter(d, (250, 235), "\u05d0", 330)
    d.rounded_rectangle((364, 364, 1004, 944), radius=130, fill=WHITE)
    d.polygon([(840, 900), (950, 1020), (640, 930)], fill=WHITE)
    d.rounded_rectangle((394, 394, 974, 914), radius=110, fill=FRONT)
    d.polygon([(830, 890), (915, 985), (680, 900)], fill=FRONT)
    letter(d, (684, 654), "A", 400)
    return img


def main():
    img = render()
    img.save(os.path.join(OUT, "logo.png"))
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(os.path.join(OUT, "icon.ico"), sizes=sizes)
    print("Saved logo.png and icon.ico to", OUT)


if __name__ == "__main__":
    main()
