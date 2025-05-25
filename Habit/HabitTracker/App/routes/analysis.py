from fastapi import FastAPI,APIRouter,HTTPException
from datetime import timedelta, datetime,date 
from models.habit import Log
from core.config import client
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
# url = "mongodb://localhost:27017/"
# client = MongoClient(url)
db = client.server 
progress = db.progress
logData=db.log
habitData=db.habit

router=APIRouter()

# class Log(BaseModel):
#     habit_id:str 
#     user:str
#     date:date 

def analyse_month(data:Log):
    today=datetime.combine(data.date,datetime.min.time()) 
    endDate=today-timedelta(days=30)
    data.date=today
    logData.insert_one(data.dict())
    log=logData.find({"user":data.user,"habit_id":data.habit_id, "date":{"$gte":endDate,"$lte":today}})
    list=sorted([i["date"].date()  for i in log],reverse=True)
    status=progress.find_one({"user":data.user,"habit_id":data.habit_id})
    longest_streak=status['longest_streak'] if(status['longest_streak']!=0) else 1
    currStreak=status['streak']
    streak=0
    for indx,date in enumerate(list):
        expected_date= today-timedelta(days=indx)
        if date==expected_date:
            streak+=1
        else:
            streak=1
            break
    if streak==30:
        progress.update_one({"user":data.user,"habit_id":data.habit_id},{"$set":{"streak":currStreak+1,"longest_streak":longest_streak+1,"last_completed_date":today}})
        return {"current_streak":currStreak+1,"longest_streak":longest_streak+1}
    progress.update_one({"user":data.user,"habit_id":data.habit_id},{"$set":{"streak":1,"longest_streak":longest_streak,"last_completed_date":today}})
    return {"current_streak":1,"longest_streak":longest_streak}  

def analyse_week(data:Log):
    today=datetime.combine(data.date,datetime.min.time()) 
    endDate=today-timedelta(days=7)
    data.date=today
    logData.insert_one(data.dict())
    log=logData.find({"user":data.user,"habit_id":data.habit_id, "date":{"$gte":endDate,"$lte":today}})
    list=sorted([i["date"].date()  for i in log],reverse=True)
    status=progress.find_one({"user":data.user,"habit_id":data.habit_id})
    longest_streak=status['longest_streak'] if(status['longest_streak']!=0) else 1
    currStreak=status['streak']
    streak=0
    for indx,date in enumerate(list):
        expected_date= today-timedelta(days=indx)
        if date==expected_date:
            streak+=1
        else:
            streak=1
            break
    if streak==7:
        progress.update_one({"user":data.user,"habit_id":data.habit_id},{"$set":{"streak":currStreak+1,"longest_streak":longest_streak+1,"last_completed_date":today}})
        return {"current_streak":currStreak+1,"longest_streak":longest_streak+1}
    progress.update_one({"user":data.user,"habit_id":data.habit_id},{"$set":{"streak":1,"longest_streak":longest_streak,"last_completed_date":today}})
    return {"current_streak":1,"longest_streak":longest_streak}  
    

def analyse_daily(data:Log):
    today=data.date 
    dbDate=datetime.combine(today,datetime.min.time())
    yesterday=today-timedelta(days=1)
    status=progress.find_one({"user":data.user,"habit_id":data.habit_id})
    if status and status["last_completed_date"].date()==today and status['streak']>0:
        raise HTTPException(status_code=400)
    data.date=dbDate
    logData.insert_one(data.dict())
    lastCompletedTaskDate=status["last_completed_date"].date()
    if lastCompletedTaskDate==yesterday:
        streak=status["streak"]
        longest=max(status["longest_streak"],streak+1)
        progress.update_one({"user":data.user,"habit_id":data.habit_id},{"$set":{"streak":streak+1,"longest_streak":longest,"last_completed_date":dbDate}})
    else:
        progress.update_one({"user":data.user,"habit_id":data.habit_id},{"$set":{"streak":1,"last_completed_date":dbDate}})
    data=progress.find_one({"user":data.user,"habit_id":data.habit_id})
    longest=data["longest_streak"] if data["longest_streak"]!=0 else 1
    return {"current_streak":data["streak"],"longest_streak":longest}

@router.post("/analyse")
def analyse(data:Log):
    habit=habitData.find_one({"_id":ObjectId(data.habit_id),"user":data.user})
   
    if habit['frequency']=='daily':
        return analyse_daily(data)
    elif habit['frequency']=='weekly':
        return analyse_week(data)
    elif habit['frequency']=='monthly':
        return analyse_month(data)
    else:
        raise HTTPException(status_code=400)
