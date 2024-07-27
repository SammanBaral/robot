import numpy as np
import  cv2

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