"""
I call this the Cat Doorbell

The application first listens for a cat meowing, then looks to verify it can see the cat. Once both criteria are met,
it sends a notification message to me via a REST API.

Why does the app need to both hear and see the cat?  It is because the cat in question sometimes likes to meow for the
hell of it while outside.  But, if he is close to the door (and therefore the doorbell), and then starts to meow,
it means he truly wants inside.  So, if he can be heard _and_ seen while at the door, it is the right time to alert me.

This is basically a combination of 2 Tensorflow sample applications.  One application identifies an "object" by
sound, and the other by sight.  Here is the example code for the 2 apps:
  1. https://github.com/tensorflow/examples/blob/master/lite/examples/audio_classification/raspberry_pi/classify.py
  2. https://github.com/tensorflow/examples/blob/master/lite/examples/image_classification/raspberry_pi/classify.py

"""
import argparse
import datetime
import logging
import os
import socket
import sys
import time

import board
import cv2
import numpy as np
import requests
from tflite_support.task import audio, core, processor, vision

import my_secrets
from lights import DoorBellLightsController

TARGET = "cat"
MODEL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/models/yamnet.tflite"

# What GPIO pin is associated with a condition?
DARK_INDICATOR_PIN = 2  # Physical pin 3

# Use the board internal definition for this
LED_STRIP_OUTPUT_PIN = board.D10  # Physical pin 19

REQUEST_HEADER = {'content-type': 'application/json'}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def main():

    max_results = 1
    score_threshold = 0.0
    overlapping_factor = 0.5
    num_threads = 4
    enable_edgetpu = False

    base_options = core.BaseOptions(file_name=MODEL_PATH, use_coral=enable_edgetpu, num_threads=num_threads)
    classification_options = processor.ClassificationOptions(max_results=max_results, score_threshold=score_threshold)
    options = audio.AudioClassifierOptions(base_options=base_options, classification_options=classification_options)

    classifier = audio.AudioClassifier.create_from_options(options)

    audio_record = classifier.create_audio_record()
    tensor_audio = classifier.create_input_tensor_audio()

    input_length_in_second = float(len(tensor_audio.buffer)) / tensor_audio.format.sample_rate
    interval_between_inference = input_length_in_second * (1 - overlapping_factor)
    pause_time = interval_between_inference * 0.1
    last_inference_time = time.time()

    audio_record.start_recording()

    lights = DoorBellLightsController(DARK_INDICATOR_PIN, LED_STRIP_OUTPUT_PIN, logger=logger)

    logger.info("Starting main loop")
    while True:
        now = time.time()
        diff = now - last_inference_time
        if diff < interval_between_inference:
            time.sleep(pause_time)
            continue
        last_inference_time = now

        # Load the input audio and run classify.
        tensor_audio.load_from_audio_record(audio_record)
        result = classifier.classify(tensor_audio)

        classification = result.classifications[0]
        label_list = [category.category_name for category in classification.categories]
        noise = str(label_list[0]).lower()

        # print(f"noise: {noise}")

        if noise == TARGET:
            logger.info(f"Heard {noise}")


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.exception("-C R A S H-")
        requests.post(my_secrets.REST_CRASH_NOTIFY_URL, data=socket.gethostname(), headers=REQUEST_HEADER)
