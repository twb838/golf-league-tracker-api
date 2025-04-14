from fastapi import APIRouter, HTTPException
from typing import List
from ..models.schemas import Team
from ..database import db
from datetime import datetime
from app.models.base.models import *

router = APIRouter(prefix="/players", tags=["players"])
