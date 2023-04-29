from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from sample_data import *
import json
import uuid
from bson import ObjectId
from PyObjectId import PyObjectId


class Persona(Enum):
    BOB = 'Bob'
    ANNA = 'Anna'
    JEN = 'Jen'

    @property
    def default_value(self):
        if self == Persona.BOB:
            return json.loads(preset_bob)
        elif self == Persona.ANNA:
            return json.loads(preset_anna)
        elif self == Persona.JEN:
            return json.loads(preset_jen)


class Emotion(Enum):
    ACCEPTANCE = 'acceptance'
    DISAPPOINTMENT = 'disappointment'
    BITTERNESS = 'bitterness'
    GRATITUDE = 'gratitude'
    CONFUSION = 'confusion'
    SERENITY = 'serenity'
    NERVOUSNESS = 'nervousness'
    SHAME = 'shame'
    TERROR = 'terror'
    EXCITEMENT = 'excitement'
    OPTIMISM = 'optimism'
    FRUSTATION = 'frustration'


class BalanceStatus(Enum):
    LOW_EXPENSES = 'low_expenses'
    MODERATE_EXPENSES = 'moderate_expenses'
    HIGH_EXPENSES = 'high_expenses'
    OVERSHOOTING_EXPENSES = 'overshooting_expenses'


class PurchaseIntent(BaseModel):
    user_question: str


class PurchaseDecision(BaseModel):
    decision: bool
    explanation: str


class EmotionsInput(BaseModel):
    emotions: list[Emotion]


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
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

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    def expenses(self) -> float:
        return self.monthly_expense_food + \
            self.monthly_expense_rent + \
            self.monthly_expense_education + \
            self.monthly_expense_transportation + \
            self.monthly_expense_insurance + \
            self.monthly_expense_other

    def balance_status(self) -> BalanceStatus:
        expenses = self.expenses()
        income = self.monthly_income
        ratio = expenses / income
        if ratio < 0.4:
            return BalanceStatus.LOW_EXPENSES
        elif ratio >= 0.4 and ratio < 0.8:
            return BalanceStatus.MODERATE_EXPENSES
        elif ratio >= 0.8 and ratio < 1.0:
            return BalanceStatus.HIGH_EXPENSES
        else:
            return BalanceStatus.OVERSHOOTING_EXPENSES


class WellnessUpdate(BaseModel):
    wellness_score: Optional[float]
    explanation: Optional[str]


class FinancialRecommendations(BaseModel):
    spending_and_saving: Optional[str]
    money_feelings: Optional[str]
    opportunities: Optional[str]
