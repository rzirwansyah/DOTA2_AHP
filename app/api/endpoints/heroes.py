from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.models import models
from app.schemas import hero as hero_schema

router = APIRouter()

@router.get("", response_model=hero_schema.HeroList, summary="Mendapatkan referensi semua hero")
def get_all_heroes(
    db: Session = Depends(deps.get_db),
    current_user: models.Users = Depends(deps.get_current_user)
):
    """
    Mengambil daftar semua hero Dota 2 yang ada di database.
    """
    db_heroes = db.query(models.Heroes).order_by(models.Heroes.name).all()
    
    heroes_list = []
    for h in db_heroes:
        heroes_list.append(
            hero_schema.Hero(
                id=h.id,
                heroName=h.name,
                heroAttribute=h.attribute,
                heroAttackType=h.attack_type,
                heroDifficulty=h.difficulty,
                heroRole=hero_schema.HeroRole(role1=h.role1, role2=h.role2, role3=h.role3)
            )
        )

    return {"status": "success", "heroes": heroes_list}