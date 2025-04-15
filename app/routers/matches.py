from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models import schemas
from ..models.schemas import PlayerScoreCreate
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

@router.post("/{match_id}/scores", response_model=schemas.MatchScoreResponse)
async def submit_match_scores(
    match_id: int,
    player_scores: List[schemas.PlayerScoreCreate],
    db: Session = Depends(get_db)
):
    """Submit or update scores for a match"""
    try:
        # Verify match exists
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")

        created_scores = []
        for player_score in player_scores:
            # Upsert player score with relationship loading
            db_player_score = db.query(PlayerScore).filter(
                PlayerScore.match_id == match_id,
                PlayerScore.player_id == player_score.player_id
            ).first()

            if not db_player_score:
                db_player_score = PlayerScore(
                    match_id=match_id,
                    player_id=player_score.player_id
                )
                db.add(db_player_score)
                db.flush()

            # Upsert hole scores
            for hole_score in player_score.scores:
                db.merge(HoleScore(
                    player_score_id=db_player_score.id,
                    hole_id=hole_score.hole_id,
                    strokes=hole_score.strokes
                ))
            
            created_scores.append(db_player_score)

        # Update match status
        match.status = "completed"
        db.commit()

        # Refresh all scores with relationships loaded
        refreshed_scores = db.query(PlayerScore)\
            .options(joinedload(PlayerScore.hole_scores))\
            .filter(PlayerScore.id.in_([score.id for score in created_scores]))\
            .all()

        return {
            "status": "success",
            "message": "Scores submitted successfully",
            "match_id": match_id,
            "scores": refreshed_scores
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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