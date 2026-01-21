from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Table, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

# Association Table for User <-> Hobby
user_hobbies = Table(
    "user_hobbies",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("hobby_id", Integer, ForeignKey("hobbies.id"), primary_key=True),
)

class IntentEnum(str, enum.Enum):
    networking = "Networking"
    friendship = "Friendship"
    professional = "Professional"
    casual = "Casual"
    learning = "Learning"

class ConnectionStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    blocked = "blocked"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    city = Column(String, index=True)
    area = Column(String, index=True)
    bio = Column(Text, nullable=True)
    intent = Column(String, default=IntentEnum.friendship) # Store as string for simplicity with SQLite
    requirement = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    hobbies = relationship("Hobby", secondary=user_hobbies, back_populates="users")
    
    # Connection relationships
    sent_requests = relationship("Connection", foreign_keys="Connection.sender_id", back_populates="sender")
    received_requests = relationship("Connection", foreign_keys="Connection.receiver_id", back_populates="receiver")

class Hobby(Base):
    __tablename__ = "hobbies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    users = relationship("User", secondary=user_hobbies, back_populates="hobbies")

class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default=ConnectionStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_requests")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
