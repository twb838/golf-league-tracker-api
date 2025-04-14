from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    course_id = Column(Integer, ForeignKey("courses.id"))
    number_of_weeks = Column(Integer)
    start_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teams = relationship("Team", secondary="league_teams", back_populates="leagues")
    course = relationship("Course", back_populates="leagues")
    matches = relationship("Match", back_populates="league")

class LeagueTeam(Base):
    __tablename__ = "league_teams"

    league_id = Column(Integer, ForeignKey("leagues.id"), primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)