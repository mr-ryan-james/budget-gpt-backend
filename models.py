from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from sample_data import *
import json
import uuid
from bson import ObjectId
from PyObjectId import PyObjectId
import random


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

    @property
    def wellness_sample_range(self):
        if self == Persona.BOB:
            return (0.2, 0.5)
        elif self == Persona.ANNA:
            return (0.4, 0.7)
        elif self == Persona.JEN:
            return (0.6, 1.0)


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

    @staticmethod
    def random_emotion_list():
        emotions = []
        num_entries = random.randint(1, 5)
        i = 0
        while i < num_entries:
            emotion = random.choice(list(Emotion))
            if emotion not in emotions:
                emotions.append(emotion)
                i += 1
        return emotions


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

    def data_points_prompt(self) -> str:
        return f"""
        Use the following data points.
        Data point 1 - financial wellness score. This is a score from 1 to 10 where 1 is poor and 10 is excellent. This user has a score of {self.wellness_score}
        Data point 2 - user's name: {self.name}
        Data point 3 - average montly income: {self.monthly_income}
        Data point 4 - average monthly expense on food: {self.monthly_expense_food}
        Data point 5 - average monthly expense on rent: {self.monthly_expense_rent}
        Data point 6 - average monthly expense on transportation: {self.monthly_expense_transportation}
        Data point 7 - average monthly expense on insurance: {self.monthly_expense_insurance}
        Data point 8 - average monthly expense on other categories: {self.monthly_expense_other}
        """


class WellnessUpdate(BaseModel):
    wellness_score: Optional[float]
    explanation: Optional[str]


class FinancialRecommendations(BaseModel):
    spending_and_saving: Optional[str]
    money_feelings: Optional[str]
    opportunities: Optional[str]


class EmotionsHistoryEntry(BaseModel):
    date: str
    emotions: list[Emotion]
    user_id: str

    def dict(self, *args, **kwargs):
        dict = super().dict(*args, **kwargs)
        dict['emotions'] = [c.value for c in dict['emotions']]
        return dict


class WellnessHistoryEntry(BaseModel):
    date: str
    wellness_score: float
    user_id: str
