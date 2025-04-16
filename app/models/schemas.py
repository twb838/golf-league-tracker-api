from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List




class PlayerBase(BaseModel):
    id: Optional[int] = None
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
    id: Optional[int] = None
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
    id: int
    number: int
    par: int
    handicap: int

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    id: int
    name: str
    holes: List[HoleBase]

    class Config:
        from_attributes = True

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
    id: int
    name: str
    course_id: int
    start_date: date
    number_of_weeks: int  # This will now be computed

    class Config:
        from_attributes = True

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

class BatchMatchRequest(BaseModel):
    matches: List[MatchCreate]

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
    league: LeagueBase
    course_id: int  # Added course_id

    class Config:
        from_attributes = True

class HoleScoreBase(BaseModel):
    hole_id: int
    strokes: int

class PlayerScoreBase(BaseModel):
    hole_scores: List[HoleScoreBase]

class DeleteWeekResponse(BaseModel):
    message: str
    deleted_count: int
    week_number: int
    league_id: int

    class Config:
        from_attributes = True

class DeleteMatchResponse(BaseModel):
    message: str
    match_id: int
    league_id: int
    week_number: int

    class Config:
        from_attributes = True

class WeekMatchCreate(BaseModel):
    date: datetime

    class Config:
        from_attributes = True

class HoleScore(BaseModel):
    hole_id: int
    strokes: int

class PlayerScore(BaseModel):
    player_id: int
    scores: List[HoleScore]

class MatchScores(BaseModel):
    match_id: int
    player_scores: List[PlayerScore]

class HoleScoreCreate(BaseModel):
    hole_id: int
    strokes: int

class PlayerScoreCreate(BaseModel):
    player_id: int
    scores: List[HoleScoreCreate]

    class Config:
        from_attributes = True

class HoleScoreResponse(BaseModel):
    id: int
    hole_id: int
    strokes: int
    created_at: datetime

    class Config:
        from_attributes = True

class PlayerScoreResponse(BaseModel):
    id: int
    player_id: int
    match_id: int
    hole_scores: List[HoleScoreResponse]  # Changed from scores to hole_scores to match model
    created_at: datetime

    class Config:
        from_attributes = True

class MatchScoreResponse(BaseModel):
    status: str
    message: str
    match_id: int
    scores: List[PlayerScoreResponse]

    class Config:
        from_attributes = True