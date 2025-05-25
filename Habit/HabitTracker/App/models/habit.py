from pydantic import BaseModel
from datetime import date 
class Habit(BaseModel):
    name: str
    category: str
    frequency: str
    target_per_day: int
    start_date: date  
    user: str

class Progress(BaseModel):
    habit_id: str
    last_completed_date: date   
    amount_done: int
    status: str
    streak:int
    longest_streak:int 
    user: str

class Log(BaseModel):
    habit_id:str 
    user:str
    date:date 
    
class UpdateProgress(BaseModel):
    habit_id:str
    date:date
    status:str  
    amount_done:int
    user:str 