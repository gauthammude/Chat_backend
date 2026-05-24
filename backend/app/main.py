from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect
from .websocket import manager
import hashlib
from .auth import hash_password
from fastapi.middleware.cors import CORSMiddleware
from .websocket import manager
from .database import engine, SessionLocal
from . import models, schemas
from .database import SessionLocal

from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Chat App Backend Running"}

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_pw = hash_password(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_pw
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User created successfully"
    }


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    access_token = create_access_token(
        data={"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }


@app.websocket("/ws/chat/{username}")
async def websocket_chat(
    websocket: WebSocket,
    username: str
):

    await manager.connect(
        websocket,
        username
    )

    try:

        while True:

            data = await websocket.receive_json()

            if "type" not in data:
                continue

            # Typing Event
            if data["type"] == "typing":

                await manager.broadcast({
                    "type": "typing",
                    "username": data["username"]
                })

            # Message Event
            elif data["type"] == "message":

                db = SessionLocal()

                db_user = db.query(
                    models.User
                ).filter(
                    models.User.username
                    == data["username"]
                ).first()

                if db_user:

                    new_message = models.Message(
                        username=data["username"],
                        content=data["message"],
                        user_id=db_user.id
                    )

                    db.add(new_message)

                    db.commit()

                await manager.broadcast({
                    "type": "message",
                    "username": data["username"],
                    "message": data["message"]
                })

                db.close()

    except WebSocketDisconnect:

        manager.disconnect(
            websocket,
            username
        )

        await manager.broadcast({
            "type": "users",
            "users": manager.online_users
        })




@app.get("/messages")
def get_messages(
    db: Session = Depends(get_db)
):

    messages = db.query(
        models.Message
    ).all()

    return messages