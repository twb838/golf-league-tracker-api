from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    players = relationship("Player", back_populates="team")
    leagues = relationship("League", secondary="league_teams", back_populates="teams")
    home_matches = relationship("Match", foreign_keys="[Match.team1_id]", back_populates="team1")
    away_matches = relationship("Match", foreign_keys="[Match.team2_id]", back_populates="team2")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    team_id = Column(Integer, ForeignKey("teams.id"))
    league_average = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team", back_populates="players")
    scores = relationship("PlayerScore", back_populates="player")