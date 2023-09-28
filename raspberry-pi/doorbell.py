import argparse
import os
import sys
import time

import RPi.GPIO as GPIO
import board
import cv2
import neopixel
import numpy as np
import requests
from tflite_support.task import audio, core, processor, vision

import my_secrets

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# How many pixels are in the WS2812b strip?
MAX_PIXELS = 4

# What GPIO pin is associated with a condition?
DARK_INDICATOR_PIN = 2  # Physical pin 3

# Use the board internal definition for this
LED_STRIP_OUTPUT_PIN = board.D10  # Physical pin 19

# Pixel color values
ON = (255, 255, 255)  # White
OFF = (0, 0, 0)

_MARGIN = 10  # pixels
_ROW_SIZE = 10  # pixels
_FONT_SIZE = 1
_FONT_THICKNESS = 1
_TEXT_COLOR = (0, 0, 255)  # red


def get_category_name(detection_result: processor.DetectionResult) -> str:
    """
    Pull a specific category name from a detection result

    Args:
        detection_result: an object identification result

    Returns:
        the category name in a single string
    """
    category_name = None
    for detection in detection_result.detections:
        category = detection.categories[0]
        category_name = category.category_name
    return category_name


def visualize(image: np.ndarray, detection_result: processor.DetectionResult) -> np.ndarray:
    """
    Draws bounding boxes on the input image and return it.

  Args:
    image: The input RGB image.
    detection_result: The list of all "Detection" entities to be visualized.

  Returns:
    Image with bounding boxes.
  """
    for detection in detection_result.detections:
        # Draw bounding_box
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        cv2.rectangle(image, start_point, end_point, _TEXT_COLOR, 3)

        # Draw label and score
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)
        result_text = category_name + ' (' + str(probability) + ')'
        text_location = (_MARGIN + bbox.origin_x,
                         _MARGIN + _ROW_SIZE + bbox.origin_y)
        cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)

    return image


def cat_image_detected(model, timeout=30) -> bool:
    timeout_start = time.time()
    camera_id = 0
    width = 640
    height = 480
    num_threads = 4

    found = False
    # Variables to calculate FPS
    counter, fps = 0, 0
    start_time = time.time()

    # Start capturing video input from the camera
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Visualization parameters
    row_size = 20  # pixels
    left_margin = 24  # pixels
    text_color = (0, 0, 255)  # red
    font_size = 1
    font_thickness = 1
    fps_avg_frame_count = 10

    # Initialize the object detection model
    base_options = core.BaseOptions(file_name=model, use_coral=False, num_threads=num_threads)
    detection_options = processor.DetectionOptions(max_results=1, score_threshold=0.3)
    options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
    detector = vision.ObjectDetector.create_from_options(options)

    # Continuously capture images from the camera and run inference
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            sys.exit(
                'ERROR: Unable to read from webcam. Please verify your webcam settings.'
            )

        counter += 1
        image = cv2.flip(image, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Create a TensorImage object from the RGB image.
        input_tensor = vision.TensorImage.create_from_array(rgb_image)

        # Run object detection estimation using the model.
        detection_result = detector.detect(input_tensor)

        category = get_category_name(detection_result)

        print(f'{category}')
        if category == 'cat':
            found = True
            break

        time_hack = int(time.time() - timeout_start)

        if time_hack > timeout:
            print("timeout period reached")
            break

        # Draw keypoints and edges on input image
        image = visualize(image, detection_result)

        # Calculate the FPS
        if counter % fps_avg_frame_count == 0:
            end_time = time.time()
            fps = fps_avg_frame_count / (end_time - start_time)
            start_time = time.time()

        # Show the FPS
        fps_text = 'FPS = {:.1f}'.format(fps)
        text_location = (left_margin, row_size)
        cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    font_size, text_color, font_thickness)

        cv2.imshow('object_detector', image)

    cap.release()
    cv2.destroyAllWindows()

    return found


def doorbell(args) -> None:
    # Tensorflow setup
    model = CURRENT_DIR + '/models/' + str(args.model)
    video_model = CURRENT_DIR + '/models/' + str(args.videoModel)
    detection_pause = int(args.pauseAfterDetection)
    max_results = int(args.maxResults)
    score_threshold = float(args.scoreThreshold)
    overlapping_factor = float(args.overlappingFactor)
    num_threads = int(args.numThreads)
    enable_edgetpu = False

    # Set up the pixels for nighttime
    pixels = neopixel.NeoPixel(LED_STRIP_OUTPUT_PIN, MAX_PIXELS)
    GPIO.setwarnings(False)
    # Refer to pins by their Broadcom numbers
    GPIO.setmode(GPIO.BCM)
    # Configure the light sensor
    GPIO.setup(DARK_INDICATOR_PIN, GPIO.IN)

    base_options = core.BaseOptions(file_name=model, use_coral=enable_edgetpu, num_threads=num_threads)
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

    while True:
        if GPIO.input(DARK_INDICATOR_PIN):
            pixels.fill(OFF)

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
        # print("noise: ", noise)
        if noise == 'cat':
            if GPIO.input(DARK_INDICATOR_PIN):
                pixels.fill(ON)
            if cat_image_detected(video_model):
                print("Cat heard and seen")
                requests.post(my_secrets.REST_API_URL, headers={'content-type': 'application/json'})
                time.sleep(detection_pause)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Tensorflow Parameters
    parser.add_argument('--videoModel',
                        help='Name of the video classification model.',
                        required=False,
                        default='efficientdet_lite0.tflite')
    parser.add_argument('--model',
                        help='Name of the audio classification model.',
                        required=False,
                        default='yamnet.tflite')
    parser.add_argument('--maxResults',
                        help='Maximum number of results to show.',
                        required=False,
                        default=1)
    parser.add_argument('--overlappingFactor',
                        help='Target overlapping between adjacent inferences. Value must be in (0, 1)',
                        required=False,
                        default=0.5)
    parser.add_argument('--scoreThreshold',
                        help='The score threshold of classification results.',
                        required=False,
                        default=0.0)
    parser.add_argument('--numThreads',
                        help='Number of CPU threads to run the model.',
                        required=False,
                        default=4)
    parser.add_argument('--pauseAfterDetection',
                        help='Number of seconds to pause after a positive result.',
                        required=False,
                        default=120)
    args = parser.parse_args()
    doorbell(args)


if __name__ == '__main__':
    main()
