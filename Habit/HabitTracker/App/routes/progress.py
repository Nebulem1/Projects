from models.habit import Progress,UpdateProgress
from core.config import client
from datetime import datetime
from fastapi import APIRouter
data = client.server
progressHabit=data.progress

router =APIRouter()
@router.post("/progress")
async def add_progress(progress: Progress):
    progress.last_completed_date=datetime.combine(progress.last_completed_date,datetime.min.time())
    progressHabit.insert_one(progress.dict())
    return {"message": "Progress added successfully"}

@router.put("/update_habit")
def updateHabit(progress:UpdateProgress):
    progress.date=datetime.combine(progress.date,datetime.min.time())
    progressHabit.update_one({"habit_id":progress.habit_id ,"user":progress.user} ,  {"$set":{ "date":progress.date,"amount_done":progress.amount_done,"status":progress.status} })
    return {"Data Inserted Successfully"}