import cv2
import numpy as np
import threading
import time
import speech_recognition as sr
import serial
import queue
import pyttsx3
import mediapipe as mp
from haat_ko_code import main as haat_ko_code_main
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
        self.frame2 = None
        self.qr_detected = False
        self.nlp = False
        self.running = True
        self.process_qr = False
        self.detect_qr = True
        self.qr_counterMartin = 0  # Initialize QR counter
        self.qr_counterTribhuvan = 0
        self.arduino = None
        self.command_queue = queue.Queue()
        self.hello_detected = False  # State to check for "hello"
        self.hand_command = None

global_state = GlobalState()

# Initialize video captures for two cameras
cap_line = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap_hand = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Function to send motor commands with retry logic
def send_wheel_command_thread():
    while global_state.running:
        try:
            move1, move2 = global_state.command_queue.get(timeout=1)
            command = f"MOVE {move1} {move2}\n"
            print(f"Sending command: {command.strip()}")
            if global_state.arduino and global_state.arduino.is_open:
                retries = 3
                for attempt in range(retries):
                    try:
                        global_state.arduino.write(command.encode())  # Send the command to the Arduino
                        break
                    except serial.SerialException as e:
                        print(f"Failed to send command: {e}. Retrying {attempt + 1}/{retries}")
                        time.sleep(1)
                else:
                    print("Failed to send command after retries")
            else:
                print("Arduino port not open")
        except queue.Empty:
            continue

def add_wheel_command(move1, move2):
    global_state.command_queue.put((move1, move2))

def arduino_connection_thread():
    while global_state.running:
        if not global_state.arduino or not global_state.arduino.is_open:
            try:
                global_state.arduino = serial.Serial('COM7', 115200, timeout=0.1)
                global_state.arduino.close()
                global_state.arduino.open()
                print("Arduino port opened")
            except serial.SerialException:
                print("Failed to open Arduino port")
        time.sleep(1)

def say_tribhuwan():
    add_wheel_command(6, 8)  # Modify these values as necessary
    time.sleep(1.7)  # Adjust the sleep time as needed for a 180
    add_wheel_command(0,0)  # Stop the robot

def say_martin():
    message = "ufffffffffff"
    speak(message)

def say_turning():
    add_wheel_command(6, 8)  # Modify these values as necessary
    time.sleep(1.7)  # Adjust the sleep time as needed for a 180
    add_wheel_command(-6,5)
    time.sleep(1)
    add_wheel_command(0,0)
    cap_line.release()
    cap_hand.release()
    cv2.destroyAllWindows()
    arduino_connection_thread.close()

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
                add_wheel_command(-6, 5)
            elif cx < 120:
                add_wheel_command(-4, 5)
            elif cx >= 190:
                add_wheel_command(-6, 4)
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
            qr_data = detect_qr_code(global_state.frame)
            if qr_data:
                global_state.qr_detected = True
                global_state.process_qr = True
                if qr_data == "tribhuwankoinfo":  
                    global_state.qr_counterTribhuvan += 1
                    if global_state.qr_counterTribhuvan < 2:
                        time.sleep(1)
                        add_wheel_command(0, 0)
                        say_tribhuwan()
                elif qr_data == "martinkoinfo":
                    global_state.qr_counterMartin += 1
                    if global_state.qr_counterMartin == 1:
                        time.sleep(1)
                        add_wheel_command(0, 0)
                        say_martin()
                        global_state.nlp = True
                        handle_user_interaction()
                elif qr_data == "endMaTurn":
                    time.sleep(1)
                    add_wheel_command(0, 0)
                    say_turning()

                global_state.qr_detected = False
                global_state.process_qr = False
                global_state.nlp = False

# Function to handle user interaction
def handle_user_interaction():
    global global_state
    while global_state.nlp:
        speak("Do you have any questions, Yes or No ?")
        continue_response = record_and_transcribe()
        print(f"User response to continue: {continue_response}")
        if continue_response and (continue_response.lower() == "no" or continue_response.lower() == "no no"):
            global_state.nlp = False
            break

        if continue_response is None:
            speak("I didn't quite get it. Please repeat.")
            continue
        retrieved_answer = answer_question(continue_response)
        prompt = f"Question: {continue_response}, context: {retrieved_answer}, based on context answer the question asked in humanly response"
        ai_response = generate_ai_response(prompt)
        speak(ai_response)

