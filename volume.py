import cv2
import mediapipe as mp
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np

vid=cv2.VideoCapture(0)
mpHand=mp.solutions.hands
hand=mpHand.Hands() 
draw=mp.solutions.drawing_utils  


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

range=volume.GetVolumeRange()

minVal=range[0]
maxVal=range[1]

# volume.SetMasterVolumeLevel(0.0, None)
wCam,hCam=700,500

vid.set(3,wCam)
vid.set(4,hCam)

while True:
    ret,frame=vid.read()
    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    res=hand.process(rgb)
    if res.multi_hand_landmarks:   
        for handLMS in res.multi_hand_landmarks: 
            h,w,c=frame.shape   
            x1 = int(handLMS.landmark[8].x * w) 
            y1 = int(handLMS.landmark[8].y * h)  
            x2 = int(handLMS.landmark[4].x * w) 
            y2 = int(handLMS.landmark[4].y * h) 
            cx,cy=(x1+x2)//2,(y1+y2)//2
            cv2.circle(frame,(x1,y1),5,(255,0,255),5,cv2.FILLED)
            cv2.circle(frame,(x2,y2),5,(255,0,255),5,cv2.FILLED)
            cv2.circle(frame,(cx,cy),5,(255,0,255),5,cv2.FILLED)
            length=math.hypot(x2-x1,y2-y1)
            vol=np.interp(length,[13,115],[minVal,maxVal])
            volume.SetMasterVolumeLevel(vol, None)
            cv2.line(frame,(x1,y1),(x2,y2),(255,0,255),3)
            draw.draw_landmarks(frame,handLMS,mpHand.HAND_CONNECTIONS)     
    cv2.imshow("Frame",frame)
    if cv2.waitKey(1)==ord('q'):
        break

vid.release()
cv2.destroyAllWindows()