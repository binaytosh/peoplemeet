from sqlalchemy.orm import Session
from . import models, schemas, auth_utils
from datetime import datetime

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth_utils.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        city=user.city,
        area=user.area,
        intent=user.intent,
        requirement=user.requirement,
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Add hobbies
    if user.hobbies:
        for hobby_name in user.hobbies:
            hobby_name_lower = hobby_name.lower().strip()
            hobby = db.query(models.Hobby).filter(models.Hobby.name == hobby_name_lower).first()
            if not hobby:
                hobby = models.Hobby(name=hobby_name_lower)
                db.add(hobby)
                db.commit()
            db_user.hobbies.append(hobby)
        db.commit()
        
    return db_user

def update_user(db: Session, user: models.User, updates: schemas.UserUpdate):
    for key, value in updates.dict(exclude_unset=True).items():
        if key == 'hobbies':
            # Handle hobbies update separately
            user.hobbies = [] # Clear existing or smart update? Let's clear and re-add for simplicity
            for hobby_name in value:
                hobby_name_lower = hobby_name.lower().strip()
                hobby = db.query(models.Hobby).filter(models.Hobby.name == hobby_name_lower).first()
                if not hobby:
                    hobby = models.Hobby(name=hobby_name_lower)
                    db.add(hobby)
                user.hobbies.append(hobby)
        else:
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

# Matching Logic
def get_matches(db: Session, current_user: models.User, limit: int = 50):
    # Retrieve all other users
    # In a real large-scale app, we would filtering by city in SQL first.
    candidates = db.query(models.User).filter(models.User.id != current_user.id).all()
    
    scored_candidates = []
    
    current_hobbies = set(h.name for h in current_user.hobbies)
    
    for candidate in candidates:
        score = 0
        if candidate.city == current_user.city:
            score += 40
        if candidate.area == current_user.area:
            score += 20
        
        candidate_hobbies = set(h.name for h in candidate.hobbies)
        if current_hobbies & candidate_hobbies:
            score += 20
            
        # Using simple string match for requirement/intent for MVP
        if candidate.intent == current_user.intent:
            score += 10
        if candidate.requirement == current_user.requirement:
            score += 10
            
        scored_candidates.append({
            "user": candidate,
            "score": score
        })
    
    # Sort by score descending
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    return scored_candidates[:limit]

# Connections
def create_connection_request(db: Session, sender_id: int, receiver_id: int):
    # Check if exists
    existing = db.query(models.Connection).filter(
        ((models.Connection.sender_id == sender_id) & (models.Connection.receiver_id == receiver_id)) |
        ((models.Connection.sender_id == receiver_id) & (models.Connection.receiver_id == sender_id))
    ).first()
    
    if existing:
        return existing # Already exists
        
    db_conn = models.Connection(sender_id=sender_id, receiver_id=receiver_id, status=models.ConnectionStatus.pending)
    db.add(db_conn)
    db.commit()
    db.refresh(db_conn)
    return db_conn

def get_connections(db: Session, user_id: int):
    return db.query(models.Connection).filter(
        ((models.Connection.sender_id == user_id) | (models.Connection.receiver_id == user_id)) &
        (models.Connection.status == models.ConnectionStatus.accepted)
    ).all()

def get_pending_requests(db: Session, user_id: int):
    return db.query(models.Connection).filter(
        models.Connection.receiver_id == user_id,
        models.Connection.status == models.ConnectionStatus.pending
    ).all()

def update_connection_status(db: Session, connection_id: int, status: str):
    conn = db.query(models.Connection).filter(models.Connection.id == connection_id).first()
    if conn:
        conn.status = status
        db.commit()
        db.refresh(conn)
    return conn

# Chat
def create_message(db: Session, sender_id: int, receiver_id: int, content: str):
    msg = models.Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_chat_history(db: Session, user_id: int, other_id: int):
    return db.query(models.Message).filter(
        ((models.Message.sender_id == user_id) & (models.Message.receiver_id == other_id)) |
        ((models.Message.sender_id == other_id) & (models.Message.receiver_id == user_id))
    ).order_by(models.Message.timestamp.asc()).all()
