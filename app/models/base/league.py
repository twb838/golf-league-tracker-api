from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship, object_session
from . import Base

class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    course_id = Column(Integer, ForeignKey("courses.id"))
    start_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teams = relationship("Team", secondary="league_teams", back_populates="leagues")
    course = relationship("Course", back_populates="leagues")
    matches = relationship("Match", back_populates="league")

    @property
    def number_of_weeks(self):
        """Dynamically calculate number of weeks based on matches"""
        if self.id is None:
            return 0
        session = object_session(self)
        if session:
            from .match import Match
            return session.query(func.max(Match.week_number))\
                .filter(Match.league_id == self.id)\
                .scalar() or 0
        return 0

class LeagueTeam(Base):
    __tablename__ = "league_teams"

    league_id = Column(Integer, ForeignKey("leagues.id"), primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)