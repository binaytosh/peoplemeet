from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, crud, auth_utils, database

router = APIRouter(
    prefix="/connections",
    tags=["Connections"]
)

@router.post("/request/{n_user_id}", response_model=schemas.Connection)
def send_request(
    n_user_id: int,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    if n_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot connect with yourself")
    return crud.create_connection_request(db, current_user.id, n_user_id)

@router.get("/", response_model=List[schemas.Connection])
def list_connections(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    return crud.get_connections(db, current_user.id)

@router.get("/requests", response_model=List[schemas.Connection])
def list_received_requests(
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    return crud.get_pending_requests(db, current_user.id)

@router.put("/accept/{connection_id}", response_model=schemas.Connection)
def accept_request(
    connection_id: int,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Verify ownership
    conn = db.query(models.Connection).get(connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    if conn.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud.update_connection_status(db, connection_id, models.ConnectionStatus.accepted)

@router.put("/reject/{connection_id}", response_model=schemas.Connection)
def reject_request(
    connection_id: int,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    conn = db.query(models.Connection).get(connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    if conn.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return crud.update_connection_status(db, connection_id, models.ConnectionStatus.rejected)
