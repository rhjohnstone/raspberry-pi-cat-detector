import sys
import time

import RPi.GPIO as GPIO
import board
import neopixel

# How many pixels are in the WS2812b strip?
MAX_PIXELS = 4

# What GPIO pin is associated with a condition?
DARK_INDICATOR_PIN = 2  # Physical pin 3

# Use the board internal definition for this
LED_STRIP_OUTPUT_PIN = board.D10  # Physical pin 19

# Pixel color values
ON = (255, 255, 255)  # White
OFF = (0, 0, 0)

# Set up the pixels for nighttime
pixels = neopixel.NeoPixel(LED_STRIP_OUTPUT_PIN, MAX_PIXELS)
GPIO.setwarnings(False)
# Refer to pins by their Broadcom numbers
GPIO.setmode(GPIO.BCM)
# Configure the light sensor
GPIO.setup(DARK_INDICATOR_PIN, GPIO.IN)

while True:
    try:
        if GPIO.input(DARK_INDICATOR_PIN):
            print("dark")
            pixels.fill(ON)
            time.sleep(120)
            pixels.fill(OFF)
        else:
            print("light")
        time.sleep(5)
    except KeyboardInterrupt:
        print("interrupt")
        pixels.fill(OFF)
        sys.exit()
