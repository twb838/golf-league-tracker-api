from fastapi import APIRouter, HTTPException
from typing import List
from ..database import db
from datetime import datetime
from app.models.base.models import *

router = APIRouter(prefix="/scores", tags=["scores"])

