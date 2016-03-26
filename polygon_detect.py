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

pts = deque(maxlen=5)

def maskFilterEdit():
    key = cv2.waitKey(1)

    if key == ord("e"):
        erode_iter += 1
        print "Erode Iterations: %d" % (erode_iter)
    elif key == ord("d"):
        erode_iter -= 1
        print "Erode Iterations: %d" % (erode_iter)
    elif key == ord("w"):
        dilate_iter += 1
        print "Dilate Iterations: %d" % (dilate_iter)
    elif key == ord("s"):
        dilate_iter -= 1
        print "Dilate Iterations: %d" % (dilate_iter)
    elif key == ord("r"):
        max_radius += 1
        print "Max Radius: %d" % (max_radius)
    elif key == ord("f"):
        max_radius -= 1
        print "Max Radius: %d" % (max_radius)


def runPolyDetect(buffer_size):

    camera = cv2.VideoCapture(0)

    while True:
        grabbed, frame = camera.read()

        frame = imutils.resize(frame, width = 600)
        blur = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations = erode_iter)
        mask = cv2.dilate(mask, None, iterations = dilate_iter)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        centers = []


        if len(cnts) == 1:
            # print "One Object Found!"
            # c = max(cnts, key = cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(cnts[0])
            M = cv2.moments(cnts[0])
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

        else:
            # print "%d Objects Found!" % (len(cnts))
            for i in range(0, len(cnts)):
                ((x, y), radius) = cv2.minEnclosingCircle(cnts[i])
                M = cv2.moments(cnts[i])
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                if radius > max_radius:
                    centers.append(center)
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)

            for x in range(1, len(centers)):
                thickness = 1
                cv2.line(frame, centers[x], centers[x - 1], (0, 0, 255), thickness, lineType = cv2.CV_AA)
                if x == len(centers) - 1:
                    cv2.line(frame, centers[x], centers[0], (0, 0, 255), thickness, lineType = cv2.CV_AA)



        cv2.imshow("frame", cv2.flip(frame, 1))
        cv2.imshow("mask", cv2.flip(mask, 1))

        maskFilterEdit()  

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

if __name__ == '__main__':
    # contruct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
    args = vars(ap.parse_args())

    runPolyDetect(args)
