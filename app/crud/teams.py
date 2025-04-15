import logging
from sqlalchemy.orm import Session

from app.models.base.models import Team, Player
from app.models import schemas


def create_team(db: Session, team: schemas.TeamCreate):
    logging.info("Creating team: %s", team.name)
    db_team = Team(name=team.name)
    db.add(db_team)
    db.flush()

    for player_data in team.players:
        player = Player(
            first_name=player_data.first_name,
            last_name=player_data.last_name,
            league_average=player_data.league_average,
            team_id=db_team.id
        )
        db.add(player)

    db.commit()
    db.refresh(db_team)
    return db_team


def get_teams(db: Session):
    logging.info("Fetching all teams")
    return db.query(Team).all()


def get_team(db: Session, team_id: int):
    logging.info("Fetching team with id: %s", team_id)
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if db_team:
        db_team.players = db.query(Player).filter(Player.team_id == team_id).all()
    return db_team


def delete_team(db: Session, team_id: int):
    logging.info("Deleting team with id: %s", team_id)
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        logging.warning("Team with id %s not found", team_id)
        return None

    db.query(Player).filter(Player.team_id == team_id).delete()
    db.delete(db_team)
    db.commit()
    return db_team


def delete_unassigned_players(db: Session):
    logging.info("Deleting unassigned players")
    result = db.query(Player).filter(Player.team_id is None).delete()
    db.commit()
    return result
