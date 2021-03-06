# import the necessary packages
import os
import cv2
import requests
from webConfig import *

class pictureSaverAndSender:

    def __init__(self):
        self.base ="picController/img/"
        self.ext = ".jpg"
        return

    def createPicture(self, fileName, frame, eventNumber):
        # construct the file path

        if eventNumber == None:
            self.path = "{path}{fileName}{ext}".format(path=self.base,fileName=fileName,ext=self.ext)
            print (self.path)
            cv2.imwrite(self.path, frame)
        else:
            self.directory = self.base + str(eventNumber)
            self.eventNumber = eventNumber
            self.fileName=fileName
            if not os.path.exists( self.directory):
                os.makedirs(self.directory)
            self.path = "{path}/{fileName}{ext}".format(path=os.path.join(self.base, str(eventNumber)), fileName=fileName,ext=self.ext)
            cv2.imwrite(self.path,frame)
        return

    def sendPicture(self,id):
        events = os.listdir(self.directory)

        print (events)
        if len(events) is 1:
            json = {}
            img_file = {'file': open(self.path, "rb")}
            json['alertId'] = self.eventNumber
            json['cameraId'] = id
            json['time'] = int(self.fileName)
            json['date'] = os.path.getctime(self.path)
            send =serverIp+'/api/cameras/cameraAlert/'
            res = requests.post( send + str(id),
                                data=json, files=img_file)

            if res.status_code is 200:
                # os.remove(self.path)
                print ('200')

        else:
            json = {}
            img_file = {
                'file': open(self.path, "rb")}
            json['alertId'] = self.eventNumber
            json['cameraId'] = id
            json['time'] = int(self.fileName)
            json['date'] = os.path.getctime(self.path)
            print json
            send = serverIp+'/api/cameras/cameraAlertPhoto/'
            res = requests.post(send + str(self.eventNumber),
                            data=json, files=img_file)

            if res.status_code is 200:
                # os.remove(self.path)
                print ('200')
