from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class MessageResponse(BaseModel):

    username: str

    content: str

    class Config:
        orm_mode = True