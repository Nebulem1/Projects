from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

uri = "mongodb://localhost:27017/"
client = MongoClient(uri)
database = client.todo
movies = database.todo

app=FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class postData(BaseModel):
    username:str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password) 

def get_password_hash(password):
    return pwd_context.hash(password) 

def authenticate_user(username: str, password: str):
    user=movies.find_one({username: {"$exists": True}}, {"_id": 0, username: 1})
    user=user[username]
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


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
async def login_for_access_token(form_data: postData ):
    user = authenticate_user(form_data.username, form_data.password)
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

    user = movies.find_one({username: {"$exists": True}}, {"_id": 0, username: 1})
    user=user[username]

    if user is None:
        raise credential_exception
    return User(Task=user['Task'])

class User(BaseModel):
     Task:list

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/register")
def login(userInfo:postData):
    if not userInfo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user=movies.find_one({},{"_id":0,userInfo.username:1})
    if user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    hashed=get_password_hash(userInfo.password)
    data={
        "username":userInfo.username,
        "hashed_password":hashed,
        "Task":[]
    }
    taskinfo={
        userInfo.username:data
    }
    movies.insert_one(taskinfo)
    return {"msg":"Data Entered"}

class TaskDetails(BaseModel):
    username:str
    Task:list
@app.post("/setTask")
def addTask(user:TaskDetails):
    username=user.username
    Task=user.Task
    user=movies.find_one({username: {"$exists": True}}, {"_id": 0, username: 1})
    user=user[username]
    movies.update_one(
    {username: {"$exists": True}},      
    {"$set": {f"{username}.Task": Task}}      
    )
    return {"msg":"Task Added"}
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=3000)