from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, users, connections, chat

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PeopleMeet API", version="1.0.0")

# CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "*", # Allow all for MVP simplicity (Mobile app access)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(connections.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to PeopleMeet API"}
