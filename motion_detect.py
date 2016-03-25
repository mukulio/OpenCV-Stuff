from collections import deque
import numpy as np
import argparse
import imutils
import cv2


# define the lower and upper boundries of the "green"
# ball and then initialize a space of tracked points
lower = (29, 86, 6)
upper = (64, 255, 255)
pts = deque()
erode_iter = 1
dilate_iter = 5
max_radius = 10
pts = deque(maxlen=64)

def stationary(pt1, pt2):
    if pt2[1] - pt1[1] < 5:
        return True
    else:
        return False

def detectTrend(pts):
    # stationary, up, down, left, right
    movements = [0, 0, 0, 0, 0]
    for i in xrange(1, len(pts)):
        print "[X2: %d, X1: %d] [Y2: %d, Y1: %d]" % (pts[i][0], pts[i - 1][0], pts[i][1], pts[i - 1][1])

        if pts[i][0] < pts[i - 1][0]:
            movements[3] += 1
        elif pts[i][0] > pts[i - 1][0]:
            movements[4] += 1

        if pts[i][1] > pts[i - 1][1]:
            movements[1] += 1
        elif pts[i][1] < pts[i - 1][1]:
            movements[2] += 1
        else:
            movements[0] += 1

    index = movements.index(max(movements))
    if (index == 0):
        print "STATIONARY"
    elif (index == 1):
        print "UP"
    elif (index == 2):
        print "DOWN"
    elif (index == 3):
        print "LEFT"
    elif (index == 4):
        print "RIGHT"


def runObjectDetect(buffer_size):
    pts = deque(maxlen=args["buffer"])  # Set the buffer size

    # if a video path was not supplied, grab the reference to the webcam
    if not args.get("video", False):
        camera = cv2.VideoCapture(0)
    else:
        camera = cv2.VideoCapture(args["video"])


    while True:
        grabbed, frame = camera.read()  # Get frames

        # Determine when video file ends
        if args.get("video") and not grabbed:
            break

        frame = imutils.resize(frame, width = 600)   # resize frame to speed up FPS
        blur = cv2.GaussianBlur(frame, (11, 11), 0)  # blur the frame to reduce noise
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)  # convert to HSV color space

        mask = cv2.inRange(hsv, lower, upper)          # Create mask for object
        mask = cv2.erode(mask, None, iterations = 1)   # Erode the image to reduce noise
        mask = cv2.dilate(mask, None, iterations = 2)  # dilate the image to improve detection

        # Find contours of the mask and initilize the current (x, y) center
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        # only proceed if at least one contour is found
        if len(cnts) > 0:
            c = max(cnts, key = cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))  # Calculate centroid

            # only proceed if radius is big enough
            if radius > 5:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)


                pts.appendleft(center)  # update points queue
                detectTrend(pts)        # Determine motion of object


        # Use the points in the queue to draw the line from the centroid
        for i in xrange(1, len(pts)):
            if pts[i - 1] is None or pts[i] is None:
                continue
            thickness = 1
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

        cv2.imshow("frame", cv2.flip(frame, 1))  # show actual camera feed
        cv2.imshow("mask", cv2.flip(mask, 1))    # show the blob detection feed

        # Press "q" tp exit program
        key = cv2.waitKey(1)
        if key == ord("q"):
            break


if __name__ == '__main__':
    # contruct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
    args = vars(ap.parse_args())
    runObjectDetect(args)
