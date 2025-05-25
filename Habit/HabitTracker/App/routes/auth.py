from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from core.config import SECRET_KEY, ALGORITHM
from core.config import client
from core.security import get_password_hash
from models.user import User

router = APIRouter()
data=client.server
users=data.user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user["username"]

@router.get("/users/me/")
async def read_users_me(current_user:str = Depends(get_current_user)):
    return current_user

@router.post("/register")
async def register_user(username: str = Form(...), password: str = Form(...)):
    userData=User(username=username,password=password)
    if not userData.username or not userData.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    user = users.find_one({"username": userData.username})
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    new_user = {"username": username, "hashed_password": hashed_password}
    users.insert_one(new_user)
    return {"message": "User created successfully"}