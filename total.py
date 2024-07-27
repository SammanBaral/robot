import cv2
import numpy as np
import threading
import time
import serial
import subprocess
import pyttsx3
from collections import deque

# Initialize the serial port communication with Arduino
arduino = serial.Serial('COM6', 115200, timeout=0.1)
arduino.close()
arduino.open()

# Global states
class GlobalState:
    def __init__(self):
        self.frame = None
        self.qr_detected = False
        self.running = True
        self.process_qr = False  # Add flag to indicate QR code processing

global_state = GlobalState()

# Capturing video from DroidCam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 200)
cap.set(4, 200)

# Function to send motor commands
def send_wheel_command(move1, move2):
    command = f"MOVE {move1} {move2}\n"
    print(f"Sending command: {command.strip()}")
    arduino.write(command.encode())  # Send the command to the Arduino

# Find path and return its contour
def findPath(hsv):
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([200, 255, 70])
    mask = cv2.inRange(hsv, lower_black, upper_black)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1)
    cv2.imshow("mask", mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    biggest = None
    biggest_size = -1
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > biggest_size:
            biggest = contour
            biggest_size = area
    return biggest

# Detect lines and calculate control signals
def detect_lines(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    contour = findPath(hsv)
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

# QR code detection function
def detect_qr_code(image):
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(image)
    if data:
        return True
    return False

# Text-to-speech and script execution function
def say_hello():
    # Initialize Text-to-Speech engine
    engine = pyttsx3.init()  # Initializing the Text-to-Speech engine

    # Define the message
    message = " This is the first ring King Tribhuvan gifted to then Crown Prince Mahendra. He then gave it to King Birendra before his coronation. "  # Defining the message

    # Use Text-to-Speech to say the message
    engine.say(message)  # Queue the message to be spoken
    engine.runAndWait()  # Wait until speaking is finished

    # Run another script if needed (optional)
    # subprocess.call(["python", "gptwala.py"])

# Function to run bolne.py script
# def run_bolne_script():
#     subprocess.call(["python", "bolne.py"])

# Thread function for QR code detection
def qr_detection_thread():
    global global_state
    while global_state.running:
        if global_state.frame is not None and not global_state.process_qr:
            qr_detected = detect_qr_code(global_state.frame)
            if qr_detected:
                global_state.qr_detected = True
                global_state.process_qr = True  # Set QR processing flag
                print("QR Code detected. Stopping the robot and processing QR code.")
                time.sleep(1)  # Wait for actions to complete
                send_wheel_command(0, 0)
                say_hello()  # Call the function to say the message
                # run_bolne_script()
                time.sleep(1)  # Wait for actions to complete
                global_state.qr_detected = False
                global_state.process_qr = False  # Reset QR processing flag

# Main camera capture thread
def camera_capture_thread():
    global global_state, cap
    while global_state.running:
        ret, frame = cap.read()
        if not ret:
            break
        global_state.frame = frame

        if not global_state.process_qr:  # Only process lines if not handling QR code
            original, center, hsv, res, line_detected = detect_lines(frame)
            cv2.imshow('hsv', hsv)
            cv2.imshow('res', res)
            if center is not None:
                cv2.imshow('Detected Lines', center)
            if original is not None:
                cv2.imshow('Contours', original)
            if not line_detected:
                print("No line detected. Sending stop command.")
                send_wheel_command(0, 0)

        if cv2.waitKey(1) & 0xFF == ord('d'):
            global_state.running = False
            break

if __name__ == "__main__":
    try:
        qr_thread = threading.Thread(target=qr_detection_thread)
        camera_thread = threading.Thread(target=camera_capture_thread)

        qr_thread.start()
        camera_thread.start()

        qr_thread.join()
        camera_thread.join()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        arduino.close()
        print("Serial connection closed.")
