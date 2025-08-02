from pydantic import BaseModel
from typing import List, Optional

class HeroRole(BaseModel):
    role1: str
    role2: Optional[str]
    role3: Optional[str]

class Hero(BaseModel):
    id: int
    heroName: str
    heroAttribute: str
    heroAttackType: str
    heroDifficulty: str
    heroRole: HeroRole

    class Config:
        from_attributes = True # <-- PERUBAHAN DI SINI
        
class HeroList(BaseModel):
    status: str
    heroes: List[Hero]