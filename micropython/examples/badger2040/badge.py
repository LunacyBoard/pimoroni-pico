import time
import badger2040
import badger_os
import qrcode
import os

# Global Constants
WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT

IMAGE_WIDTH = 104

COMPANY_HEIGHT = 40
DETAILS_HEIGHT = 20
NAME_HEIGHT = HEIGHT - COMPANY_HEIGHT - (DETAILS_HEIGHT * 2) - 2
TEXT_WIDTH = WIDTH - IMAGE_WIDTH - 1

COMPANY_TEXT_SIZE = 0.7
DETAILS_TEXT_SIZE = 0.47

LEFT_PADDING = 5
NAME_PADDING = 10
DETAIL_SPACING = 10

DEFAULT_TEXT = """mustelid inc
H. Badger
RP2040
2MB Flash
E ink
296x128px
http://broken.com"""

BADGE_STATES = 2


def load_image(filename="badge-image.bin"):
    BADGE_IMAGE = bytearray(int(IMAGE_WIDTH * HEIGHT / 8))
    try:
        open(filename, "rb").readinto(BADGE_IMAGE)
    except OSError:
        try:
            import badge_image
            BADGE_IMAGE = bytearray(badge_image.data())
            del badge_image
        except ImportError:
            pass
    return BADGE_IMAGE


# ------------------------------
#      Utility functions
# ------------------------------

# Reduce the size of a string until it fits within a given width
def truncatestring(text, text_size, width):
    while True:
        length = display.measure_text(text, text_size)
        if length > 0 and length > width:
            text = text[:-1]
        else:
            text += ""
            return text



def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.pen(15)
    display.rectangle(ox, oy, size, size)
    display.pen(0)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)
                

# ------------------------------
#      Drawing functions
# ------------------------------

