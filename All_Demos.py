from collections import deque
import numpy as np
import argparse
import imutils
import cv2

class VisionDemos:
    # define the lower and upper boundries of the "green"
    # ball and then initialize a space of tracked points
    lower = (29, 86, 6)
    upper = (64, 255, 255)
    pts = deque()
    erode_iter = 1
    dilate_iter = 5
    max_radius = 10

    def __init__(self, args):
        self.pts = deque(maxlen=args["buffer"])

    def stationary(self, pt1, pt2):
        if pt2[1] - pt1[1] < 5:
            return True
        else:
            return False

    def detectTrend(self, pts):
        # stationary, up, down, left, right
        movements = [0, 0, 0, 0, 0]
        for i in xrange(1, len(self.pts)):
            print "[X2: %d, X1: %d] [Y2: %d, Y1: %d]" % (self.pts[i][0], self.pts[i - 1][0], self.pts[i][1], self.pts[i - 1][1])

            if self.pts[i][0] < self.pts[i - 1][0]:
                movements[3] += 1
            elif self.pts[i][0] > self.pts[i - 1][0]:
                movements[4] += 1

            if self.pts[i][1] > self.pts[i - 1][1]:
                movements[1] += 1
            elif self.pts[i][1] < self.pts[i - 1][1]:
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


    def maskFilterEdit(self):
        key = cv2.waitKey(1)

        if key == ord("e"):
            self.erode_iter += 1
            print "Erode Iterations: %d" % (self.erode_iter)
        elif key == ord("d"):
            self.erode_iter -= 1
            print "Erode Iterations: %d" % (self.erode_iter)
        elif key == ord("w"):
            self.dilate_iter += 1
            print "Dilate Iterations: %d" % (self.dilate_iter)
        elif key == ord("s"):
            self.dilate_iter -= 1
            print "Dilate Iterations: %d" % (self.dilate_iter)
        elif key == ord("r"):
            self.max_radius += 1
            print "Max Radius: %d" % (self.max_radius)
        elif key == ord("f"):
            self.max_radius -= 1
            print "Max Radius: %d" % (self.max_radius)

    def runObjectDetect(self):
        # if a video path was not supplied, grab the reference to the webcam
        if not args.get("video", False):
            camera = cv2.VideoCapture(0)
        else:
            camera = cv2.VideoCapture(args["video"])


        while True:
            # Get frames
            grabbed, frame = camera.read()

            # Determine when video file ends
            if args.get("video") and not grabbed:
                break

            frame = imutils.resize(frame, width = 600)  # resize frame to speed up FPS
            blur = cv2.GaussianBlur(frame, (11, 11), 0)  # blur the frame to reduce noise
            hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)  # convert to HSV color space

            mask = cv2.inRange(hsv, self.lower, self.upper) # Create mask for object
            mask = cv2.erode(mask, None, iterations = 1)
            mask = cv2.dilate(mask, None, iterations = 2)

            # Find contours of the mask and initilize the current (x, y) center
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

            # only proceed if at least one contour is found
            if len(cnts) > 0:
                c = max(cnts, key = cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # only proceed if radius is big enough
                if radius > 5:
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)

                    # update points queue
                    self.pts.appendleft(center)
                    self.detectTrend(self.pts)


            for i in xrange(1, len(self.pts)):
                if self.pts[i - 1] is None or self.pts[i] is None:
                    continue

                thickness = 1
                cv2.line(frame, self.pts[i - 1], self.pts[i], (0, 0, 255), thickness)

            cv2.imshow("frame", cv2.flip(frame, 1))
            cv2.imshow("mask", cv2.flip(mask, 1))

    def runPolyDetect(self):
        # if a video path was not supplied, grab the reference to the webcam
        if not args.get("video", False):
            camera = cv2.VideoCapture(0)
        else:
            camera = cv2.VideoCapture(args["video"])

        while True:
            grabbed, frame = camera.read()

            if args.get("video") and not grabbed:
                break

            frame = imutils.resize(frame, width = 600)
            # blur = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            mask = cv2.inRange(hsv, self.lower, self.upper)
            mask = cv2.erode(mask, None, iterations = self.erode_iter)
            mask = cv2.dilate(mask, None, iterations = self.dilate_iter)

            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

            centers = []

            if len(cnts) == 0:
                # print "No Objects Found!"
                continue
            elif len(cnts) == 1:
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

                    if radius > self.max_radius:
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

            self.maskFilterEdit()

            key = cv2.waitKey(1)
            if key == ord("q"):
                break





if __name__ == '__main__':
    # contruct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to (optional) video file")
    ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
    args = vars(ap.parse_args())

    vd = VisionDemos(args)
    # vd.runObjectDetect()
    vd.runPolyDetect()
