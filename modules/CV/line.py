import os
import sys

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)
print(parent_dir)
# Add the parent directory to sys.path
sys.path.append(parent_dir)

import cv2
import numpy as np
from CV import path
from Kinematics.robo.signal_transfer import send_wheel_command 

# Detect lines and calculate control signals
def detect_lines(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    contour = path.findPath(hsv)
    mask = np.zeros_like(hsv[:, :, 0])
    if contour is not None:
        cv2.drawContours(mask, [contour], -1, 255, -1)
        mask = cv2.medianBlur(mask, 5)
    res = cv2.bitwise_and(image, image, mask=mask)
    copy = image.copy()
    if contour is not None:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.line(image, (cx, 0), (cx, 720), (255, 0, 0), 1)
            cv2.line(image, (0, cy), (1280, cy), (255, 0, 0), 1)
            cv2.drawContours(copy, [contour], -1, (0, 255, 0), 1)
            print(f"CX: {cx} CY: {cy}")
            if 120 < cx < 190:
                send_wheel_command(-6, 5)
            elif cx < 120:
                send_wheel_command(-4, 5)
            elif cx >= 190:
                send_wheel_command(-6, 4)
            return image, copy, hsv, res, True  # Line detected
    return image, copy, hsv, res, False  # No line detected
