import cv2
import mediapipe as mp
import time
import serial

class HandDetector():
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplexity = modelComplexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplexity, 
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.lmList = []

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        
        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                              (0, 255, 0), 2)
        
        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        
        if not self.lmList:
            return fingers
        
        if len(self.lmList) < max(self.tipIds) + 1:
            return fingers
        
        # Thumb
        if len(self.lmList) > self.tipIds[0] and len(self.lmList) > self.tipIds[0] - 1:
            if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        # Fingers
        for id in range(1, 5):
            if len(self.lmList) > self.tipIds[id] and len(self.lmList) > self.tipIds[id] - 2:
                if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        
        return fingers

def main(ser):
 
    cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
    detector = HandDetector()
    pTime = 0

    # Gesture detection variables
    gesture_duration_threshold = 10  # Number of frames to consider a gesture valid
    gesture_frames = {"FIST_BUMP": 0, "HAND_SHAKE": 0, "ELBOW_DOWN": 0, "WAVE_MOTION": 0}
    gesture_cooldown = {"FIST_BUMP": 0, "HAND_SHAKE": 0, "ELBOW_DOWN": 0, "WAVE_MOTION": 0}
    cooldown_time = 2  # Cooldown time in seconds

    while True:
        success, img = cap.read()
        if not success:
            break
        
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        
        if len(lmList) != 0:
            fingers = detector.fingersUp()
            print(fingers)
            
            # Define gesture commands
            if fingers == [0, 0, 1, 1, 1] or fingers == [0, 1, 1, 1, 1]: # Example gesture for FIST_BUMP
                gesture_frames["FIST_BUMP"] += 1
            else:
                gesture_frames["FIST_BUMP"] = 0

            if fingers == [0, 0, 0, 0, 0]:  # Example gesture for HAND_SHAKE
                gesture_frames["HAND_SHAKE"] += 1
            else:
                gesture_frames["HAND_SHAKE"] = 0

            if fingers == [0, 1, 0, 0, 0]:  # Example gesture for ELBOW_DOWN
                gesture_frames["ELBOW_DOWN"] += 1
            else:
                gesture_frames["ELBOW_DOWN"] = 0

            if fingers == [1, 1, 1, 1, 1]:  # Example gesture for WAVE_MOTION
                gesture_frames["WAVE_MOTION"] += 1
            else:
                gesture_frames["WAVE_MOTION"] = 0

            current_time = time.time()
            
            # Check gesture duration and send serial command if gesture is sustained and not in cooldown
            if gesture_frames["FIST_BUMP"] >= gesture_duration_threshold and current_time - gesture_cooldown["FIST_BUMP"] > cooldown_time:
                if ser:
                    ser.write(b'FIST_BUMP\n')
                    time.sleep(1)
                gesture_frames["FIST_BUMP"] = 0
                gesture_cooldown["FIST_BUMP"] = current_time

            if gesture_frames["HAND_SHAKE"] >= gesture_duration_threshold and current_time - gesture_cooldown["HAND_SHAKE"] > cooldown_time:
                if ser:
                    ser.write(b'HAND_SHAKE\n')
                gesture_frames["HAND_SHAKE"] = 0
                gesture_cooldown["HAND_SHAKE"] = current_time

            if gesture_frames["ELBOW_DOWN"] >= gesture_duration_threshold and current_time - gesture_cooldown["ELBOW_DOWN"] > cooldown_time:
                if ser:
                    ser.write(b'ELBOW_DOWN\n')
                gesture_frames["ELBOW_DOWN"] = 0
                gesture_cooldown["ELBOW_DOWN"] = current_time

            if gesture_frames["WAVE_MOTION"] >= gesture_duration_threshold and current_time - gesture_cooldown["WAVE_MOTION"] > cooldown_time:
                if ser:
                    ser.write(b'WAVE_MOTION\n')
                    print("wave")
                gesture_frames["WAVE_MOTION"] = 0
                gesture_cooldown["WAVE_MOTION"] = current_time

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)
        
        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()