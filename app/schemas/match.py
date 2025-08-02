from pydantic import BaseModel
from datetime import date
from typing import List, Dict, Any
from app.models.models import GameModeEnum, ResultBattleEnum

class MatchCreate(BaseModel):
    matchName: str
    matchDate: date
    matchMode: GameModeEnum
    allyTeam: str
    allies: List[int]
    enemyTeam: str
    enemies: List[int]

class MatchResponse(BaseModel):
    status: str
    matchId: int

class ResultCreate(BaseModel):
    matchId: int
    heroId: int
    result: ResultBattleEnum

class HistoryHero(BaseModel):
    heroName: str
    heroAttribute: str

class MatchHistory(BaseModel):
    matchId: int
    matchDate: date
    matchName: str
    matchMode: GameModeEnum
    allyTeam: str
    allies: List[HistoryHero]
    enemyTeam: str
    enemies: List[HistoryHero]
    yourHero: HistoryHero
    matchResult: ResultBattleEnum

class HistoryResponse(BaseModel):
    status: str
    matches: List[MatchHistory]