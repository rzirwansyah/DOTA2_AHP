from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models import models
from app.schemas import match as match_schema

router = APIRouter()

@router.post("", response_model=match_schema.MatchResponse, summary="Mengirimkan informasi pertandingan baru")
def create_match(
    *,
    db: Session = Depends(deps.get_db),
    match_in: match_schema.MatchCreate,
    current_user: models.Users = Depends(deps.get_current_user)
):
    """
    Membuat record pertandingan baru.
    """
    db_match = models.Matches(
        user_id=current_user.id,
        match_name=match_in.matchName,
        match_date=match_in.matchDate,
        match_mode=match_in.matchMode.value,
        ally_team=match_in.allyTeam,
        allies={"members": match_in.allies},
        enemy_team=match_in.enemyTeam,
        enemies={"members": match_in.enemies}
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    
    return {"status": "success", "matchId": db_match.id}