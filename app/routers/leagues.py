from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models import schemas
from ..models.schemas import LeagueCreate, MatchResponse, MatchCreate
from app.models.base.models import *

router = APIRouter()

@router.post("/leagues/", response_model=schemas.League)
async def create_league(league: LeagueCreate, db: Session = Depends(get_db)):
    # Validate team count
    if len(league.team_ids) < 2 or len(league.team_ids) > 30:
        raise HTTPException(status_code=400, detail="Team count must be between 2 and 30")
    if len(league.team_ids) % 2 != 0:
        raise HTTPException(status_code=400, detail="Must have an even number of teams")

    db_league = League(
        name=league.name,
        course_id=league.course_id,
        number_of_weeks=league.number_of_weeks,
        start_date=league.start_date
    )
    db.add(db_league)
    
    try:
        db.flush()
        # Add teams to league
        for team_id in league.team_ids:
            league_team = LeagueTeam(league_id=db_league.id, team_id=team_id)
            db.add(league_team)
        
        db.commit()
        db.refresh(db_league)
        return db_league
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/leagues/", response_model=List[schemas.League])
async def get_leagues(db: Session = Depends(get_db)):
    try:
        leagues = db.query(League).all()
        return leagues
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leagues/{league_id}", response_model=schemas.League)
async def get_league(league_id: int, db: Session = Depends(get_db)):
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league

@router.delete("/leagues/{league_id}")
async def delete_league(league_id: int, db: Session = Depends(get_db)):
    # Check if league exists
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    try:
        # Delete league teams first (due to foreign key constraint)
        db.query(LeagueTeam).filter(LeagueTeam.league_id == league_id).delete()
        
        # Delete the league
        db.delete(league)
        db.commit()
        
        return {"message": f"League '{league.name}' successfully deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/leagues/{league_id}", response_model=schemas.League)
async def update_league(league_id: int, league_update: schemas.LeagueUpdate, db: Session = Depends(get_db)):
    # Check if league exists
    db_league = db.query(League).filter(League.id == league_id).first()
    if not db_league:
        raise HTTPException(status_code=404, detail="League not found")

    # Validate team count
    if len(league_update.team_ids) < 2 or len(league_update.team_ids) > 30:
        raise HTTPException(status_code=400, detail="Team count must be between 2 and 30")
    if len(league_update.team_ids) % 2 != 0:
        raise HTTPException(status_code=400, detail="Must have an even number of teams")

    try:
        # Update league details
        db.query(League).filter(League.id == league_id).update({
            League.name: league_update.name,
            League.course_id: league_update.course_id,
            League.number_of_weeks: league_update.number_of_weeks,
            League.start_date: league_update.start_date
        })

        # Remove existing team associations
        db.query(LeagueTeam).filter(LeagueTeam.league_id == league_id).delete()

        # Add updated team associations
        for team_id in league_update.team_ids:
            league_team = LeagueTeam(league_id=league_id, team_id=team_id)
            db.add(league_team)

        db.commit()
        db.refresh(db_league)
        return db_league

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/leagues/{league_id}", response_model=schemas.LeagueDetails)
async def get_league_details(league_id: int, db: Session = Depends(get_db)):
    # Load league with joined team data
    league = db.query(League).options(
        joinedload(League.teams)
    ).filter(League.id == league_id).first()
    
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Get all teams associated with this league
    teams = db.query(Team).join(LeagueTeam).filter(LeagueTeam.league_id == league_id).all()
    
    return {
        "id": league.id,
        "name": league.name,
        "course_id": league.course_id,
        "number_of_weeks": league.number_of_weeks,
        "start_date": league.start_date,
        "team_ids": [team.id for team in teams],
        "teams": teams
    }

@router.get("/leagues/{league_id}/matches", response_model=List[MatchResponse])
async def get_league_matches(league_id: int, db: Session = Depends(get_db)):
    matches = db.query(Match).filter(Match.league_id == league_id).all()
    return matches

@router.post("/leagues/{league_id}/matches", response_model=MatchResponse)
async def create_match(
    league_id: int, 
    match: MatchCreate, 
    db: Session = Depends(get_db)
):
    # Verify league exists
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    # Check if week number is valid
    existing_match = db.query(Match).filter(
        Match.league_id == league_id,
        Match.week_number == match.week_number
    ).first()
    
    if existing_match:
        raise HTTPException(
            status_code=400, 
            detail=f"Matches already exist for week {match.week_number}"
        )

    # Create new match
    db_match = Match(
        league_id=league_id,
        week_number=match.week_number,
        team1_id=match.team1_id,
        team2_id=match.team2_id,
        date=match.date
    )
    
    try:
        db.add(db_match)
        db.commit()
        db.refresh(db_match)
        return db_match
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/leagues/{league_id}/matches/batch", response_model=List[schemas.BatchMatchResponse])
async def create_matches(
    league_id: int,
    request: dict,
    db: Session = Depends(get_db)
):
    matches = request.get("matches", [])
    created_matches = []

    try:
        for match_data in matches:
            db_match = Match(
                league_id=league_id,
                week_number=match_data["week_number"],
                team1_id=match_data["team1_id"],
                team2_id=match_data["team2_id"],
                date=match_data["date"]
            )
            db.add(db_match)
            created_matches.append(db_match)
        
        db.commit()
        for match in created_matches:
            db.refresh(match)
        
        return created_matches
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
