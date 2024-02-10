from sqlalchemy import Column, Integer, String, Date , ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class State(enum.Enum):
    START = "start"
    PROGRESS = "progress"
    FINISH = "finish"
    
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    image = Column(String)
    tasks = relationship('Task', cascade='all, delete, delete-orphan')

class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    create_date = Column(Date)
    finish_date = Column(Date)
    state = Column(Enum(State), default=State.START)
    category = Column(Integer, ForeignKey('category.id'))
    user = Column(Integer, ForeignKey('user.id'))

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String)