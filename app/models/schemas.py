from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List




class PlayerBase(BaseModel):
    id: int
    first_name: str
    last_name: str
    league_average: Optional[float] = None

    class Config:
        from_attributes = True

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    id: int
    name: str
    players: List[PlayerBase]

    class Config:
        from_attributes = True

class TeamCreate(TeamBase):
    players: List[PlayerCreate]

class Team(TeamBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

class TeamBasic(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class ScoreBase(BaseModel):
    team_id: int
    hole_number: int
    strokes: int
    date_played: datetime

class ScoreCreate(ScoreBase):
    pass

class Score(ScoreBase):
    id: int
    
    class Config:
        from_attributes = True

class HoleBase(BaseModel):
    number: int = Field(ge=1, le=18)
    par: int = Field(ge=3, le=5)
    handicap: int = Field(ge=1, le=18)

class CourseBase(BaseModel):
    name: str
    holes: List[HoleBase]

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CourseUpdate(BaseModel):
    name: str
    holes: List[HoleBase]

    class Config:
        from_attributes = True


class LeagueBase(BaseModel):
    name: str
    course_id: int
    number_of_weeks: int = Field(ge=1, le=15)
    start_date: date

class LeagueCreate(LeagueBase):
    team_ids: List[int]

class League(LeagueBase):
    id: int
    created_at: datetime
    teams: List[Team]
    
    class Config:
        from_attributes = True

class LeagueUpdate(BaseModel):
    name: str
    course_id: int
    number_of_weeks: int
    start_date: datetime
    team_ids: List[int]

    class Config:
        from_attributes = True


class MatchCreate(BaseModel):
    week_number: int
    team1_id: int
    team2_id: int
    date: date

class MatchResponse(BaseModel):
    id: int
    league_id: int
    week_number: int
    team1_id: int
    team2_id: int
    date: date

    class Config:
        from_attributes = True

class BatchMatchResponse(BaseModel):
    id: int
    league_id: int
    week_number: int
    team1_id: int
    team2_id: int
    date: date

    class Config:
        from_attributes = True

class LeagueDetails(BaseModel):
    id: int
    name: str
    course_id: int
    number_of_weeks: int
    start_date: date
    team_ids: List[int]
    teams: List[TeamBasic]

    class Config:
        from_attributes = True

class PlayerDetail(BaseModel):
    id: int
    first_name: str
    last_name: str
    handicap: int | None = None

    class Config:
        from_attributes = True

class TeamDetail(BaseModel):
    id: int
    name: str
    players: List[PlayerDetail]

    class Config:
        from_attributes = True

class MatchDetail(BaseModel):
    id: int
    league_id: int
    week_number: int
    team1_id: int
    team2_id: int
    date: datetime
    team1: TeamBase
    team2: TeamBase

    class Config:
        from_attributes = True

class HoleScoreBase(BaseModel):
    hole_id: int
    strokes: int

class HoleScoreCreate(HoleScoreBase):
    pass

class HoleScore(HoleScoreBase):
    id: int
    player_score_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PlayerScoreBase(BaseModel):
    player_id: int
    match_id: int
    hole_scores: List[HoleScoreBase]

class PlayerScoreCreate(PlayerScoreBase):
    pass

class PlayerScore(PlayerScoreBase):
    id: int
    created_at: datetime
    hole_scores: List[HoleScore]

    class Config:
        from_attributes = True