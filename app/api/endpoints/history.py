from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.api import deps
from app.models import models
from app.schemas import match as match_schema
from app.schemas.recommendation import StatusResponse

router = APIRouter()

@router.post("/result", response_model=StatusResponse, summary="Mengirimkan hasil pertandingan")
def submit_result(
    *,
    db: Session = Depends(deps.get_db),
    result_in: match_schema.ResultCreate,
    current_user: models.Users = Depends(deps.get_current_user)
):
    """
    Merekam hasil pertandingan setelah user bermain.
    """
    # Verifikasi bahwa match ini milik user yang sedang login
    match = db.query(models.Matches).filter(models.Matches.id == result_in.matchId, models.Matches.user_id == current_user.id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found or does not belong to user")

    db_history = models.Histories(
        match_id=result_in.matchId,
        hero_id=result_in.heroId,
        match_result=result_in.result.value
    )
    db.add(db_history)
    db.commit()
    
    return {"status": "success"}


@router.get("/history", response_model=match_schema.HistoryResponse, summary="Melihat riwayat pertandingan")
def get_history(
    db: Session = Depends(deps.get_db),
    current_user: models.Users = Depends(deps.get_current_user)
):
    """
    Mengambil semua riwayat pertandingan milik user.
    """
    histories = db.query(models.Histories)\
        .join(models.Matches)\
        .filter(models.Matches.user_id == current_user.id)\
        .order_by(desc(models.Matches.match_date))\
        .all()

    response_matches = []
    for hist in histories:
        match = hist.match
        your_hero_db = hist.hero
        
        # Ambil detail hero tim kawan
        ally_ids = match.allies.get('members', [])
        allies_db = db.query(models.Heroes).filter(models.Heroes.id.in_(ally_ids)).all()
        allies_map = {h.id: h for h in allies_db}
        
        # Ambil detail hero tim lawan
        enemy_ids = match.enemies.get('members', [])
        enemies_db = db.query(models.Heroes).filter(models.Heroes.id.in_(enemy_ids)).all()
        enemies_map = {h.id: h for h in enemies_db}
        
        response_matches.append(
            match_schema.MatchHistory(
                matchId=match.id,
                matchDate=match.match_date,
                matchName=match.match_name,
                matchMode=match.match_mode,
                allyTeam=match.ally_team,
                allies=[match_schema.HistoryHero(heroName=allies_map[id].name, heroAttribute=allies_map[id].attribute) for id in ally_ids if id in allies_map],
                enemyTeam=match.enemy_team,
                enemies=[match_schema.HistoryHero(heroName=enemies_map[id].name, heroAttribute=enemies_map[id].attribute) for id in enemy_ids if id in enemies_map],
                yourHero=match_schema.HistoryHero(heroName=your_hero_db.name, heroAttribute=your_hero_db.attribute),
                matchResult=hist.match_result
            )
        )

    return {"status": "success", "matches": response_matches}