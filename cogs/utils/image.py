from io import BytesIO

from PIL import Image

ASCII_CHARS = [
    ' ',
    "$",
    "@",
    "B",
    "%",
    "8",
    "&",
    "W",
    "M",
    "#",
    "*",
    "a",
    "h",
    "k",
    "b",
    "d",
    "p",
    "q",
    "w",
    "m",
    "O",
    "0",
    "Q",
    "L",
    "J",
    "X",
    "z",
    "v",
    "u",
    "n",
    "r",
    "j",
    "f",
    "t",
    "/",
    "\\",
    "|",
    "(",
    ")",
    "1",
    "{",
    "}",
    "[",
    "]",
    "?",
    "-",
    "_",
    "+",
    "~",
    "<",
    ">",
    "i",
    "!",
    "l",
    "I",
    ";",
    ":",
    ",",
    '"',
    "^",
    "`",
    "'",
    ".",
    " ",
]


async def get_bytes(bot, url):
    """gets bytes from a url, bot is needed for clientsession"""
    response = await bot.session.get(url)
    return await response.read()


def open_image(res):
    img = Image.open(BytesIO(res))
    return img


def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)

    return img.point(contrast)


def resize_image(img: Image, width=57):
    orig_width, orig_height = img.size
    ratio = orig_height / orig_width
    height = int((width * ratio) / 2)
    resized_image = img.resize((width, height))
    return resized_image


def gray_image(img: Image):
    grayscale_img = img.convert("L")
    return grayscale_img


def pixels_to_ascii(img: Image):
    pixels = img.getdata()
    characters = "".join([ASCII_CHARS[pixel // 20] for pixel in pixels])
    return characters


def image_to_ascii(img_bytes):
    pixels = pixels_to_ascii(
        gray_image(resize_image(change_contrast(open_image(img_bytes), 250)))
    )
    pixel_count = len(pixels)
    done = "\n".join(pixels[i : i + 57] for i in range(0, pixel_count, 57))
    return done
