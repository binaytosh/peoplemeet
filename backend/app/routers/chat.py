from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from .. import schemas, models, crud, auth_utils, database
import json

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        # Map user_id to WebSocket list (user might have multiple devices/tabs)
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(database.get_db)):
    # Validate Token
    try:
        payload = auth_utils.jwt.decode(token, auth_utils.SECRET_KEY, algorithms=[auth_utils.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            await websocket.close(code=1008)
            return
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            # Expecting JSON: {"receiver_id": 123, "content": "Hello"}
            try:
                msg_data = json.loads(data)
                receiver_id = msg_data.get("receiver_id")
                content = msg_data.get("content")
                
                if receiver_id and content:
                    # Save to DB
                    msg = crud.create_message(db, user.id, receiver_id, content)
                    
                    # Notify Receiver
                    outgoing_msg = {
                        "id": msg.id,
                        "sender_id": user.id,
                        "receiver_id": receiver_id,
                        "content": content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    await manager.send_personal_message(outgoing_msg, receiver_id)
                    # Also echo back to sender (for multiple tabs sync)
                    await manager.send_personal_message(outgoing_msg, user.id)
                    
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)

@router.get("/history/{other_user_id}", response_model=List[schemas.Message])
def get_history(
    other_user_id: int,
    current_user: models.User = Depends(auth_utils.get_current_user),
    db: Session = Depends(database.get_db)
):
    return crud.get_chat_history(db, current_user.id, other_user_id)
