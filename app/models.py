# app/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class SymptomInput(BaseModel):
    symptoms: str = Field(..., example="fever, sore throat, cough")
    age: Optional[int] = Field(None, example=25)
    sex: Optional[str] = Field(None, example="male")
    duration: Optional[str] = Field(None, example="3 days")

class Condition(BaseModel):
    name: str
    rank: int
    confidence: str
    rationale: Optional[str] = None

class SymptomResponse(BaseModel):
    conditions: List[Condition]
    recommendations: List[str]
    triage: str
    disclaimer: str
    notes: Optional[str] = None
