from sqlalchemy import Column, Integer, String
from .database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True)

    email = Column(String, unique=True, index=True)

    password = Column(String)

class Message(Base):

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String)

    content = Column(String)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    user = relationship("User")