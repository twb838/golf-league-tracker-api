from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    holes = relationship("Hole", back_populates="course")
    leagues = relationship("League", back_populates="course")

class Hole(Base):
    __tablename__ = "holes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    number = Column(Integer)
    par = Column(Integer)
    handicap = Column(Integer)
    
    course = relationship("Course", back_populates="holes")
    scores = relationship("HoleScore", back_populates="hole")