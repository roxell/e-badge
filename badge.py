import badger2040
import jpegdec
import qrcode

WIDTH = badger2040.WIDTH   # 296
HEIGHT = badger2040.HEIGHT  # 128

IMAGE_WIDTH = 80
IMAGE_HEIGHT = 80
IMAGE_X = WIDTH - IMAGE_WIDTH  # 216

COMPANY_HEIGHT = 30
DETAILS_HEIGHT = 22
NAME_HEIGHT = HEIGHT - COMPANY_HEIGHT - (DETAILS_HEIGHT * 2) - 2
TEXT_WIDTH = IMAGE_X - 1  # 215

LEFT_PADDING = 5
NAME_PADDING = 20
BADGE_PATH = "/badges/badge.txt"
PERSONAL_PATH = "/badges/personal.txt"

DEFAULT_BADGE = """FOSDEM 2026
"""

DEFAULT_PERSONAL = """Your Name
Email:
you@example.com
IRC:
handle
GitHub:
handle
GitLab:
handle
/badges/badge.jpg
+1234567890
"""

COMPANY_TEXT_SIZE = 0.6
DETAILS_TEXT_SIZE = 0.5

JOKES = [
    "Why do programmers\nprefer dark mode?\n\nBecause light\nattracts bugs.",
    "There are 10 types\nof people:\n\nthose who understand\nbinary and those\nwho do not.",
    "A SQL query walks\ninto a bar, sees two\ntables and asks:\n\nCan I join you?",
    "Why do Linux admins\nnever knock?\n\nThey always have\nthe right key.",
    "Hardware:\nthe part you can kick.\n\nSoftware:\nthe part you swear at.",
    "It works on\nmy machine.\n\n-- Every developer ever",
]

# Load jokes from file, fall back to built-in list
try:
    with open("/jokes.txt", "r") as f:
        file_jokes = [j.strip() for j in f.read().split("---") if j.strip()]
    if file_jokes:
        JOKES = file_jokes
except OSError:
    pass

# Setup
display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_NORMAL)
display.set_thickness(2)

jpeg = jpegdec.JPEG(display.display)

# Read conference name
try:
    badge = open(BADGE_PATH, "r")
except OSError:
    with open(BADGE_PATH, "w") as f:
        f.write(DEFAULT_BADGE)
        f.flush()
    badge = open(BADGE_PATH, "r")

company = badge.readline().strip()
badge.close()

# Read personal info
try:
    personal = open(PERSONAL_PATH, "r")
except OSError:
    with open(PERSONAL_PATH, "w") as f:
        f.write(DEFAULT_PERSONAL)
        f.flush()
    personal = open(PERSONAL_PATH, "r")

name = personal.readline().strip()
detail1_title = personal.readline().strip()
detail1_text = personal.readline().strip()
detail2_title = personal.readline().strip()
detail2_text = personal.readline().strip()
detail3_title = personal.readline().strip()
detail3_text = personal.readline().strip()
detail4_title = personal.readline().strip()
detail4_text = personal.readline().strip()
badge_image = personal.readline().strip()
phone = personal.readline().strip()
personal.close()


def truncatestring(text, text_size, width):
    while True:
        length = display.measure_text(text, text_size)
        if length > 0 and length > width:
            text = text[:-1]
        else:
            return text


# Collect detail 2-4 as (label, value) pairs, skip empty values
detail_notes = [(title.rstrip(":"), text)
                for title, text in ((detail2_title, detail2_text),
                                    (detail3_title, detail3_text),
                                    (detail4_title, detail4_text))
                if text]

company_t = truncatestring(company, COMPANY_TEXT_SIZE, TEXT_WIDTH)

# Build vCard from badge config
name_parts = name.split(" ", 1)
if len(name_parts) == 2:
    vcard_n = name_parts[1] + ";" + name_parts[0]
else:
    vcard_n = name_parts[0]
VCARD = "BEGIN:VCARD\nVERSION:3.0\nN:" + vcard_n + "\nFN:" + name
if detail1_text:
    VCARD += "\nEMAIL:" + detail1_text
if phone:
    VCARD += "\nTEL:" + phone
if detail_notes:
    VCARD += "\nNOTE:" + ", ".join(l + ": " + t for l, t in detail_notes)
VCARD += "\nEND:VCARD"


# ------------------------------
#      Screen A: Badge
# ------------------------------

