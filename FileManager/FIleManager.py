from fastapi import FastAPI, Form, File, UploadFile,HTTPException, Depends, status
import uvicorn
import shutil
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
import os
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math

uri = "mongodb://localhost:27017/"
client = MongoClient(uri)
database = client.server
files = database.file
user = database.user

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Token(BaseModel):
    access_token: str
    token_type: str

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password) 

def get_password_hash(password):
    return pwd_context.hash(password) 


def authenticate_user(username: str, password: str):
    users=user.find_one({"username":username}, {"_id": 0})
    if not users:
        return False
    if not verify_password(password, users["hashed_password"]):
        return False
    return users


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta  
    else:
        expire = datetime.now() + timedelta(minutes=15) 
    to_encode.update({"exp": expire})     
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 
    return encoded_jwt 

@app.post("/token", response_model=Token)
async def login_for_access_token(username:str=Form(...), password:str=Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

    except JWTError:
        raise credential_exception
    
    users = user.find_one({"username":username})
    if users is None:
        raise credential_exception
    return users["username"]

@app.get("/users/me/")
async def read_users_me(current_user:str = Depends(get_current_user)):
    return current_user

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    if user.find_one({"username":username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(password)
    user.insert_one({"username": username, "hashed_password": hashed_password})
    return {"message": "User created successfully"}

@app.post("/uploadfile")
def uploadFile(file: UploadFile = File(...), title: str = Form(...), category: str = Form(...),owner:str=Form(...)): 
    if file.filename == "":
        raise HTTPException(status_code=400, detail="No file selected")
    os.makedirs("upload", exist_ok=True)
    file_path = os.path.join("upload", file.filename)
    with open(file_path, "wb") as f:      
      shutil.copyfileobj(file.file, f)
    insetedData=files.insert_one({"filename":file.filename,"path":"upload", "title": title, "category": category,"owner":owner})
    result=files.find_one({"_id":ObjectId(insetedData.inserted_id)})
    result['_id']=str(result["_id"])
    return result

@app.get("/files")
def getFiles():
    l=[]
    for i in files.find():
        i["_id"]=str(i["_id"])
        l.append(i)
    return l

def handControl():
    vid=cv2.VideoCapture(0)
    mpHand=mp.solutions.hands
    hand=mpHand.Hands(max_num_hands=1,min_detection_confidence=0.75) 
    draw=mp.solutions.drawing_utils  
    smooth=5
    px=0
    py=0
    wCam,hCam=720,550
    vid.set(3,wCam)
    vid.set(4,hCam)
    minH=0
    minW=0
    maxW, maxH = pyautogui.size()
    Frame=100
    while True:
        ret,frame=vid.read()
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        res=hand.process(rgb)

        tipid=[4,8,12,16,20]
        if res.multi_hand_landmarks:   
            for handLMS in res.multi_hand_landmarks: 
                h,w,c=frame.shape   
                x1 = int(handLMS.landmark[8].x * w) 
                y1 = int(handLMS.landmark[8].y * h)  
                x2 = int(handLMS.landmark[12].x * w) 
                y2 = int(handLMS.landmark[12].y * h)  

                #This function helps to find which Finger tip is up by calculating diff in height
                handtip=[]
                for i in range(0,5):
                    if handLMS.landmark[tipid[i]].y*h<handLMS.landmark[tipid[i]-2].y*h:
                        handtip.append(1)
                    else:
                        handtip.append(0)
                length=math.hypot(x2-x1,y2-y1)
                if handtip[1] ==1 and handtip[2]==0:
                    xx1=np.interp(x1,[0,w-Frame],[minW,maxW])
                    yy1=np.interp(y1,[0,h-Frame],[minH,maxH])
                    crx=px+(xx1-px)/smooth
                    cry=py+(yy1-py)/smooth
                    pyautogui.moveTo(maxW-crx,cry)
                    cv2.circle(frame,(x1,y1),5,(255,0,255),5)
                    px,py=crx,cry
                if handtip[1]==1 and handtip[2]==1:
                    if length <=25:
                        cv2.line(frame,(x1,y1),(x2,y2),(255,0,255),3)
                        pyautogui.click()
                draw.draw_landmarks(frame,handLMS,mpHand.HAND_CONNECTIONS)     
        cv2.imshow("Frame",frame)
        if cv2.waitKey(1)==ord('q'):
            break
    vid.release()
    cv2.destroyAllWindows()

@app.post("/hand")
def activeHand():
    handControl()
    return {'handMotion':"activated"}

@app.delete("/deletefile/{id}")
def deleteFile(id:str):
    files.delete_one({"_id":ObjectId(id)})
    return {"message":"File deleted successfully"}

@app.get("/download/{id}")
def downloadFile(id:str):
    data=files.find_one({"_id":ObjectId(id)})
    filename=data["filename"]
    file_path = os.path.join("upload", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='application/octet-stream',filename=filename) # here we have to give exact path of file 
                        #which we want to send to client and 2nd parameter is media type ocete-stream tells the browser This is just a generic binary file. I don’t know what it is exactly — treat it as raw bytes.
                        # or its just a file, it can be anything dont try to read it just download it. 
                        # filename is the name of file which we want to give to client when he download the file. as not all browsers support hyperlink download.
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=3000)
