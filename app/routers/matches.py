from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models import schemas
from ..models.schemas import MatchDetail, PlayerScore
from app.models.base.models import *

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/{match_id}", response_model=MatchDetail)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    """Get match details including teams and players"""
    match = db.query(Match)\
        .options(
            joinedload(Match.league).joinedload(League.course),
            joinedload(Match.team1).joinedload(Team.players),
            joinedload(Match.team2).joinedload(Team.players)
        )\
        .filter(Match.id == match_id)\
        .first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    return match

@router.post("/{match_id}/scores", response_model=List[schemas.PlayerScore])
async def submit_scores(
    match_id: int, 
    scores: List[schemas.PlayerScoreCreate],
    db: Session = Depends(get_db)
):
    """Submit scores for a match"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    created_scores = []
    try:
        for score_data in scores:
            # Create player score
            player_score = PlayerScore(
                match_id=match_id,
                player_id=score_data.player_id
            )
            db.add(player_score)
            db.flush()  # Get the ID

            # Create hole scores
            for hole_score in score_data.hole_scores:
                db_hole_score = HoleScore(
                    player_score_id=player_score.id,
                    hole_id=hole_score.hole_id,
                    strokes=hole_score.strokes
                )
                db.add(db_hole_score)
            
            created_scores.append(player_score)

        db.commit()
        
        # Refresh to get all relationships
        for score in created_scores:
            db.refresh(score)
        
        return created_scores
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))