'''
This code has been modified from code written by Adrian Rosebrock
of pyimagesearch

The original can be found at:
http://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
'''

# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
# from collections import deque
from time import sleep
# from math import hypot
from math import atan
from math import pi
import numpy as np
import argparse
import imutils
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=10,
                help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
balls = 10
greenLower = (24, 40, 168)
greenUpper = (49, 229, 255)
# pts = [deque(maxlen=args["buffer"]),
#        deque(maxlen=args["buffer"]),
#        deque(maxlen=args["buffer"]),
#        deque(maxlen=args["buffer"]),
#        deque(maxlen=args["buffer"]),
#        deque(maxlen=args["buffer"]),
#        deque(maxlen=args["buffer"]),
#        deque(maxlen=args["buffer"])]

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])

# keep looping
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if args.get("video") and not grabbed:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    if args.get("video"):
        frame = imutils.rotate(frame, -90)
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:balls]
    centers = [None] * balls
    radii = [None] * balls

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        for i in xrange(0, min(balls, len(cnts))):
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            ((x, y), radii[i]) = cv2.minEnclosingCircle(cnts[i])
            M = cv2.moments(cnts[i])
            centers[i] = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radii[i] > 5:
                drawBGR = np.uint8([[[255 / (balls - 1) * i, 255, 255]]])
                BGRlist = cv2.cvtColor(drawBGR, cv2.COLOR_HSV2BGR)[0][0]
                (h, s, v) = (int(BGRlist[0]),
                             int(BGRlist[1]),
                             int(BGRlist[2]))
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radii[i]),
                           (0, 0, 255), 2)
                cv2.circle(frame, centers[i], 5, (h, s, v), -1)

    # # update the points queue
    # for i in xrange(0, balls):
    #     pts[i].appendleft(centers[i])

    # for i in xrange(0, balls):
    #     # loop over the set of tracked points
    #     for j in xrange(1, len(pts[i])):
    #         # if either of the tracked points are None, ignore
    #         # them
    #         if pts[i][j - 1] is None or pts[i][j] is None:
    #             continue

    #         # otherwise, compute the thickness of the line and
    #         # draw the connecting lines
    #         drawBGR = np.uint8([[[255 / (balls - 1) * i, 255, 255]]])
    #         BGRlist = cv2.cvtColor(drawBGR, cv2.COLOR_HSV2BGR)[0][0]
    #         (h, s, v) = (int(BGRlist[0]),
    #                      int(BGRlist[1]),
    #                      int(BGRlist[2]))

    #         thickness = int(np.sqrt(args["buffer"] / float(j + 1)) * 2.5)
    #         x1 = pts[i][j - 1][0]
    #         y1 = pts[i][j - 1][1]
    #         x2 = pts[i][j][0]
    #         y2 = pts[i][j][1]
    #         if hypot(x2 - x1, y2 - y1) < 100:
    #             cv2.line(frame, pts[i][j - 1], pts[i][j],
    #                      (h, s, v), thickness)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

    # print message
    if not(centers[0] is None or len(frame[0]) is None):
        deltay = float(frame.shape[0]) - float(centers[0][1])
        deltax = float(centers[0][0]) - float(frame.shape[1]) / 2
        angle = pi / 2 if deltax == 0 else atan(deltay / deltax)

        k = 1000.0  # Need to find empirically

        distance = 50.0 if radii[0] ** 2.0 == 0.0 else k / radii[0] ** 2.0

        centred = 1.27
        if (abs(angle) > centred or distance < 1):
            direction = "Forward"
        else:
            direction = "Turn"

        speed = "100%" if distance > 2 else "50%"

        if direction == "Forward":
            left, right = speed, speed
        elif angle > 0:
            right = "50%" if speed == "100%" else "25%"
            left = speed
        else:
            right = speed
            left = "50%" if speed == "100%" else "25%"

        message = string = (
            "{0}\n"
            "Location: ({2}, {3})\n"
            "Radius:    {4}\n"
            "{1}\n"
            "Angle:     {5}\n"
            "Distance:  {6}\n"
            "{1}\n"
            "Direction: {7}\n"
            "Speed:     {8}\n"
            "{1}\n"
            "Left:      {9}\n"
            "Right:     {10}\n"
            "{0}"
        ).format('=' * 40, '-' * 40,
                 centers[0][0], centers[0][1],
                 radii[0],

                 angle,
                 distance,

                 direction,
                 speed,

                 left,
                 right)

        print message

    # sleep(0.5)

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
