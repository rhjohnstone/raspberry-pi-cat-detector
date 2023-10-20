"""
DoorBellLightsController Class

This class allows you to control lights based on a dark indicator sensor using a motion sensor or other sensor.
It manages turning on and off the lights based on the darkness detected by the sensor.

Example Usage:
1. Create a logger to capture events and initialize the DoorBellLightsController.
2. Continuously check and control the lights based on darkness conditions.

"""

import logging
import sys
import time

import RPi.GPIO as GPIO
# Import necessary libraries
import board
import neopixel


class DoorBellLightsController:
    """
    Controller for managing lights associated with a doorbell.

    This class allows you to control lights based on a dark indicator sensor using a motion sensor or other sensor.

    Args:
        dark_indicator_pin (int): The GPIO pin number connected to the dark indicator sensor.
        led_strip_pin (board.Pin): The pin used to control the LED strip.
        logger (logging.Logger, optional): The logger to use for logging events. Defaults to None.
        max_pixels (int, optional): The maximum number of pixels in the LED strip. Defaults to 4.

    Attributes:
        dark_indicator_pin (int): The GPIO pin number connected to the dark indicator sensor.
        led_strip_pin (board.Pin): The pin used to control the LED strip.
        max_pixels (int): The maximum number of pixels in the LED strip.
        logger (logging.Logger or None): The logger used for logging events.

    Methods:
        _is_dark(): Check if it's dark based on the dark indicator sensor.
        turn_on(): Turn on the lights if it's dark and log the event.
        turn_off(): Turn off the lights if it's dark and log the event.
    """

    def __init__(self, dark_indicator_pin, led_strip_pin, logger=None, max_pixels=4):
        self.dark_indicator_pin = dark_indicator_pin
        self.led_strip_pin = led_strip_pin
        self.max_pixels = max_pixels
        self.logger = logger

        # Initialize neopixel
        self.pixels = neopixel.NeoPixel(self.led_strip_pin, self.max_pixels, auto_write=False)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dark_indicator_pin, GPIO.IN)

    def _is_dark(self):
        """
        Check if it's dark based on the dark indicator sensor.

        Returns:
            bool: True if it's dark, False otherwise.
        """
        return GPIO.input(self.dark_indicator_pin)

    def turn_on(self):
        """
        Turn on the lights if it's dark and log the event.
        """
        if self._is_dark():
            self.pixels.fill((255, 255, 255))  # Set pixels to ON color (white)
            self.pixels.show()
            if self.logger:
                self.logger.info("Lights turned ON")

    def turn_off(self):
        """
        Turn off the lights if it's dark and log the event.
        """
        if self._is_dark():
            self.pixels.fill((0, 0, 0))  # Set pixels to OFF color (black)
            self.pixels.show()
            if self.logger:
                self.logger.info("Lights turned OFF")


if __name__ == "__main__":
    # Example usage with logger
    dark_pin = 2  # Physical pin 3
    led_pin = board.D10  # Physical pin 19

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    controller = DoorBellLightsController(dark_pin, led_pin, logger=logger)

    while True:
        controller.turn_on()  # Turn on the lights if it's dark and log the event
        time.sleep(30)  # Wait for 30 seconds
        controller.turn_off()  # Turn off the lights if it's dark and log the event
