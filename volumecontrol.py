import cv2
import time
import numpy as np
import mediapipe as mp
import handtrackmodule as htm  
import math
from ctypes import cast,POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities,IAudioEndpointVolume

wCam,hCam=640,480

cap=cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime=0

detector = htm.handDetector()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_,CLSCTX_ALL,None
)
volume = cast(interface,POINTER(IAudioEndpointVolume))

volrange=volume.GetVolumeRange()
minvol=volrange[0]
maxvol=volrange[1]
vol=0
volbar=400
volper=0

while True:
    success,img = cap.read()
    img = detector.findHands(img)
    lmlist = detector.findPosition(img,draw=False)
    if lmlist:
        #print(lmlist[4],lmlist[8])

        x1,y1=lmlist[4][1],lmlist[4][2]
        x2,y2=lmlist[8][1],lmlist[8][2]
        cx,cy = (x1+x2)//2,(y1+y2)//2

        cv2.circle(img,(x1,y1),10,(255,0,255),cv2.FILLED)
        cv2.circle(img,(x2,y2),10,(255,0,255),cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(225,0,255),2)
        cv2.circle(img,(cx,cy),10,(225,0,255),cv2.FILLED)

        lenght = math.hypot(x2-x1,y2-y1)
        #print(lenght)

        vol = np.interp(lenght,[20,230],[minvol,maxvol])
        volbar = np.interp(lenght,[30,400],[400,150])
        volper = np.interp(lenght,[30,400],[0,100])

        print(int(lenght),vol)
        volume.SetMasterVolumeLevel(vol,None)

        if lenght<30:
            cv2.circle(img,(cx,cy),10,(0,255,0),cv2.FILLED)

    cv2.rectangle(img,(50,150),(85,400),(0,255,0),2)
    cv2.rectangle(img,(50,int(volbar)),(85,400),(0,255,0),cv2.FILLED)
    cv2.putText(img,f' {int(volper)} %', (40,450),cv2.FONT_HERSHEY_COMPLEX,
                1,(255,0,0),2)

    cTime=time.time()
    fps=1/(cTime - pTime)
    pTime=cTime

    cv2.putText(img,f'FPS: {int(fps)}', (40,50),cv2.FONT_HERSHEY_COMPLEX,
                1,(255,0,255),2)

    cv2.imshow('img',img)
    if cv2.waitKey(30)==27:
        break