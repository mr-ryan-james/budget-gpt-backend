from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from sample_data import *
import json


class Persona(Enum):
    BOB = 'bob'
    ANNA = 'anna'
    JEN = 'jen'

    @property
    def default_value(self):
        if self == Persona.BOB:
            return json.loads(preset_bob)
        elif self == Persona.ANNA:
            return json.loads(preset_anna)
        elif self == Persona.JEN:
            return json.loads(preset_jen)


class PurchaseIntent(BaseModel):
    user_question: str


class PurchaseDecision(BaseModel):
    decision: bool
    explanation: str


class User(BaseModel):
    name: str
    monthly_income: float
    monthly_expense_food: float
    monthly_expense_rent: float
    monthly_expense_education: float
    monthly_expense_transportation: float
    monthly_expense_insurance: float
    monthly_expense_other: float
    monthly_saving_target: float
    wellness_score: float
    risk_score: float
