from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import schemas
from app.crud import teams as teams_crud

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=schemas.Team)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    try:
        return teams_crud.create_team(db, team)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/", response_model=List[schemas.Team])
def get_teams(db: Session = Depends(get_db)):
    return teams_crud.get_teams(db)

@router.get("/{team_id}")
async def get_team_details(team_id: int, db: Session = Depends(get_db)):
    db_team = teams_crud.get_team(db, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@router.delete("/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db)):
    try:
        result = teams_crud.delete_team(db, team_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Team not found")
        return {"message": "Team and associated players deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.delete("/cleanup/unassigned-players")
def delete_unassigned_players(db: Session = Depends(get_db)):
    try:
        result = teams_crud.delete_unassigned_players(db)

        if result == 0:
            return {"message": "No unassigned players found"}

        return {
            "message": f"Successfully deleted {result} unassigned players"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error deleting unassigned players: {str(e)}"
        ) from e
