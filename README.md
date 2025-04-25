Task Manager Backend (FastAPI + MongoDB)

This is the backend API for a simple Task Manager application built using FastAPI and MongoDB.

Features

User registration and login with JWT-based authentication

Store and manage tasks per user

Task fields include: title, description, and status (Pending, Completed, In Progress)

API endpoints secured with token-based access

Task sorting and status filter logic handled at frontend


Tech Stack

Backend: FastAPI

Database: MongoDB (via PyMongo)

Auth: OAuth2, JWT

Password hashing: passlib (bcrypt)

CORS Enabled for frontend connection (http://localhost:5173)


Endpoints

POST /register — Register a new user

POST /token — Login and get access token

GET /users/me/ — Get user's task data (requires token)

POST /setTask — Save/update user's tasks


How to Run

1. Clone the repo


2. Make sure MongoDB is running locally


3. Run the server:

uvicorn main:app --reload



Note

Frontend is in progress / private. Only backend code is public in this repo.
