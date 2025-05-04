from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math

url = "mongodb://localhost:27017/"
client = MongoClient(url)
database = client.server
blog = database.todo
blogContent=database.blog

class Token(BaseModel):
    token_access:str
    token_type:str

class User(BaseModel):
    username:str

class userDB(User):
    hashed_password:str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app=FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  #This is used to allow the request from this origin only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password) 

def get_password_hash(password):
    return pwd_context.hash(password)    

def authenticate_user(username: str, password: str):
    user = blog.find_one({"username":username},{'_id':0})
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

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

def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + timedelta(expires_delta)  
    else:
        expire = datetime.now() + timedelta(minutes=15) 
    to_encode.update({"exp": expire})     
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 
    return encoded_jwt 

class postData(BaseModel):
    username:str
    password:str

@app.post("/token",response_model=Token)
async def createToken(form:postData):
     user=authenticate_user(form.username,form.password)
     if not user:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
     token=create_access_token({"sub":user['username']},ACCESS_TOKEN_EXPIRE_MINUTES)
     return {"token_access": token, "token_type": "bearer"}

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
    
    user = blog.find_one({"username":username},{'_id':0})
    
    if user is None:
        raise credential_exception
    return User(**user)

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/hand")
def activeHand():
    handControl()
    return {'handMotion':"activated"}

class Update(BaseModel):
    pass
@app.delete("/delete/{id}")
def updateData(id:str):
    blogContent.delete_one({"_id":ObjectId(id)})
    return {"Deleted":"Successfully"}

@app.get("/getData")
def loadData():
    l=[]
    for i in blogContent.find():
        i['_id']=str(i["_id"])
        l.append(i)
    return l

class sData(BaseModel):
    title:str
    content:str
    username:str

@app.post("/setData")
def setData(data:sData):
    insetedData=blogContent.insert_one(dict(data))
    result=blogContent.find_one({"_id":ObjectId(insetedData.inserted_id)})
    result['_id']=str(result["_id"])
    return result

@app.post("/register")
def register(registerData:postData):
     if not registerData:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
     hash=get_password_hash(registerData.password)
     blog.insert_one({"username":registerData.username,"hashed_password":hash})
     return {"register":"successfull"}
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=3000)