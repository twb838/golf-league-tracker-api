from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models import schemas
from ..models.base.models import Match, League, Team, PlayerScore, HoleScore, Course

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/{match_id}", response_model=schemas.MatchDetail)
async def get_match(match_id: int, db: Session = Depends(get_db)):
    """Get match details including teams and players"""
    try:
        # Load match with all relationships
        match = db.query(Match)\
            .options(
                joinedload(Match.league),
                joinedload(Match.team1).joinedload(Team.players),
                joinedload(Match.team2).joinedload(Team.players)
            )\
            .filter(Match.id == match_id)\
            .first()
        
        if not match:
            raise HTTPException(
                status_code=404, 
                detail=f"Match with id {match_id} not found"
            )

        if not match.league:
            raise HTTPException(
                status_code=404, 
                detail=f"No league found for match {match_id}"
            )
            
        if not match.league.course_id:
            raise HTTPException(
                status_code=404, 
                detail=f"No course assigned to league {match.league.id}"
            )

        # Add course_id to the response
        match.course_id = match.league.course_id
        
        return match
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch match details: {str(e)}"
        )

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

@router.delete("/{match_id}", response_model=schemas.DeleteMatchResponse)
async def delete_match(match_id: int, db: Session = Depends(get_db)):
    """Delete a match and all associated scores"""
    try:
        # Check if match exists
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(
                status_code=404,
                detail=f"Match with id {match_id} not found"
            )

        # Get all player scores for this match
        player_scores = db.query(PlayerScore).filter(
            PlayerScore.match_id == match_id
        ).all()

        # Delete hole scores first (child records)
        for score in player_scores:
            db.query(HoleScore).filter(
                HoleScore.player_score_id == score.id
            ).delete()

        # Delete player scores
        db.query(PlayerScore).filter(
            PlayerScore.match_id == match_id
        ).delete()

        # Delete the match
        db.delete(match)
        db.commit()

        return {
            "message": f"Successfully deleted match {match_id}",
            "match_id": match_id,
            "league_id": match.league_id,
            "week_number": match.week_number
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete match: {str(e)}"
        )