# Draw the badge, including user text
def draw_badge(img_state, BADGE_IMAGE, company, name, detail1_title, detail1_text, detail2_title, detail2_text, url):
    display.pen(0)
    display.clear()

    # Draw badge image or qr code
    if img_state == 0:
        display.image(BADGE_IMAGE, IMAGE_WIDTH, HEIGHT, WIDTH - IMAGE_WIDTH, 0)
    elif img_state == 1:
        code = qrcode.QRCode()                
        code.set_text(url)
        size, _ = measure_qr_code(104, code)
        print(size)
        top = int((HEIGHT / 2) - (size / 2))
        left = WIDTH - size
        print(left)
        display.pen(15)
        display.rectangle(left - 3 , 0, size + 2 , HEIGHT)
        draw_qr_code(left, top, 104, code)
        

    # Draw a border around the image
    display.pen(15)
    display.thickness(1)
    display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - 1, 0)
    display.line(WIDTH - IMAGE_WIDTH, 0, WIDTH - IMAGE_WIDTH, HEIGHT - 1)
    display.line(WIDTH - IMAGE_WIDTH, HEIGHT - 1, WIDTH - 1, HEIGHT - 1)
    display.line(WIDTH - 1, 0, WIDTH - 1, HEIGHT - 1)

    # Uncomment this if a white background is wanted behind the company
    # display.pen(15)
    # display.rectangle(1, 1, TEXT_WIDTH, COMPANY_HEIGHT - 1)

    # Draw the company
    display.pen(15)  # Change this to 0 if a white background is used
    display.font("sans")
    display.thickness(2) #default 3
    display.text(company, LEFT_PADDING, (COMPANY_HEIGHT // 2) + 1, COMPANY_TEXT_SIZE)

    # Draw a white background behind the name
    display.pen(15)
    display.thickness(1)
    display.rectangle(0, COMPANY_HEIGHT + 1, TEXT_WIDTH + 1, NAME_HEIGHT + 1)

    # Draw the name, scaling it based on the available width
    display.pen(0)
    display.font("sans")
    display.thickness(2)
    name_size = 2.0  # A sensible starting scale
    while True:
        name_length = display.measure_text(name, name_size)
        if name_length >= (TEXT_WIDTH - NAME_PADDING) and name_size >= 0.1:
            name_size -= 0.01
        else:
            display.text(name, (TEXT_WIDTH - name_length) // 2, (NAME_HEIGHT // 2) + COMPANY_HEIGHT + 1, name_size)
            break

    # Draw a white backgrounds behind the details
    display.pen(15)
    display.thickness(1)
    display.rectangle(0, HEIGHT - DETAILS_HEIGHT * 2, TEXT_WIDTH + 1, DETAILS_HEIGHT )
    display.rectangle(0, HEIGHT - DETAILS_HEIGHT, TEXT_WIDTH + 1, DETAILS_HEIGHT )

    # Draw the first detail's title and text
    display.pen(0)
    display.font("sans")
    display.thickness(1)
    name_length = display.measure_text(detail1_title, DETAILS_TEXT_SIZE)
    display.text(detail1_title, LEFT_PADDING, HEIGHT - ((DETAILS_HEIGHT * 3) // 2), DETAILS_TEXT_SIZE)
    display.thickness(1)
    display.text(detail1_text, 5 + name_length + DETAIL_SPACING, HEIGHT - ((DETAILS_HEIGHT * 3) // 2), DETAILS_TEXT_SIZE)

    # Draw the second detail's title and text
    display.thickness(1)
    name_length = display.measure_text(detail2_title, DETAILS_TEXT_SIZE)
    display.text(detail2_title, LEFT_PADDING, HEIGHT - (DETAILS_HEIGHT // 2), DETAILS_TEXT_SIZE)
    display.thickness(1)
    display.text(detail2_text, LEFT_PADDING + name_length + DETAIL_SPACING, HEIGHT - (DETAILS_HEIGHT // 2), DETAILS_TEXT_SIZE)


# ------------------------------
#        Program setup
# ------------------------------

# Create a new Badger and set it to update NORMAL
display = badger2040.Badger2040()
display.led(128)
display.update_speed(badger2040.UPDATE_NORMAL)


def load_data(filename="badge.txt"):
    # Open the badge file
    try:
        badge = open(filename, "r")
    except OSError:
        with open(filename, "w") as f:
            f.write(DEFAULT_TEXT)
            f.flush()
        badge = open(filename, "r")
    return ([badge.readline(), badge.readline(), badge.readline(), badge.readline(), badge.readline(), badge.readline(), badge.readline()])

def format_data_lines(datalines):
    datalines[0] = truncatestring(datalines[0], COMPANY_TEXT_SIZE, TEXT_WIDTH)
    get_badge_data[2] = truncatestring(get_badge_data[2], DETAILS_TEXT_SIZE, TEXT_WIDTH)
    get_badge_data[3] = truncatestring(get_badge_data[3], DETAILS_TEXT_SIZE,
                              TEXT_WIDTH - DETAIL_SPACING - display.measure_text(get_badge_data[2], DETAILS_TEXT_SIZE))

    get_badge_data[4] = truncatestring(get_badge_data[4], DETAILS_TEXT_SIZE, TEXT_WIDTH)
    get_badge_data[5] = truncatestring(get_badge_data[5], DETAILS_TEXT_SIZE,
                              TEXT_WIDTH - DETAIL_SPACING - display.measure_text(get_badge_data[4], DETAILS_TEXT_SIZE))
    return datalines


# ------------------------------
#       Main program
# ------------------------------
badge_state = 0
b_text_file = "badgeA.txt"
b_image_file = "badge-imageA.bin"

while True:
    # Buttons A-C switch between different cards
    if display.pressed(badger2040.BUTTON_A):
        b_text_file = "badgeA.txt"
        b_image_file = "badge-imageA.bin"
        
    if display.pressed(badger2040.BUTTON_B):
        b_text_file = "badgeB.txt"
        b_image_file = "badge-imageB.bin"
        
    if display.pressed(badger2040.BUTTON_C):
        b_text_file = "badgeC.txt"
        b_image_file = "badge-imageC.bin"
        
    # UP & DOWN switch between image displayed - currently the image or the QR code from the last row of text    
    if display.pressed(badger2040.BUTTON_UP):
        badge_state = badge_state -1 if badge_state > 0 else BADGE_STATES - 1
        
    if display.pressed(badger2040.BUTTON_DOWN):
        badge_state = badge_state + 1 if badge_state < BADGE_STATES - 1  else 0 

    get_badge_data = load_data(filename = b_text_file)
    get_badge_image = load_image(filename = b_image_file)
    get_badge_data_f = format_data_lines(get_badge_data)
    draw_badge(badge_state, get_badge_image, *get_badge_data_f)

    display.update()

    # If on battery, halt the Badger to save power, it will wake up if any of the front buttons are pressed
    display.halt()