# Main camera capture thread
def camera_capture_thread():    
    global global_state, cap_line
    while global_state.running:
        ret, frame = cap_line.read()
        if not ret:
            break
       
        global_state.frame = frame

        if not global_state.process_qr and not global_state.nlp:  # Only process lines if not handling QR code or NLP interaction
            cropped = frame[100:250, 80:]
            original, center, hsv, res, line_detected = detect_lines(frame)
            cv2.imshow('hsv', hsv)
            cv2.imshow('res', res)
            if center is not None:
                cv2.imshow('Detected Lines', center)
            if original is not None:
                cv2.imshow('Contours', original)
            if not line_detected:
                print("No line detected. Sending stop command.")
                add_wheel_command(0, 0)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    global_state.running = False
    cap_line.release()
    cv2.destroyAllWindows()

def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            return command
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

def nlp_in_between():
    global global_state
    while global_state.running:
        if not global_state.nlp:
            command = recognize_speech()
            if command:
                command = command.lower()
                if command == "nitro":  # Check for the specific command 'nitro'
                    print("Detected command 'Nitro'")
                    add_wheel_command(0, 0)
                    global_state.nlp = True
                    handle_user_interaction()
# Hand detection and command processing
def hand_detection_thread():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    while global_state.running:
        ret, frame2 = cap_hand.read()
        if not ret:
            break

        global_state.frame2 = frame2

        frame_rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame2, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

                thumb_state = "open" if thumb_tip.y < index_tip.y else "closed"
                index_state = "open" if index_tip.y < middle_tip.y else "closed"
                middle_state = "open" if middle_tip.y < ring_tip.y else "closed"
                ring_state = "open" if ring_tip.y < pinky_tip.y else "closed"
                pinky_state = "open" if pinky_tip.y < thumb_tip.y else "closed"

                if index_state == "open" and middle_state == "closed" and ring_state == "closed" and pinky_state == "closed":
                    global_state.hand_command = "MOVE_FORWARD"
                elif index_state == "closed" and middle_state == "open" and ring_state == "closed" and pinky_state == "closed":
                    global_state.hand_command = "MOVE_BACKWARD"
                elif thumb_state == "closed" and index_state == "open" and middle_state == "open" and ring_state == "closed" and pinky_state == "closed":
                    global_state.hand_command = "TURN_LEFT"
                elif thumb_state == "closed" and index_state == "closed" and middle_state == "open" and ring_state == "open" and pinky_state == "closed":
                    global_state.hand_command = "TURN_RIGHT"
                elif thumb_state == "open" and index_state == "open" and middle_state == "open" and ring_state == "open" and pinky_state == "open":
                    global_state.hand_command = "STOP"

                if global_state.hand_command:
                    command = None
                    if global_state.hand_command == "MOVE_FORWARD":
                        command = "MOVE 10 10\n"
                    elif global_state.hand_command == "MOVE_BACKWARD":
                        command = "MOVE -10 -10\n"
                    elif global_state.hand_command == "TURN_LEFT":
                        command = "MOVE -10 10\n"
                    elif global_state.hand_command == "TURN_RIGHT":
                        command = "MOVE 10 -10\n"
                    elif global_state.hand_command == "STOP":
                        command = "MOVE 0 0\n"

                    if command and global_state.arduino and global_state.arduino.is_open:
                        global_state.arduino.write(command.encode())

        cv2.imshow("Hand Detection", frame2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    global_state.running = False

# # Line detection thread
# def line_detection_thread():
#     while global_state.running:
#         ret, frame = cap_line.read()
#         if not ret:
#             break

#         global_state.frame = frame
#         image, copy, hsv, res, line_detected = detect_lines(frame)

#         cv2.imshow("Original", image)
#         cv2.imshow("Path", copy)
#         cv2.imshow("Mask", res)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     global_state.running = False

# Main function to start threads
def main():
    arduino_thread = threading.Thread(target=arduino_connection_thread)
    arduino_thread.start()

    send_command_thread = threading.Thread(target=send_wheel_command_thread)
    send_command_thread.start()

    line_thread = threading.Thread(target=camera_capture_thread)
    line_thread.start()

    qr_thread = threading.Thread(target=qr_detection_thread)
    qr_thread.start()

    hand_thread = threading.Thread(target=hand_detection_thread)
    hand_thread.start()

    nlp_thread = threading.Thread(target=nlp_in_between)
    nlp_thread.start()

    # Wait for threads to finish
    line_thread.join()
    qr_thread.join()
    arduino_thread.join()
    send_command_thread.join()
    hand_thread.join()
    nlp_thread.join()

if __name__ == "__main__":
    main()
