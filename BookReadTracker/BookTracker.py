from fastapi import FastAPI, Form,HTTPException, Depends, status
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

url=os.getenv("url")
client = MongoClient(url)
database = client.server
user = database.user
bookCollection = database.book

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

class Token(BaseModel):
    access_token: str
    token_type: str

class BookDetails(BaseModel):
  title: str
  author: str
  totalPage: int
  currentPage: int
  status: str
  username: str

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

@app.post("/book")
def bookInfo(book:BookDetails):
    books = {
        "title": book.title,
        "author": book.author,
        "totalPage": book.totalPage,
        "currentPage": book.currentPage,
        "status": book.status,
        "username": book.username
    }
    insetedData=bookCollection.insert_one(books)
    result=bookCollection.find_one({"_id":ObjectId(insetedData.inserted_id)})
    result['_id']=str(result["_id"])
    return result

def decode(ob):
    ob['_id']=str(ob['_id'])
    return ob

@app.get("/books/{username}")
def getBooks(username:str):
    book_list = [decode(b) for b in bookCollection.find({"username": username})]
    return book_list

@app.put("/updateBook/{book_id}")
async def updateBook(book_id: str, field: str, value:int):
    result = bookCollection.update_one({"_id": ObjectId(book_id)}, {"$set": {field: value}})
    return {"msg":"Updated"}

@app.put("/updateStatus/{book_id}")
async def updateBook2(book_id: str, field: str, value: str):
    result = bookCollection.update_one({"_id": ObjectId(book_id)}, {"$set": {field: value}})
    return {"msg":"Updated Successfully"}

@app.delete("/book/{book_id}")
def deleteBook(book_id: str):
    result = bookCollection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return {"message": "Book deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Book not found")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=3000)