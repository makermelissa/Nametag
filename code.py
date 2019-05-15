"""
This is a name tag that is intended to be displayed on the PyBadge
Feel free to customize it to your heart's content
"""

import board
from micropython import const
import displayio
import digitalio
from gamepadshift import GamePadShift
import neopixel
import time
from math import sqrt, cos, sin, radians
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

# Button Constants
BUTTON_LEFT = const(128)
BUTTON_UP = const(64)
BUTTON_DOWN = const(32)
BUTTON_RIGHT = const(16)
BUTTON_SEL = const(8)
BUTTON_START = const(4)
BUTTON_A = const(2)
BUTTON_B = const(1)

# Customizations
NAME_STRING = "Blinka"
NAME_FONTNAME = "/fonts/Noto-18.bdf"
NEOPIXEL_COUNT = 5
BACKGROUND_COLOR = 0xFF0000
FOREGROUND_COLOR = 0xFFFFFF
BACKGROUND_TEXT_COLOR = 0xFFFFFF
FOREGROUND_TEXT_COLOR = 0x000000

# Default Values
brightness = 0.2
direction = 1
speed = 1

# Define the NeoPixel and Game Pad Objects
neopixels = neopixel.NeoPixel(board.NEOPIXEL, 5, brightness=brightness,
                              auto_write=False, pixel_order=neopixel.GRB)

pad = GamePadShift(digitalio.DigitalInOut(board.BUTTON_CLOCK),
                   digitalio.DigitalInOut(board.BUTTON_OUT),
                   digitalio.DigitalInOut(board.BUTTON_LATCH))

# Make the Display Background
splash = displayio.Group(max_size=20)
board.DISPLAY.show(splash)

color_bitmap = displayio.Bitmap(160, 128, 1)
color_palette = displayio.Palette(1)
color_palette[0] = BACKGROUND_COLOR

bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
splash.append(bg_sprite)

# Draw a Foreground Rectangle where the name goes
rect = Rect(0, 50, 160, 70, fill=FOREGROUND_COLOR)
splash.append(rect)

# Load the Hello font
hello_string = "HELLO"
large_font_name = "/fonts/Verdana-Bold-18.bdf"
large_font = bitmap_font.load_font(large_font_name)
large_font.load_glyphs(hello_string.encode('utf-8'))

# Load the "My Name Is" font
my_name_string = "MY NAME IS"
small_font_name = "/fonts/Arial-12.bdf"
small_font = bitmap_font.load_font(small_font_name)
small_font.load_glyphs(my_name_string.encode('utf-8'))

# Load the Name font
name_font_name = NAME_FONTNAME
name_font = bitmap_font.load_font(name_font_name)
name_font.load_glyphs(NAME_STRING.encode('utf-8'))

# Setup and Center the Hello Label
hello_text = Label(large_font, text=hello_string)
(x, y, w, h) = hello_text.bounding_box
hello_text.x = (80 - w // 2)
hello_text.y = 15
hello_text.color = BACKGROUND_TEXT_COLOR
splash.append(hello_text)

# Setup and Center the "My Name Is" Label
mni_text = Label(small_font, text=my_name_string)
(x, y, w, h) = mni_text.bounding_box
mni_text.x = (80 - w // 2)
mni_text.y = 35
mni_text.color = BACKGROUND_TEXT_COLOR
splash.append(mni_text)

# Setup and Center the Name Label
name_text = Label(name_font, text=NAME_STRING, line_spacing=0.75)
(x, y, w, h) = name_text.bounding_box
name_text.x = (80 - w // 2)
name_text.y = 85
name_text.color = FOREGROUND_TEXT_COLOR
splash.append(name_text)

# Remap the calculated rotation to 0 - 255
def remap(vector):
    return int(((255 * vector + 85) * 0.75) + 0.5)

# Calculate the Hue rotation starting with Red as 0 degrees
def rotate(degrees):
    cosA = cos(radians(degrees))
    sinA = sin(radians(degrees))
    red = cosA + (1.0 - cosA) / 3.0
    green = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
    blue = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
    return (remap(red), remap(green), remap(blue))

palette = []
pixels = []

# Generate a rainbow palette
for degree in range(0, 360):
    color = rotate(degree)
    palette.append(color[0] << 16 | color[1] << 8 | color[2])

# Create the Pattern
for x in range(0, NEOPIXEL_COUNT):
    pixels.append(x * 360 // NEOPIXEL_COUNT)

# Respond to the buttons
def check_buttons(buttons):
    global direction, speed, brightness
    if (buttons & BUTTON_RIGHT) > 0:
        direction = -1
    elif (buttons & BUTTON_LEFT) > 0:
        direction = 1
    elif (buttons & BUTTON_UP) > 0 and speed < 10:
        speed += 1
    elif (buttons & BUTTON_DOWN) > 0 and speed > 1:
        speed -= 1
    elif (buttons & BUTTON_A) > 0 and brightness < 0.5:
        brightness += 0.025
    elif (buttons & BUTTON_B) > 0 and brightness > 0.025:
        brightness -= 0.025

# Main Loop
current_buttons = pad.get_pressed()
last_read = 0
while True:
    for color in range(0, 360, speed):
        for index in range(0, NEOPIXEL_COUNT):
            palette_index = pixels[index] + color * direction
            if palette_index >= 360:
                palette_index -= 360
            elif palette_index < 0:
                palette_index += 360
            neopixels[index] = palette[palette_index]
        neopixels.show()
        neopixels.brightness = brightness
        # Reading buttons too fast returns 0
        if (last_read + 0.1) < time.monotonic():
            buttons = pad.get_pressed()
            last_read = time.monotonic()
        if current_buttons != buttons:
            check_buttons(buttons)
            current_buttons = buttons
