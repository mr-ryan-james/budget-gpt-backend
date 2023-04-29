from typing import Optional
from pydantic import BaseModel, Field


class PurchaseIntent(BaseModel):
    user_question: str


class PurchaseDecision(BaseModel):
    decision: bool
    explanation: str


class User(BaseModel):
    name: str
    wellness_score: float