def draw_badge():
    display.set_pen(0)
    display.clear()

    # Image top-right
    try:
        jpeg.open_file(badge_image)
        jpeg.decode(IMAGE_X, 0)
    except Exception:
        display.set_pen(15)
        display.rectangle(IMAGE_X, 0, IMAGE_WIDTH, IMAGE_HEIGHT)

    # White divider between header and image
    display.set_pen(15)
    display.line(IMAGE_X - 1, 0, IMAGE_X - 1, IMAGE_HEIGHT)

    # Company name
    display.set_pen(15)
    display.set_font("serif")
    display.text(company_t, LEFT_PADDING, (COMPANY_HEIGHT // 2) + 1,
                 TEXT_WIDTH, COMPANY_TEXT_SIZE)

    # Name background (left of image, then full width below image)
    display.set_pen(15)
    display.rectangle(0, COMPANY_HEIGHT + 1, TEXT_WIDTH,
                      IMAGE_HEIGHT - COMPANY_HEIGHT - 1)
    display.rectangle(0, IMAGE_HEIGHT, WIDTH,
                      COMPANY_HEIGHT + NAME_HEIGHT - IMAGE_HEIGHT)

    # Name text
    display.set_pen(0)
    display.set_font("sans")
    name_w = TEXT_WIDTH - LEFT_PADDING * 2
    name_size = 0.8
    while True:
        name_length = display.measure_text(name, name_size)
        if name_length >= (name_w - NAME_PADDING) and name_size >= 0.1:
            name_size -= 0.01
        else:
            display.text(name, (TEXT_WIDTH - name_length) // 2,
                         (NAME_HEIGHT // 2) + COMPANY_HEIGHT + 1,
                         TEXT_WIDTH, name_size)
            break

    # Contact details full width
    display.set_pen(15)
    display.rectangle(0, HEIGHT - DETAILS_HEIGHT * 2, WIDTH, DETAILS_HEIGHT - 1)
    display.rectangle(0, HEIGHT - DETAILS_HEIGHT, WIDTH, DETAILS_HEIGHT - 1)

    display.set_pen(0)
    display.set_font("sans")

    # Fixed value column at 100px so labels never overlap values
    label_col = 100
    val_w = WIDTH - label_col - LEFT_PADDING

    row1_y = HEIGHT - ((DETAILS_HEIGHT * 3) // 2)
    row2_y = HEIGHT - (DETAILS_HEIGHT // 2)

    display.text(detail1_title, LEFT_PADDING, row1_y, label_col, DETAILS_TEXT_SIZE)
    display.text(truncatestring(detail1_text, DETAILS_TEXT_SIZE, val_w),
                 label_col, row1_y, WIDTH, DETAILS_TEXT_SIZE)

    # Group handles by value: "IRC/GitHub: roxell, GitLab: aroxell"
    groups = {}
    for label, text in detail_notes:
        if text in groups:
            groups[text] += "/" + label
        else:
            groups[text] = label
    handles = [groups[v] + ": " + v for v in groups]
    handles_text = ", ".join(handles)
    display.text(truncatestring(handles_text, DETAILS_TEXT_SIZE,
                                WIDTH - LEFT_PADDING * 2),
                 LEFT_PADDING, row2_y, WIDTH, DETAILS_TEXT_SIZE)

    display.update()


# ------------------------------
#      Screen B: Joke
# ------------------------------

joke_index = 0


def draw_joke():
    global joke_index
    display.set_pen(15)
    display.clear()

    display.set_pen(0)
    display.set_font("sans")
    display.set_thickness(2)

    joke = JOKES[joke_index % len(JOKES)]
    joke_index += 1

    # Draw joke lines
    display.set_font("sans")
    y = 10
    for line in joke.split("\n"):
        display.text(line, LEFT_PADDING, y, WIDTH - LEFT_PADDING * 2, 0.45)
        y += 18

    display.update()


# ------------------------------
#      Screen C: QR Contact
# ------------------------------

def draw_qr():
    display.set_pen(15)
    display.clear()

    code = qrcode.QRCode()
    code.set_text(VCARD)

    size, _ = code.get_size()
    module_size = (HEIGHT - 10) // size
    qr_width = module_size * size
    qr_x = WIDTH - qr_width - 5
    qr_y = (HEIGHT - qr_width) // 2

    # Draw QR code on right side
    display.set_pen(0)
    for x_mod in range(size):
        for y_mod in range(size):
            if code.get_module(x_mod, y_mod):
                display.rectangle(qr_x + x_mod * module_size,
                                  qr_y + y_mod * module_size,
                                  module_size, module_size)

    # Contact info on left side
    left_w = qr_x - LEFT_PADDING * 2
    display.set_pen(0)
    display.set_font("sans")
    display.set_thickness(2)
    display.text(name, LEFT_PADDING, 10, left_w, 0.6)
    display.text(company, LEFT_PADDING, 33, left_w, 0.6)
    display.text(detail1_text, LEFT_PADDING, 56, left_w, 0.5)
    y = 72
    for label, text in detail_notes:
        display.text(label + ": " + text, LEFT_PADDING, y, left_w, 0.5)
        y += 14

    display.set_thickness(2)

    display.update()


# ------------------------------
#       Main program
# ------------------------------

current_screen = "badge"
draw_badge()

while True:
    display.keepalive()

    if display.pressed(badger2040.BUTTON_A) and current_screen != "badge":
        current_screen = "badge"
        draw_badge()
    elif display.pressed(badger2040.BUTTON_B):
        current_screen = "joke"
        draw_joke()
    elif display.pressed(badger2040.BUTTON_C) and current_screen != "qr":
        current_screen = "qr"
        draw_qr()

    display.halt()
