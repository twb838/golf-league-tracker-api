from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.routers import players, teams, scores, courses, leagues, matches
from app.database import engine
from app.models.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",  # Allow requests from React app's origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
def root():
    return {"message": "Hello World"}

# Include routers
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(scores.router)
app.include_router(courses.router)
app.include_router(leagues.router)
app.include_router(matches.router)





