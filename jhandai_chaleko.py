import cv2
import numpy as np
import threading
import time
import pyttsx3
from cryptography.fernet import Fernet

from modules.NLP.STT import record_and_transcribe
from modules.NLP.create_JSON import create_museum_json
from modules.NLP.retrieval_model import answer_question
from modules.NLP.TSS import speak
from modules.NLP.NLG import generate_ai_response
from modules.CV import qr

# Global states
class GlobalState:
    def __init__(self):
        self.frame = None
        self.qr_detected = False
        self.nlp = False
        self.running = True
        self.process_qr = False

global_state = GlobalState()

# Capturing video from DroidCam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 200)
cap.set(4, 200)

# Function to send motor commands
def send_wheel_command(move1, move2):
    command = f"MOVE {move1} {move2}\n"
    # print(f"Sending command: {command.strip()}")
    # arduino.write(command.encode())  # Send the command to the Arduino

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
        return data
    return None

# Thread function for QR code detection
def qr_detection_thread():
    global global_state
    while global_state.running:
        if global_state.frame is not None and not global_state.process_qr:
            qr_data = qr.detect_qr_code(global_state.frame)
            if qr_data:
                print(f"QR Code detected with data: {qr_data}. Stopping the robot and processing QR code.")
                print(f"jai")
                global_state.qr_detected = True
                global_state.process_qr = True  # Set QR processing flag
                time.sleep(1)  # Wait for actions to complete
                send_wheel_command(0, 0)
                print(f"hi1")

                try:
                    print("Calling speak function")
                    # speak(qr_data)
                    print("Finished speaking")
                except Exception as e:
                    print(f"Error in speak function: {e}")
                print(f"hi")
                # time.sleep(1)  # Wait for actions to complete
                global_state.qr_detected = False
                global_state.process_qr = False  # Reset QR processing flag
                global_state.nlp = True
                handle_user_interaction()

# Function to handle user interaction
def handle_user_interaction():
    global global_state
    while global_state.nlp:
        speak("Do you have any questions, Yes or No ?")
        continue_response = record_and_transcribe()
        print(f"User response to continue: {continue_response}")
        if continue_response and continue_response.lower() == "no":
            global_state.nlp = False
            break

        user_question = record_and_transcribe()
        print(f"User question: {user_question}")
        if user_question is None:
            speak("I didn't quite get it. Please repeat.")
            continue

        retrieved_answer = answer_question(user_question)
        prompt = f"Question: {user_question}, context: {retrieved_answer}, based on context answer the question asked in humanly response"
        ai_response = generate_ai_response(prompt)
        speak(ai_response)

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
        create_museum_json()
        speak("Hello, I am Nitro, your museum assistant, we will start the tour now.")

        qr_thread = threading.Thread(target=qr_detection_thread)
        camera_thread = threading.Thread(target=camera_capture_thread)
        nlp_thread = threading.Thread(target=handle_user_interaction)
        qr_thread.start()
        camera_thread.start()
        nlp_thread.start()
        qr_thread.join()
        camera_thread.join()
        nlp_thread.join()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        # arduino.close()
        print("Serial connection closed.")
