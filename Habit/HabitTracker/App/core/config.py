import os
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()
url= os.getenv("url")
client = MongoClient(url)
SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM= os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES= int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))