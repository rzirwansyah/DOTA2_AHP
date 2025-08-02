from pydantic import BaseModel, Field
from typing import List, Optional

class SubCriteriaSchema(BaseModel):
    id: int
    code: str
    description: str
    paraphrase: str
    narration: str

    class Config:
        orm_mode = True

class CriteriaSchema(BaseModel):
    id: int
    code: str
    description: str
    paraphrase: str
    narration: str
    sub_criterias: List[SubCriteriaSchema] = []

    class Config:
        orm_mode = True

class ModelSchema(BaseModel):
    id: int
    code: str
    description: str
    paraphrase: str
    narration: str
    criterias: List[CriteriaSchema] = []

    class Config:
        orm_mode = True

class CriteriaResponse(BaseModel):
    status: str
    model: ModelSchema