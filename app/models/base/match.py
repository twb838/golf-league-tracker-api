from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    week_number = Column(Integer)
    team1_id = Column(Integer, ForeignKey("teams.id"))
    team2_id = Column(Integer, ForeignKey("teams.id"))
    date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    league = relationship("League", back_populates="matches")
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="home_matches")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="away_matches")
    player_scores = relationship("PlayerScore", back_populates="match")

class PlayerScore(Base):
    __tablename__ = "player_scores"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="player_scores")
    player = relationship("Player", back_populates="scores")
    hole_scores = relationship("HoleScore", back_populates="player_score")

class HoleScore(Base):
    __tablename__ = "hole_scores"

    id = Column(Integer, primary_key=True, index=True)
    player_score_id = Column(Integer, ForeignKey("player_scores.id"))
    hole_id = Column(Integer, ForeignKey("holes.id"))
    strokes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    player_score = relationship("PlayerScore", back_populates="hole_scores")
    hole = relationship("Hole", back_populates="scores")