from pydantic import BaseModel, Field
from typing import List, Optional

class SubCriteriaSchema(BaseModel):
    id: int
    code: str
    name: str
    description: str
    paraphrase: str
    narration: str

    class Config:
        from_attributes = True # <-- PERUBAHAN DI SINI

class CriteriaSchema(BaseModel):
    id: int
    code: str
    name: str
    description: str
    paraphrase: str
    narration: str
    sub_criterias: List[SubCriteriaSchema] = []

    class Config:
        from_attributes = True # <-- PERUBAHAN DI SINI

class ModelSchema(BaseModel):
    id: int
    code: str
    name: str
    description: str
    paraphrase: str
    narration: str
    criterias: List[CriteriaSchema] = []

    class Config:
        from_attributes = True # <-- PERUBAHAN DI SINI

class CriteriaResponse(BaseModel):
    status: str
    model: ModelSchema