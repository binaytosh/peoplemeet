from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class IntentEnum(str, Enum):
    networking = "Networking"
    friendship = "Friendship"
    professional = "Professional"
    casual = "Casual"
    learning = "Learning"

# Hobby Schemas
class HobbyBase(BaseModel):
    name: str

class HobbyCreate(HobbyBase):
    pass

class Hobby(HobbyBase):
    id: int
    class Config:
        orm_mode = True

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    city: str
    area: str
    intent: IntentEnum
    requirement: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str
    hobbies: List[str] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    bio: Optional[str] = None
    intent: Optional[IntentEnum] = None
    requirement: Optional[str] = None
    hobbies: Optional[List[str]] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    hobbies: List[Hobby] = []

    class Config:
        orm_mode = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Connection Schema
class ConnectionCreate(BaseModel):
    receiver_id: int

class Connection(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime
    sender: Optional[User] = None
    receiver: Optional[User] = None

    class Config:
        orm_mode = True

# Message Schema
class MessageCreate(BaseModel):
    content: str
    receiver_id: int

class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True
