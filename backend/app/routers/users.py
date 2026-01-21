from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, crud, auth_utils, database

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.put("/profile", response_model=schemas.User)
def update_profile(
    updates: schemas.UserUpdate,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    return crud.update_user(db, current_user, updates)

@router.get("/discover", response_model=List[dict])
def discover_people(
    limit: int = 50,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Returns a list of users with a match score.
    Response format: [{"user": UserObj, "score": int}, ...]
    Note: We need a custom response model if we want to validate this strictly, 
    but for now returning list of dicts is flexible for the 'score' field.
    """
    matches = crud.get_matches(db, current_user, limit)
    # Pydantic doesn't serialize the SQLAlchemy model inside the dict automatically if we just return the raw dict
    # So we manually format carefully or rely on FastAPI's magical serialization if we had a Scheme.
    # Let's simple format it manually to be safe and clean or use a Pydantic model wrapper.
    # For MVP, let's just return the list and let FastAPI try to encode it.
    # Actually, SQLAlchemy objects in a dict might fail JSON serialization if not converted.
    
    results = []
    for match in matches:
        user_obj = match['user']
        # Convert user_obj to dict using Pydantic's from_orm logic (manually)
        user_data = schemas.User.from_orm(user_obj).dict()
        results.append({
            "user": user_data,
            "score": match['score']
        })
    return results

@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
