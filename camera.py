
# import the necessary packages
from pyimagesearch.tempimage import TempImage
# import argparse
import warnings
import datetime
import json
import time
import cv2
import numpy as np
import uuid



class camera:
    def __init__(self,cameraId):
        self.cameraId = cameraId
        self.name = "camear-1"
        self.cameraInitialise()
        self.TempImage = TempImage()
        return

    def cameraInitialise(self):
        camera = cv2.VideoCapture(0)
        time.sleep(1.5)
        status,frame = camera.read()
        if(status):
            cv2.imwrite("img/frame-1.jpg", frame)
            self.status = 10
            return 10
        else:
            self.status = 11
            return 11


    def analysis(self):
        rule= json.load(open('theRule.json'))
        self.myPolygon = np.array(rule["polygon"])
        self.inOut = rule['inOut']
        conf = json.load(open('conf.json'))
        # rule= json.load(open('theRule.json'))
        # myArray = np.array(rule["polygon"])

        camera = cv2.VideoCapture(0)
        time.sleep(2)
        # allow the camera to warmup, then initialize the average frame, last
        # uploaded timestamp, and frame motion counter
        print "[INFO] warming up..."

        alertNumber = 0
        avg = None
        maske = None
        # inOut = rule['inOut']
        lastUploaded = datetime.datetime.now()
        motionCounter = 0
        eventNumber = uuid.uuid4().int & (1<<32)-1


        # capture frames from the camera
        # for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        while True:
            ret, frame = camera.read()
            # grab the raw NumPy array representing the image and initialize
            # the timestamp and occupied/unoccupied text
            # frame = f.array
            timestamp = datetime.datetime.now()
            text = "Unoccupied"

            # resize the frame, convert it to grayscale, and blur it
            # frame = imutils.resize(frame, conf["width"])
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the average frame is None, initialize it
            if avg is None:
                print "[INFO] starting background model..."
                print timestamp
                avg = gray.copy().astype("float")
                mask = np.zeros((gray.shape[0], gray.shape[1]), dtype=np.uint8)
                cv2.fillConvexPoly(mask,self.myPolygon, 1)
                mask = mask.astype(np.bool)

            out = np.zeros_like(gray)
            if self.inOut is 1:
                # "looking out of the erea."
                screan = gray
                screan[mask] = out[mask]

            if self.inOut is 0:
                # print "looking in the erea."
                screan = np.zeros_like(gray)
                out[mask] = gray[mask]
                screan[mask] = out[mask]
            else:
                screan = gray

            # accumulate the weighted average between the current frame and
            # previous frames, then compute the difference between the current
            # frame and running average
            cv2.accumulateWeighted(screan, avg, 0.5)
            frameDelta = cv2.absdiff(screan, cv2.convertScaleAbs(avg))

            # threshold the delta image, dilate the thresholded image to fill
            # in holes, then find contours on thresholded image
            thresh = cv2.threshold(frameDelta,  conf["delta_thresh"], 255,
                                   cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            im2, cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)

            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < conf["min_area"]:

                    continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"

            # draw the text and timestamp on the frame
            ts = timestamp.strftime("%d-%B-%Y--%I:%M:%S%p")
            cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)

            # check to see if the room is occupied
            if text == "Occupied":
                # check to see if enough time has passed between uploads

                if (timestamp - lastUploaded).seconds >=  conf["min_upload_seconds"]:

                    # increment the motion counter
                    motionCounter += 1
                    # check to see if the number of frames with consistent motion is
                    # high enough
                    if motionCounter >=  conf["min_motion_frames"]:
                        # print eventNumber, ( timestamp-lastUploaded).seconds
                        fileName = time.time()
                        self.TempImage.createPicture(fileName, frame,eventNumber)
                        self.TempImage.sendPicture(self.cameraId)
                        alertNumber+=1
                        # upload the image to Dropbox and cleanup the tempory image
                        print "[UPLOAD] {}".format(ts)

                        if (timestamp-lastUploaded).seconds >conf["min_time_events"]:
                            eventNumber = uuid.uuid4().int & (1<<32)-1

                        # write the image to temporary file
                        # update the last uploaded timestamp and reset the motion
                        # counter

                        lastUploaded = timestamp
                        motionCounter = 0



            # otherwise, the room is not occupied
            else:
                motionCounter = 0

            # check to see if the frames should be displayed to screen
            if conf["show_video"]:
                # display the security feed
                cv2.imshow("Security Feed", frame)
                cv2.imshow("Frame Delta", frameDelta)
                cv2.imshow('Thresh', thresh)
                cv2.imshow('screan', screan)

                key = cv2.waitKey(1) & 0xFF

                # if the `q` key is pressed, break from the lop
                if key == ord("q"):
                    break

                # clear the stream in preparation for the next frame
                # rawCapture.truncate(0)
        camera.release()
        cv2.destroyAllWindows()

    def updateRule(self,polygon):
        self.myPolygon = polygon
