"""
This test will initialize the display using displayio
and draw a solid red background
"""

NAME_STRING = "@Maker\nMelissa"

import board
from micropython import const
import displayio
import digitalio
from gamepadshift import GamePadShift
import neopixel
from math import sqrt, cos, sin, radians
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font

brightness = 0.2
direction = 1
speed = 1

neopixels = neopixel.NeoPixel(board.NEOPIXEL, 5, brightness=brightness,
                              auto_write=False, pixel_order=neopixel.GRB)

# Make the display context
splash = displayio.Group(max_size=20)
board.DISPLAY.show(splash)

color_bitmap = displayio.Bitmap(160, 128, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFF0000

bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
splash.append(bg_sprite)

rect = Rect(0, 50, 160, 70, fill=0xffffff)
splash.append(rect)
"""
# Load the font
hello_string = "HELLO"
large_font_name = "/fonts/Verdana-Bold-18.bdf"
large_font = bitmap_font.load_font(large_font_name)
large_font.load_glyphs(hello_string.encode('utf-8'))

my_name_string = "MY NAME IS"
small_font_name = "/fonts/Arial-12.bdf"
small_font = bitmap_font.load_font(small_font_name)
small_font.load_glyphs(my_name_string.encode('utf-8'))

name_font_name = "/fonts/Comic-Bold-18.bdf"
name_font = bitmap_font.load_font(name_font_name)
name_font.load_glyphs(NAME_STRING.encode('utf-8'))

hello_text = Label(large_font, text=hello_string)
(x, y, w, h) = hello_text.bounding_box
hello_text.x = (80 - w // 2)
hello_text.y = 15
hello_text.color = 0xffffff
splash.append(hello_text)

mni_text = Label(small_font, text=my_name_string)
(x, y, w, h) = mni_text.bounding_box
mni_text.x = (80 - w // 2)
mni_text.y = 35
mni_text.color = 0xffffff
splash.append(mni_text)

name_text = Label(name_font, text=NAME_STRING, line_spacing=0.75)
(x, y, w, h) = name_text.bounding_box
print(h)
name_text.x = (80 - w // 2)
name_text.y = (100 - int(h / 2.75))
name_text.color = 0x0
splash.append(name_text)
"""
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
for x in range(0, 5):
    pixels.append(x * 360 // 5)

pad = GamePadShift(digitalio.DigitalInOut(board.BUTTON_CLOCK),
                   digitalio.DigitalInOut(board.BUTTON_OUT),
                   digitalio.DigitalInOut(board.BUTTON_LATCH))

BUTTON_LEFT = const(128)
BUTTON_UP = const(64)
BUTTON_DOWN = const(32)
BUTTON_RIGHT = const(16)
BUTTON_SEL = const(8)
BUTTON_START = const(4)
BUTTON_A = const(2)
BUTTON_B = const(1)

def get_buttons():
    buttons = []
    latch.value = False
    latch.value = True
    for value in range(0, 8):
        buttons.append(out.value)
        clock.value = False
        clock.value = True
    return buttons

def check_buttons(buttons):
    global direction, speed, brightness
    if buttons & BUTTON_RIGHT > 0:
        direction = -1
    elif buttons & BUTTON_LEFT > 0:
        direction = 1
    elif buttons & BUTTON_UP > 0 and speed < 10:
        speed += 1
    elif buttons & BUTTON_DOWN > 0 and speed > 1:
        speed -= 1
    elif buttons & BUTTON_A > 0 and brightness < 0.5:
        brightness += 0.05
    elif buttons & BUTTON_B > 0 and brightness > 0.05:
        brightness -= 0.05

old_buttons = 0
while True:
    for color in range(0, 360, speed):
        for index in range(0, 5):
            palette_index = pixels[index] + color * direction
            if palette_index >= 360:
                palette_index -= 360
            elif palette_index < 0:
                palette_index += 360
            neopixels[index] = palette[palette_index]
        neopixels.show()
        neopixels.brightness = brightness
        buttons = pad.get_pressed()
        if old_buttons != buttons:
            check_buttons(buttons)
            old_buttons = buttons
