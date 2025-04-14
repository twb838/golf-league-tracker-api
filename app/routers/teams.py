from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import schemas
from app.models.base.models import *

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=schemas.Team)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    # Create team first
    db_team = Team(name=team.name)
    db.add(db_team)
    db.flush()  # This gets us the team.id without committing
    
    # Create players dynamically
    for player_data in team.players:
        player = Player(
            first_name=player_data.first_name,
            last_name=player_data.last_name,
            league_average=player_data.league_average,
            team_id=db_team.id
        )
        db.add(player)
    
    try:
        db.commit()
        db.refresh(db_team)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return db_team

@router.get("/", response_model=List[schemas.Team])
def get_teams(db: Session = Depends(get_db)):
    return db.query(Team).all()

@router.get("/{team_id}")
async def get_team_details(team_id: int, db: Session = Depends(get_db)):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    db_team.players = db.query(Player).filter(Player.team_id == team_id).all()
    return db_team

@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db)):
    # First check if team exists
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if db_team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    
    try:
        # Delete associated players first
        db.query(Player).filter(Player.team_id == team_id).delete()
        # Then delete the team
        db.delete(db_team)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Team and associated players deleted successfully"}

@router.delete("/cleanup/unassigned-players")
def delete_unassigned_players(db: Session = Depends(get_db)):
    try:
        # Delete all players where team_id is NULL
        result = db.query(Player).filter(
            Player.team_id == None
        ).delete()
        
        db.commit()
        
        if result == 0:
            return {"message": "No unassigned players found"}
        
        return {
            "message": f"Successfully deleted {result} unassigned players"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error deleting unassigned players: {str(e)}"
        )