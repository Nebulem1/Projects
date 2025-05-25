from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException,Form
from datetime import datetime, timedelta
from jose import jwt
from core.config import client
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models.user import User

data=client.server
users=data.user
router = APIRouter()
class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return crypt_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return crypt_context.hash(password)

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token", response_model=Token)
def get_token(username:str=Form(...),password:str=Form(...)):
    userData=User(username=username,password=password)
    if not userData.username or not userData.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    user = users.find_one({"username": userData.username})
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(userData.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}