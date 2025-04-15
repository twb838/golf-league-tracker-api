from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import schemas
from ..models.base.models import PlayerScore, HoleScore, Match, Player

router = APIRouter(prefix="/scores", tags=["scores"])

