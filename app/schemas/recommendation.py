from pydantic import BaseModel, Field, conlist
from typing import List, Dict

# --- Preferences Schemas ---
class SubCriteriaPreferences(BaseModel):
    playerArchetype: List[int]
    generalPlaystyle: List[int]
    roleSpecificPlaystyle: List[int]
    teamCompositionBalance: List[int]
    heroSynergyCombos: List[int]
    directHeroCounters: List[int]
    exploitingLineupWeaknesses: List[int]
    identifyingKeyThreats: List[int]

class PreferencesBody(BaseModel):
    criteria: List[int]
    subCriteria: SubCriteriaPreferences

class PreferencesCreate(BaseModel):
    matchId: int
    preferences: PreferencesBody

# --- Alternatives Schemas ---
class AlternativeScores(BaseModel):
    # Menggunakan Field alias untuk mencocokkan nama JSON dengan nama variabel Python
    PA_HC: int = Field(..., alias='PA-HC')
    PA_M: int = Field(..., alias='PA-M')
    PA_O: int = Field(..., alias='PA-O')
    PA_SS: int = Field(..., alias='PA-SS')
    PA_HS: int = Field(..., alias='PA-HS')
    GP_A: int = Field(..., alias='GP-A')
    GP_FD: int = Field(..., alias='GP-FD')
    GP_PST: int = Field(..., alias='GP-PST')
    GP_ED: int = Field(..., alias='GP-ED')
    RSP_IS: int = Field(..., alias='RSP-IS')
    RSP_TC: int = Field(..., alias='RSP-TC')
    RSP_MPS: int = Field(..., alias='RSP-MPS')
    RSP_GL: int = Field(..., alias='RSP-GL')
    RSP_SA: int = Field(..., alias='RSP-SA')
    RSP_VC: int = Field(..., alias='RSP-VC')
    TCB_DTM: int = Field(..., alias='TCB-DTM')
    TCB_RF: int = Field(..., alias='TCB-RF')
    TCB_PP: int = Field(..., alias='TCB-PP')
    TCB_TC: int = Field(..., alias='TCB-TC')
    HSC_AC: int = Field(..., alias='HSC-AC')
    HSC_LS: int = Field(..., alias='HSC-LS')
    HSC_ABS: int = Field(..., alias='HSC-ABS')
    DHC_AC: int = Field(..., alias='DHC-AC')
    DHC_PC: int = Field(..., alias='DHC-PC')
    DHC_IC: int = Field(..., alias='DHC-IC')
    ELW_LC: int = Field(..., alias='ELW-LC')
    ELW_GC: int = Field(..., alias='ELW-GC')
    ELW_SDT: int = Field(..., alias='ELW-SDT')
    ELW_WPP: int = Field(..., alias='ELW-WPP')
    IKT_TWC: int = Field(..., alias='IKT-TWC')
    IKT_TPI: int = Field(..., alias='IKT-TPI')
    IKT_TTS: int = Field(..., alias='IKT-TTS')

class HeroAlternative(BaseModel):
    heroId: int
    alternative: AlternativeScores

class AlternativesCreate(BaseModel):
    matchId: int
    heroes: List[HeroAlternative] = Field(..., min_items=5, max_items=5)

# --- Recommendation Response Schemas ---
class RecommendationHero(BaseModel):
    heroId: int
    heroName: str
    finalScore: float

class RecommendationResponse(BaseModel):
    status: str
    recommendations: List[RecommendationHero]

class StatusResponse(BaseModel):
    status: str