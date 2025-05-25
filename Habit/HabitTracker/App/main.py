from fastapi import FastAPI
import uvicorn
import core.security as security
import routes.auth as auth
import routes.habit as habit
import routes.progress as progress
import routes.analysis as analysis
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(security.router)
app.include_router(auth.router)
app.include_router(habit.router)
app.include_router(progress.router)
app.include_router(analysis.router)

if __name__=="__main__":
    uvicorn.run(app,host="localhost",port=3000)