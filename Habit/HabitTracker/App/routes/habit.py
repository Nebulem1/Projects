from models.habit import Habit
from models.habit import Progress
from fastapi import APIRouter, HTTPException
from core.config import client
from bson import ObjectId
from datetime import datetime
data = client.server
habitData=data.habit
progressHabit=data.progress

router = APIRouter()

def idConvert(ob):
    ob["_id"] = str(ob["_id"])
    return ob

@router.get("/habits/{user}")
async def get_habits(user: str):
    status=progressHabit.find_one({"user":user})
    if status:
        today=datetime.now().date()
        completedDate=status['last_completed_date'].date()
        if today!=completedDate:
            progressHabit.update_one({"user":progress.user} ,  {"$set":{"amount_done":0,"status":'incomplete'}})
    habit=[idConvert(i) for i in habitData.find({"user": user})]
    progress=[idConvert(i) for i in progressHabit.find({"user": user})]
    return {"habit":habit,"progress":progress}

@router.post("/create_habit")
async def create_habit(habit: Habit):
    if habitData.find_one({"name": habit.name}):
        raise HTTPException(status_code=400, detail="Habit already exists")
    habit.start_date= datetime.combine(habit.start_date , datetime.min.time())
    insetedData=habitData.insert_one(habit.dict())
    if insetedData:
          result=habitData.find_one({"_id":ObjectId(insetedData.inserted_id)})
          result['_id']=str(result["_id"])
    else:
        raise HTTPException(status_code=400, detail="Habit creation failed")
    return result

@router.delete("/delete_habit/{habit_id}")
async def deleteHabit(habit_id: str):
    habitData.delete_one({"_id": ObjectId(habit_id)})
    progressHabit.delete_one({"habit_id":habit_id})
    return {"message": "Habit deleted successfully"}